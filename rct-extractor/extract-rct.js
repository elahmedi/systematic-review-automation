#!/usr/bin/env node

/**
 * RCT Data Extraction Script using Azure Content Understanding
 * Processes PDFs and extracts structured data based on a custom JSON schema
 * 
 * Usage:
 *   node extract-rct.js --folder=/path/to/pdfs --schema=./my-schema.json
 *   node extract-rct.js --folder=/path/to/pdfs  # Uses default field-schema.json
 * 
 * The schema JSON defines what fields to extract from each PDF.
 * See field-schema.json for an example with 65+ RCT-specific fields.
 */

import dotenv from 'dotenv';
import fs from 'fs-extra';
import path from 'path';
import { fileURLToPath } from 'url';
import readline from 'readline';
import { AzureContentUnderstandingClient } from './azure-content-understanding-client.js';
import { DualCSVWriter } from './dual-csv-writer.js';
import { logger } from './logger.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Load environment variables from global .env in repository root
dotenv.config({ path: path.join(__dirname, '..', '.env') });

class RCTExtractionPipeline {
    constructor() {
        this.client = null;
        this.csvWriter = null;
        this.extractedDataList = [];
        this.errors = [];
        this.outputFolder = null;
        this.pdfFolderName = null;
    }

    /**
     * Initialize the pipeline
     */
    async initialize() {
        try {
            logger.info('🚀 Initializing RCT Extraction Pipeline with Azure Content Understanding...');

            // Validate environment variables
            this.validateEnvironment();

            // Create timestamped output folder for this extraction run
            const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
            const baseOutputFolder = path.resolve(__dirname, 'output');
            this.outputFolder = path.join(baseOutputFolder, `extraction_${timestamp}`);
            await fs.ensureDir(this.outputFolder);
            logger.info(`📁 Output folder: ${path.basename(this.outputFolder)}`);

            // Initialize Azure Content Understanding client
            this.client = new AzureContentUnderstandingClient({
                endpoint: process.env.AZURE_CONTENT_UNDERSTANDING_ENDPOINT,
                apiVersion: process.env.AZURE_CONTENT_UNDERSTANDING_API_VERSION,
                subscriptionKey: process.env.AZURE_CONTENT_UNDERSTANDING_SUBSCRIPTION_KEY,
                aadToken: process.env.AZURE_CONTENT_UNDERSTANDING_AAD_TOKEN,
                analyzerId: process.env.AZURE_CONTENT_UNDERSTANDING_ANALYZER_ID,
                timeoutSeconds: parseInt(process.env.TIMEOUT_SECONDS || '3600'),
                pollingIntervalSeconds: parseInt(process.env.POLLING_INTERVAL_SECONDS || '2')
            });

            // Initialize Dual CSV writer
            this.csvWriter = new DualCSVWriter();

            logger.info('✅ Pipeline initialized successfully');
        } catch (error) {
            logger.error('Failed to initialize pipeline', error);
            throw error;
        }
    }

    /**
     * Validate environment variables
     */
    validateEnvironment() {
        const required = [
            'AZURE_CONTENT_UNDERSTANDING_ENDPOINT',
            'AZURE_CONTENT_UNDERSTANDING_API_VERSION',
            'AZURE_CONTENT_UNDERSTANDING_ANALYZER_ID'
        ];

        const missing = required.filter(key => !process.env[key]);

        if (missing.length > 0) {
            throw new Error(`Missing required environment variables: ${missing.join(', ')}\nPlease copy env.template to .env and fill in your values.`);
        }

        // Check for authentication
        if (!process.env.AZURE_CONTENT_UNDERSTANDING_SUBSCRIPTION_KEY && 
            !process.env.AZURE_CONTENT_UNDERSTANDING_AAD_TOKEN) {
            throw new Error('Either AZURE_CONTENT_UNDERSTANDING_SUBSCRIPTION_KEY or AZURE_CONTENT_UNDERSTANDING_AAD_TOKEN must be provided');
        }
    }

