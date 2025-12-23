/**
 * Azure Content Understanding Client (Node.js)
 * Based on Azure Content Understanding REST API
 */

import fetch from 'node-fetch';
import fs from 'fs-extra';
import path from 'path';
import { logger } from './logger.js';

class AzureContentUnderstandingClient {
    constructor(config) {
        this.endpoint = config.endpoint.replace(/\/$/, ''); // Remove trailing slash
        this.apiVersion = config.apiVersion;
        this.subscriptionKey = config.subscriptionKey;
        this.aadToken = config.aadToken;
        this.analyzerId = config.analyzerId;
        this.timeoutSeconds = config.timeoutSeconds || 3600;
        this.pollingIntervalSeconds = config.pollingIntervalSeconds || 2;

        // Validate configuration
        if (!this.endpoint) {
            throw new Error('Endpoint must be provided');
        }
        if (!this.apiVersion) {
            throw new Error('API version must be provided');
        }
        if (!this.subscriptionKey && !this.aadToken) {
            throw new Error('Either subscription key or AAD token must be provided');
        }
        if (!this.analyzerId) {
            throw new Error('Analyzer ID must be provided');
        }

        // Set up headers
        this.headers = this._getHeaders();
        
        logger.info('Azure Content Understanding Client initialized', {
            endpoint: this.endpoint,
            apiVersion: this.apiVersion,
            analyzerId: this.analyzerId
        });
    }

    /**
     * Get HTTP headers for requests
     */
    _getHeaders() {
        const headers = {
            'x-ms-useragent': 'rct-content-understanding-client'
        };

        if (this.subscriptionKey) {
            headers['Ocp-Apim-Subscription-Key'] = this.subscriptionKey;
        } else if (this.aadToken) {
            headers['Authorization'] = `Bearer ${this.aadToken}`;
        }

        return headers;
    }

    /**
     * Begin analysis of a PDF file
     */
    async beginAnalyze(filePath) {
        try {
            logger.info(`Starting analysis for: ${path.basename(filePath)}`);

            // Check if file exists
            if (!await fs.pathExists(filePath)) {
                throw new Error(`File not found: ${filePath}`);
            }

            // Read file as buffer
            const fileBuffer = await fs.readFile(filePath);
            
            // Set headers for file upload
            const headers = {
                ...this.headers,
                'Content-Type': 'application/octet-stream'
            };

            // Construct URL
            const url = `${this.endpoint}/contentunderstanding/analyzers/${this.analyzerId}:analyze?api-version=${this.apiVersion}&stringEncoding=utf16`;

            logger.debug('Making POST request to begin analysis', { url });

            // Make request
            const response = await fetch(url, {
                method: 'POST',
                headers: headers,
                body: fileBuffer
            });

            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`Analysis request failed: ${response.status} ${response.statusText}\n${errorText}`);
            }

            // Get operation location from headers
            const operationLocation = response.headers.get('operation-location');
            if (!operationLocation) {
                throw new Error('Operation location not found in response headers');
            }

            logger.info('Analysis started successfully', {
                file: path.basename(filePath),
                operationLocation
            });

