#!/usr/bin/env node
import dotenv from 'dotenv';
import LibraryPDFRetriever from './library-retriever.js';
import csvParser from 'csv-parser';
import { createObjectCsvWriter } from 'csv-writer';
import fs from 'fs-extra';
import path from 'path';
import logger from './logger.js';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Load environment variables from global .env in repository root
dotenv.config({ path: path.join(__dirname, '..', '.env') });

class BatchPDFRetriever {
    constructor() {
        this.retriever = new LibraryPDFRetriever();
        this.results = {
            success: [],
            failed: [],
            cached: []
        };
    }
    
    /**
     * Process a CSV file with DOIs
     * Expected CSV format: columns including "DOI", "PMID", "Title", etc.
     */
    async processCSV(csvPath, options = {}) {
        const {
            doiColumn = 'DOI',
            titleColumn = 'Title',
            startFrom = 0,
            limit = null,
            delayBetweenRequests = 2000  // 2 seconds between requests
        } = options;
        
        logger.info(`\n${'='.repeat(80)}`);
        logger.info(`BATCH PDF RETRIEVAL STARTING`);
        logger.info(`${'='.repeat(80)}`);
        logger.info(`Input CSV: ${csvPath}`);
        logger.info(`Starting from row: ${startFrom}`);
        logger.info(`Limit: ${limit || 'none'}`);
        logger.info(`Delay between requests: ${delayBetweenRequests}ms`);
        
        // Read CSV
        const studies = await this._readCSV(csvPath);
        logger.info(`Found ${studies.length} studies in CSV`);
        
        // Apply start/limit
        const studiesToProcess = limit 
            ? studies.slice(startFrom, startFrom + limit)
            : studies.slice(startFrom);
        
        logger.info(`Processing ${studiesToProcess.length} studies...\n`);
        
        // Process each study
        for (let i = 0; i < studiesToProcess.length; i++) {
            const study = studiesToProcess[i];
            const doi = study[doiColumn];
            const title = study[titleColumn] || 'Unknown';
            
            if (!doi) {
                logger.warn(`Skipping row ${startFrom + i + 1}: No DOI found`);
                this.results.failed.push({
                    ...study,
                    error: 'No DOI provided',
                    rowNumber: startFrom + i + 1
                });
                continue;
            }
            
            logger.info(`\n[${ i + 1}/${studiesToProcess.length}] Processing:`);
            logger.info(`  DOI: ${doi}`);
            logger.info(`  Title: ${title.substring(0, 80)}...`);
            
            try {
                const result = await this.retriever.retrievePDF(doi);
                
                if (result.success) {
                    if (result.alreadyExists) {
                        this.results.cached.push({ 
                            ...study, 
                            pdfPath: result.path,
                            rowNumber: startFrom + i + 1
                        });
                        logger.info(`  ✓ Already downloaded`);
                    } else {
                        this.results.success.push({ 
                            ...study, 
                            pdfPath: result.path,
                            source: result.source,
                            rowNumber: startFrom + i + 1
                        });
                        logger.info(`  ✅ SUCCESS - Source: ${result.source}`);
                    }
                } else {
                    this.results.failed.push({ 
                        ...study, 
                        error: result.error,
                        rowNumber: startFrom + i + 1
                    });
                    logger.error(`  ❌ FAILED - ${result.error}`);
                    logger.info(`  ⏭️  Moving to next PDF...`);
                }
                
            } catch (error) {
                this.results.failed.push({ 
                    ...study, 
                    error: error.message,
                    rowNumber: startFrom + i + 1
                });
                logger.error(`  ❌ ERROR - ${error.message}`);
                logger.info(`  ⏭️  Moving to next PDF...`);
            }
            
            // Progress update
            this._printProgress();
            
            // Delay between requests (be nice to servers)
            if (i < studiesToProcess.length - 1 && delayBetweenRequests > 0) {
                logger.info(`  ⏸️  Waiting ${delayBetweenRequests}ms...`);
                await this._sleep(delayBetweenRequests);
            }
        }
        
        // Generate report
        await this._generateReport();
        
        return this.results;
    }
    
