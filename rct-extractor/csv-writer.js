/**
 * CSV Writer for Content Understanding Results
 * Dynamically uses analyzer schema for headers
 */

import { createObjectCsvWriter } from 'csv-writer';
import fs from 'fs-extra';
import path from 'path';
import { fileURLToPath } from 'url';
import { logger } from './logger.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

class CSVWriter {
    constructor() {
        this.outputFolder = path.resolve(__dirname, 'output');
        fs.ensureDirSync(this.outputFolder);
        this.schema = null;
        this.loadSchema();
    }

    /**
     * Load synced analyzer schema
     */
    loadSchema() {
        try {
            const schemaPath = path.join(__dirname, 'synced-analyzer-schema.json');
            if (fs.existsSync(schemaPath)) {
                this.schema = fs.readJsonSync(schemaPath);
                logger.info(`📋 Loaded analyzer schema with ${this.schema.totalFields} fields`);
            } else {
                logger.warn('Synced analyzer schema not found, using fallback headers');
            }
        } catch (error) {
            logger.error('Failed to load analyzer schema', error);
        }
    }

    /**
     * Generate timestamped filename
     */
    generateFilename() {
        const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
        const filename = `rct_extraction_${timestamp}.csv`;
        return path.join(this.outputFolder, filename);
    }

    /**
     * Define CSV headers from analyzer schema
     */
    defineHeaders() {
        const headers = [
            // Metadata
            { id: 'filename', title: 'Filename' },
            { id: 'extracted_at', title: 'Extracted At' }
        ];

        // If we have the schema, use it
        if (this.schema && this.schema.fields) {
            // Sort fields alphabetically for consistent column order
            const fieldNames = Object.keys(this.schema.fields).sort();
            
            fieldNames.forEach(fieldName => {
                const field = this.schema.fields[fieldName];
                
                // Handle complex types
                if (field.type === 'object' && field.properties) {
                    // For objects like demographicsSex, create nested columns
                    Object.keys(field.properties).forEach(prop => {
                        headers.push({
                            id: `${fieldName}.${prop}`,
                            title: `${fieldName} - ${prop}`
                        });
                    });
                } else if (field.type === 'array' && field.items?.properties) {
                    // For arrays like demographicsAge, flatten properties
                    Object.keys(field.items.properties).forEach(prop => {
                        headers.push({
                            id: `${fieldName}.${prop}`,
                            title: `${fieldName} - ${prop}`
                        });
                    });
                } else {
                    // Simple field - add value and confidence
                    headers.push({ id: fieldName, title: fieldName });
                    headers.push({ id: `${fieldName}_confidence`, title: `${fieldName} Confidence` });
                }
            });

            logger.info(`Generated ${headers.length} CSV columns from analyzer schema`);
        } else {
            logger.warn('Using fallback headers - analyzer schema not loaded');
            // Fallback to basic headers if schema not available
            headers.push(
                { id: 'infotitle', title: 'Title' },
                { id: 'journalName', title: 'Journal Name' },
                { id: 'yearOfPublication', title: 'Year' }
            );
        }

        return headers;
    }

    /**
     * Flatten extracted data with confidence scores
     */
    flattenData(extractedData, filename) {
        const flat = {
            filename: filename,
            extracted_at: new Date().toISOString()
        };

        // Flatten all fields with confidence scores
        for (const [fieldName, fieldData] of Object.entries(extractedData)) {
            if (typeof fieldData === 'object' && fieldData !== null && 'value' in fieldData) {
                flat[fieldName] = fieldData.value;
                flat[`${fieldName}_confidence`] = fieldData.confidence || 0;
            } else {
                flat[fieldName] = fieldData;
                flat[`${fieldName}_confidence`] = 0;
            }
        }

        return flat;
    }

    /**
     * Write results to CSV
     */
    async writeToCSV(extractedDataList, filename = null) {
        try {
            const csvPath = filename || this.generateFilename();
            const fileExists = await fs.pathExists(csvPath);

            const csvWriter = createObjectCsvWriter({
                path: csvPath,
                header: this.defineHeaders(),
                append: fileExists
            });

            await csvWriter.writeRecords(extractedDataList);

            logger.info(`CSV written: ${path.basename(csvPath)}`, {
                rows: extractedDataList.length,
                path: csvPath
            });

            return csvPath;
        } catch (error) {
            logger.error('Failed to write CSV', error);
            throw error;
        }
    }
}

export { CSVWriter };
export default CSVWriter;