            return {
                operationLocation,
                response
            };

        } catch (error) {
            logger.error('Failed to begin analysis', error, { filePath });
            throw error;
        }
    }

    /**
     * Begin analysis from URL (alternative method)
     */
    async beginAnalyzeFromUrl(fileUrl) {
        try {
            logger.info(`Starting analysis for URL: ${fileUrl}`);

            const headers = {
                ...this.headers,
                'Content-Type': 'application/json'
            };

            const url = `${this.endpoint}/contentunderstanding/analyzers/${this.analyzerId}:analyze?api-version=${this.apiVersion}&stringEncoding=utf16`;

            const response = await fetch(url, {
                method: 'POST',
                headers: headers,
                body: JSON.stringify({ url: fileUrl })
            });

            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`Analysis request failed: ${response.status} ${response.statusText}\n${errorText}`);
            }

            const operationLocation = response.headers.get('operation-location');
            if (!operationLocation) {
                throw new Error('Operation location not found in response headers');
            }

            logger.info('Analysis started successfully', { fileUrl, operationLocation });

            return {
                operationLocation,
                response
            };

        } catch (error) {
            logger.error('Failed to begin analysis from URL', error, { fileUrl });
            throw error;
        }
    }

    /**
     * Poll for analysis results
     */
    async pollResult(operationLocation, filename = 'unknown') {
        try {
            const startTime = Date.now();
            let attemptCount = 0;

            logger.info('Starting to poll for results', {
                filename,
                timeoutSeconds: this.timeoutSeconds,
                pollingInterval: this.pollingIntervalSeconds
            });

            while (true) {
                attemptCount++;
                const elapsedTime = (Date.now() - startTime) / 1000;

                // Check timeout
                if (elapsedTime > this.timeoutSeconds) {
                    throw new Error(`Operation timed out after ${this.timeoutSeconds} seconds`);
                }

                // Make polling request
                const response = await fetch(operationLocation, {
                    method: 'GET',
                    headers: this.headers
                });

                if (!response.ok) {
                    const errorText = await response.text();
                    throw new Error(`Polling request failed: ${response.status} ${response.statusText}\n${errorText}`);
                }

                const result = await response.json();
                const status = result.status?.toLowerCase();

                logger.debug('Polling attempt', {
                    filename,
                    attempt: attemptCount,
                    status,
                    elapsed: `${elapsedTime.toFixed(2)}s`
                });

                if (status === 'succeeded') {
                    logger.info('Analysis completed successfully', {
                        filename,
                        elapsed: `${elapsedTime.toFixed(2)}s`,
                        attempts: attemptCount
                    });
                    return result;
                } else if (status === 'failed') {
                    logger.error('Analysis failed', null, {
                        filename,
                        result
                    });
                    throw new Error(`Analysis failed: ${JSON.stringify(result)}`);
                } else if (status === 'notstarted' || status === 'running') {
                    // Continue polling
                    const operationId = operationLocation.split('/').pop()?.split('?')[0];
                    logger.info(`Analysis in progress... (${operationId})`, {
                        filename,
                        elapsed: `${elapsedTime.toFixed(2)}s`
                    });
                } else {
                    logger.warn(`Unknown status: ${status}`, { filename, result });
                }

                // Wait before next poll
                await this._sleep(this.pollingIntervalSeconds * 1000);
            }

        } catch (error) {
            logger.error('Failed to poll results', error, { filename });
            throw error;
        }
    }

    /**
     * Analyze a PDF file and return results (convenience method)
     */
    async analyzeFile(filePath) {
        try {
            const filename = path.basename(filePath);
            
            // Begin analysis
            const { operationLocation } = await this.beginAnalyze(filePath);
            
            // Poll for results
            const result = await this.pollResult(operationLocation, filename);
            
            return result;

        } catch (error) {
            logger.error('Failed to analyze file', error, { filePath });
            throw error;
        }
    }

    /**
     * Extract fields from analysis result
     */
    extractFields(analysisResult) {
        try {
            // Azure Content Understanding returns: { result: { contents: [ { fields: {...} } ] } }
            if (!analysisResult || !analysisResult.result) {
                throw new Error('Invalid analysis result format: missing result object');
            }

            const result = analysisResult.result;
            const contents = result.contents || [];

            if (contents.length === 0) {
                logger.warn('No contents found in analysis result');
                return {};
            }

            // Get first content item (should be the only one for single PDF)
            const content = contents[0];
            const fields = content.fields || {};

            logger.info('Extracted fields', {
                totalFields: Object.keys(fields).length,
                analyzerId: result.analyzerId,
                hasMarkdown: !!content.markdown
            });

            return this._flattenFields(fields);

        } catch (error) {
            logger.error('Failed to extract fields', error);
            throw error;
        }
    }

    /**
     * Flatten nested fields structure
     */
    _flattenFields(fields) {
        const flattened = {};

        for (const [fieldName, fieldData] of Object.entries(fields)) {
            if (fieldData.type === 'object' && fieldData.valueObject) {
                // Nested object - flatten recursively
                const nested = this._flattenFields(fieldData.valueObject);
                for (const [nestedKey, nestedValue] of Object.entries(nested)) {
                    flattened[`${fieldName}.${nestedKey}`] = nestedValue;
                }
            } else if (fieldData.type === 'array' && fieldData.valueArray) {
                // Array - keep ALL items, not just first (important for multi-group studies)
                if (fieldData.valueArray.length > 0) {
                    const firstItem = fieldData.valueArray[0];
                    if (firstItem.type === 'object' && firstItem.valueObject) {
                        // This is an array of objects (like Age/Sex with multiple groups)
                        // Store the entire array so demographics extractor can process all groups
                        const arrayItems = [];
                        for (const item of fieldData.valueArray) {
                            if (item.type === 'object' && item.valueObject) {
                                const itemFlattened = {};
                                const nested = this._flattenFields(item.valueObject);
                                for (const [key, value] of Object.entries(nested)) {
                                    itemFlattened[key] = value.value; // Extract just the value
                                }
                                arrayItems.push(itemFlattened);
                            }
                        }
                        // Store as a special array field
                        flattened[fieldName] = {
                            value: arrayItems,
                            confidence: fieldData.confidence || 0,
                            type: 'array',
                            isMultiGroup: true
                        };
                    } else {
                        // Simple array - convert to JSON string
                        flattened[fieldName] = {
                            value: JSON.stringify(fieldData.valueArray),
                            confidence: fieldData.confidence || 0,
                            type: fieldData.type
                        };
                    }
                } else {
                    // Empty array - set empty value
                    flattened[fieldName] = {
                        value: '',
                        confidence: 0,
                        type: fieldData.type
                    };
                }
            } else {
                // Regular field - extract value and confidence
                flattened[fieldName] = {
                    value: this._extractFieldValue(fieldData),
                    confidence: fieldData.confidence || 0,
                    type: fieldData.type
                };
            }
        }

        return flattened;
    }

    /**
     * Extract value from field data based on type
     */
    _extractFieldValue(fieldData) {
        const type = fieldData.type;

        switch (type) {
            case 'string':
                return fieldData.valueString || fieldData.content || '';
            case 'number':
                return fieldData.valueNumber;
            case 'integer':
                return fieldData.valueInteger;
            case 'boolean':
                return fieldData.valueBoolean;
            case 'date':
                return fieldData.valueDate;
            case 'time':
                return fieldData.valueTime;
            case 'array':
                return fieldData.valueArray;
            case 'object':
                return fieldData.valueObject;
            default:
                return fieldData.content || '';
        }
    }

    /**
     * Sleep utility
     */
    _sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}

export { AzureContentUnderstandingClient };
export default AzureContentUnderstandingClient;