    /**
     * Prompt user for PDF folder name
     */
    async promptForFolder() {
        return new Promise((resolve) => {
            const rl = readline.createInterface({
                input: process.stdin,
                output: process.stdout
            });

            console.log('\n📁 PDF Folder Selection');
            console.log('─'.repeat(50));
            rl.question('Enter the PDF folder name (e.g., pdf, pdf1000_1): ', (answer) => {
                rl.close();
                resolve(answer.trim() || 'pdf');
            });
        });
    }

    /**
     * Get list of PDF files
     */
    async getPDFFiles() {
        // Determine if path is absolute or relative
        let pdfFolder;
        if (path.isAbsolute(this.pdfFolderName)) {
            // Use absolute path as-is
            pdfFolder = this.pdfFolderName;
        } else {
            // Treat as relative to parent directory
            pdfFolder = path.join(__dirname, '..', this.pdfFolderName);
        }

        if (!await fs.pathExists(pdfFolder)) {
            throw new Error(`PDF folder not found: ${pdfFolder}\nPlease check the path and try again.`);
        }

        const files = await fs.readdir(pdfFolder);
        const pdfFiles = files.filter(file => file.toLowerCase().endsWith('.pdf'));

        logger.info(`📁 Found ${pdfFiles.length} PDF files in folder: ${pdfFolder}`);

        return pdfFiles.map(file => ({
            name: file,
            path: path.join(pdfFolder, file)
        }));
    }

    /**
     * Process a single PDF
     */
    async processPDF(pdfFile) {
        try {
            logger.info(`\n${'='.repeat(80)}`);
            logger.info(`📄 Processing: ${pdfFile.name}`);
            logger.info('='.repeat(80));

            const startTime = Date.now();

            // Analyze PDF with Azure Content Understanding
            logger.info('🔍 Analyzing PDF with Azure Content Understanding...');
            const analysisResult = await this.client.analyzeFile(pdfFile.path);

            // Extract fields from result
            logger.info('📋 Extracting fields from analysis result...');
            const extractedFields = this.client.extractFields(analysisResult);

            // Calculate derived fields
            const enrichedData = this.calculateDerivedFields(extractedFields);

            const duration = ((Date.now() - startTime) / 1000).toFixed(2);
            logger.info(`⏱️ Processing completed in ${duration} seconds`);

            // Log statistics
            const fieldCount = Object.keys(enrichedData).length;
            const extractedCount = Object.values(enrichedData).filter(f => 
                f && typeof f === 'object' && f.value && f.value !== 'Not found'
            ).length;

            logger.info(`📊 Extracted ${extractedCount}/${fieldCount} fields`, {
                filename: pdfFile.name,
                extractionRate: `${Math.round((extractedCount / fieldCount) * 100)}%`
            });

            return {
                filename: pdfFile.name,
                fields: enrichedData,
                extractedAt: new Date().toISOString()
            };

        } catch (error) {
            logger.error(`Failed to process PDF: ${pdfFile.name}`, error);
            
            this.errors.push({
                filename: pdfFile.name,
                error: error.message,
                stack: error.stack,
                timestamp: new Date().toISOString()
            });

            return null;
        }
    }