    async _readCSV(csvPath) {
        return new Promise((resolve, reject) => {
            const results = [];
            fs.createReadStream(csvPath)
                .pipe(csvParser())
                .on('data', (data) => results.push(data))
                .on('end', () => resolve(results))
                .on('error', reject);
        });
    }
    
    _printProgress() {
        const total = this.results.success.length + this.results.failed.length + this.results.cached.length;
        const successRate = total > 0 
            ? ((this.results.success.length / total) * 100).toFixed(1)
            : 0;
        
        logger.info(`\n  📊 Progress: ${total} processed | ✅ ${this.results.success.length} new | 💾 ${this.results.cached.length} cached | ❌ ${this.results.failed.length} failed | Success rate: ${successRate}%`);
    }
    
    async _generateReport() {
        const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
        const reportDir = path.join(__dirname, 'reports');
        await fs.ensureDir(reportDir);
        
        logger.info(`\n${'='.repeat(80)}`);
        logger.info(`BATCH RETRIEVAL COMPLETE`);
        logger.info(`${'='.repeat(80)}`);
        logger.info(`✅ Successfully downloaded: ${this.results.success.length}`);
        logger.info(`💾 Already cached: ${this.results.cached.length}`);
        logger.info(`❌ Failed: ${this.results.failed.length}`);
        logger.info(`📊 Total processed: ${this.results.success.length + this.results.failed.length + this.results.cached.length}`);
        
        // Write success report
        if (this.results.success.length > 0) {
            const successPath = path.join(reportDir, `success_${timestamp}.csv`);
            const successWriter = createObjectCsvWriter({
                path: successPath,
                header: [
                    { id: 'rowNumber', title: 'Row Number' },
                    { id: 'DOI', title: 'DOI' },
                    { id: 'Title', title: 'Title' },
                    { id: 'pdfPath', title: 'PDF Path' },
                    { id: 'source', title: 'Source' }
                ]
            });
            await successWriter.writeRecords(this.results.success);
            logger.info(`\n✅ Success report: ${successPath}`);
        }
        
        // Write failed report
        if (this.results.failed.length > 0) {
            const failedPath = path.join(reportDir, `failed_${timestamp}.csv`);
            const failedWriter = createObjectCsvWriter({
                path: failedPath,
                header: [
                    { id: 'rowNumber', title: 'Row Number' },
                    { id: 'DOI', title: 'DOI' },
                    { id: 'Title', title: 'Title' },
                    { id: 'error', title: 'Error' }
                ]
            });
            await failedWriter.writeRecords(this.results.failed);
            logger.info(`❌ Failed report: ${failedPath}`);
            logger.info(`\n🔄 To retry failed DOIs, use the failed report as input.`);
        }
        
        logger.info(`${'='.repeat(80)}\n`);
    }
    
    _sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}

// CLI usage
if (import.meta.url === `file://${process.argv[1]}`) {
    const csvPath = process.argv[2];
    const startFrom = parseInt(process.argv[3]) || 0;
    const limit = parseInt(process.argv[4]) || null;
    
    if (!csvPath) {
        console.error('Usage: node batch-retriever.js <csv-file> [start-from] [limit]');
        console.error('Example: node batch-retriever.js covidence_export.csv');
        console.error('Example: node batch-retriever.js covidence_export.csv 0 10  # First 10 only');
        console.error('Example: node batch-retriever.js covidence_export.csv 10 5  # Skip 10, process 5');
        process.exit(1);
    }
    
    const batchRetriever = new BatchPDFRetriever();
    
    batchRetriever.processCSV(csvPath, { startFrom, limit })
        .then(() => {
            logger.info('🎉 Batch processing complete!');
            process.exit(0);
        })
        .catch(error => {
            logger.error('Fatal error in batch processing:', error);
            process.exit(1);
        });
}

export default BatchPDFRetriever;