    /**
     * Calculate derived/generated fields
     */
    calculateDerivedFields(fields) {
        // Calculate loss of follow-up
        if (fields.numberRandomized && fields.numberCompleted) {
            try {
                const randomized = parseInt(fields.numberRandomized.value);
                const completed = parseInt(fields.numberCompleted.value);
                if (!isNaN(randomized) && !isNaN(completed) && randomized > 0) {
                    const loss = ((randomized - completed) / randomized * 100).toFixed(2);
                    fields.lossOfFollowUp = {
                        value: `${loss}%`,
                        confidence: 1.0,
                        type: 'calculated'
                    };
                }
            } catch (e) {
                logger.warn('Failed to calculate loss of follow-up', e);
            }
        }

        // Calculate years since publication
        if (fields.yearOfPublication) {
            try {
                const year = parseInt(fields.yearOfPublication.value);
                if (!isNaN(year)) {
                    const yearsSince = new Date().getFullYear() - year;
                    fields.yearsSincePublication = {
                        value: yearsSince,
                        confidence: 1.0,
                        type: 'calculated'
                    };
                }
            } catch (e) {
                logger.warn('Failed to calculate years since publication', e);
            }
        }

        // Calculate average citations per year
        if (fields.totalCitations && fields.yearsSincePublication) {
            try {
                const citations = parseInt(fields.totalCitations.value);
                const years = fields.yearsSincePublication.value;
                if (!isNaN(citations) && years > 0) {
                    const avgCitations = (citations / years).toFixed(2);
                    fields.averageCitationsPerYear = {
                        value: avgCitations,
                        confidence: 1.0,
                        type: 'calculated'
                    };
                }
            } catch (e) {
                logger.warn('Failed to calculate average citations per year', e);
            }
        }

        return fields;
    }

    /**
     * Process all PDFs
     */
    async processAllPDFs() {
        try {
            const pdfFiles = await this.getPDFFiles();

            if (pdfFiles.length === 0) {
                logger.warn('⚠️ No PDF files found to process');
                return;
            }

            logger.info(`\n📊 Starting batch processing of ${pdfFiles.length} PDFs...\n`);

            for (let i = 0; i < pdfFiles.length; i++) {
                const pdfFile = pdfFiles[i];
                logger.info(`\n[${i + 1}/${pdfFiles.length}] Processing: ${pdfFile.name}`);

                const extractedData = await this.processPDF(pdfFile);

                if (extractedData) {
                    this.extractedDataList.push(extractedData);

                    // Save intermediate results
                    if (this.extractedDataList.length > 0) {
                        await this.saveIntermediateResults();
                    }
                }

                // Small delay between PDFs
                if (i < pdfFiles.length - 1) {
                    logger.info('⏸️ Waiting 0 seconds before next PDF...');
                    // await this._sleep(2000);
                }
            }

            logger.info(`\n✅ Batch processing complete!`);
            logger.info(`📊 Successfully processed: ${this.extractedDataList.length}/${pdfFiles.length} PDFs`);
            
            if (this.errors.length > 0) {
                logger.warn(`⚠️ Errors encountered: ${this.errors.length}`);
            }

        } catch (error) {
            logger.error('Fatal error during batch processing', error);
            throw error;
        }
    }

    /**
     * Save intermediate results
     */
    async saveIntermediateResults() {
        try {
            // Save intermediate with dual CSV writer to timestamped folder
            await this.csvWriter.writeBothCSVs(this.extractedDataList, this.outputFolder);
            logger.debug('💾 Intermediate results saved (both CSVs)');
        } catch (error) {
            logger.warn('Failed to save intermediate results', error);
        }
    }

    /**
     * Save final results (both main and demographics CSVs)
     */
    async saveFinalResults() {
        try {
            if (this.extractedDataList.length === 0) {
                logger.warn('⚠️ No data to save');
                return;
            }

            logger.info('\n💾 Saving final results to dual CSV outputs...');

            // Write both CSV files to timestamped folder
            const result = await this.csvWriter.writeBothCSVs(this.extractedDataList, this.outputFolder);

            logger.info(`\n📊 Results saved to: ${path.basename(this.outputFolder)}/`);
            logger.info(`   Main CSV: ${path.basename(result.mainPath)} (${result.mainRows} papers)`);
            logger.info(`   Demographics CSV: ${path.basename(result.demoPath)} (${result.demoRows} groups)`);

            // Save error report if there were errors
            if (this.errors.length > 0) {
                const errorPath = path.join(this.outputFolder, 'error_report.json');
                await fs.writeJson(errorPath, {
                    timestamp: new Date().toISOString(),
                    totalErrors: this.errors.length,
                    errors: this.errors
                }, { spaces: 2 });
                logger.info(`❌ Error report: error_report.json`);
            }

            return result;

        } catch (error) {
            logger.error('Failed to save final results', error);
            throw error;
        }
    }

    /**
     * Print summary
     */
    printSummary() {
        console.log('\n' + '='.repeat(80));
        console.log('📊 EXTRACTION SUMMARY');
        console.log('='.repeat(80));
        console.log(`Total PDFs processed: ${this.extractedDataList.length + this.errors.length}`);
        console.log(`Successful extractions: ${this.extractedDataList.length}`);
        console.log(`Failed extractions: ${this.errors.length}`);
        console.log(`Success rate: ${Math.round((this.extractedDataList.length / (this.extractedDataList.length + this.errors.length)) * 100)}%`);
        console.log('='.repeat(80) + '\n');
    }

    /**
     * Sleep utility
     */
    _sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    /**
     * Run the complete pipeline
     */
    async run(folderName = null) {
        const startTime = Date.now();

        try {
            // Get PDF folder name from argument or prompt
            if (folderName) {
                this.pdfFolderName = folderName;
                console.log(`\n✅ Using folder: ${this.pdfFolderName}\n`);
            } else {
                this.pdfFolderName = await this.promptForFolder();
                console.log(`\n✅ Selected folder: ${this.pdfFolderName}\n`);
            }

            // Initialize
            await this.initialize();

            // Process all PDFs
            await this.processAllPDFs();

            // Save results
            await this.saveFinalResults();

            // Print summary
            this.printSummary();

            const totalDuration = ((Date.now() - startTime) / 1000 / 60).toFixed(2);
            logger.info(`\n⏱️ Total pipeline execution time: ${totalDuration} minutes`);
            logger.info('✅ Pipeline completed successfully!');

        } catch (error) {
            logger.error('Pipeline failed', error);
            
            // Try to save what we have
            if (this.extractedDataList.length > 0) {
                logger.info('💾 Saving partial results before exit...');
                await this.saveFinalResults();
            }

            process.exit(1);
        }
    }
}

// Run the pipeline if this is the main module
if (import.meta.url === `file://${process.argv[1]}`) {
    // Parse command-line arguments
    const folderArg = process.argv.find(arg => arg.startsWith('--folder='));
    const schemaArg = process.argv.find(arg => arg.startsWith('--schema='));
    const helpArg = process.argv.includes('--help') || process.argv.includes('-h');
    
    if (helpArg) {
        console.log(`
RCT Data Extraction Script
==========================

Extracts structured data from PDF documents using Azure AI Content Understanding.

Usage:
  node extract-rct.js --folder=<path> [--schema=<path>]

Options:
  --folder=<path>   Path to folder containing PDF files to process (required)
  --schema=<path>   Path to JSON schema defining fields to extract
                    Default: ./field-schema.json
  --help, -h        Show this help message

Examples:
  node extract-rct.js --folder=./pdfs
  node extract-rct.js --folder=./pdfs --schema=./custom-schema.json

Schema File:
  The schema JSON defines what fields to extract. See field-schema.json for 
  an example with 65+ RCT-specific fields including study design, population,
  intervention, outcomes, and risk of bias indicators.

Environment:
  Configure Azure credentials in the root .env file (copy from env.example).
`);
        process.exit(0);
    }
    
    const folderName = folderArg ? folderArg.split('=')[1] : null;
    const schemaPath = schemaArg ? schemaArg.split('=')[1] : path.join(__dirname, 'field-schema.json');
    
    // Validate schema file exists
    if (!fs.existsSync(schemaPath)) {
        console.error(`\n❌ Schema file not found: ${schemaPath}`);
        console.error('\nPlease provide a valid schema JSON file with --schema=<path>');
        console.error('Or ensure field-schema.json exists in the rct-extractor directory.\n');
        process.exit(1);
    }
    
    // Log schema being used
    console.log(`\n📋 Using schema: ${schemaPath}`);
    
    const pipeline = new RCTExtractionPipeline();
    pipeline.run(folderName).catch(error => {
        console.error('Fatal error:', error);
        process.exit(1);
    });
}

export { RCTExtractionPipeline };
export default RCTExtractionPipeline;


