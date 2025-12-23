#!/usr/bin/env node
import fs from 'fs-extra';
import path from 'path';
import logger from './logger.js';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

/**
 * RIS Parser - Extracts references from RIS format files
 * Works with exports from Zotero, EndNote, Mendeley, RefWorks, etc.
 */
class RISParser {
    constructor() {
        this.fieldMapping = {
            'TY': 'type',           // Type of reference
            'TI': 'title',          // Title
            'AU': 'authors',        // Authors (multiple)
            'PY': 'year',           // Publication year
            'JO': 'journal',        // Journal name
            'VL': 'volume',         // Volume
            'IS': 'issue',          // Issue
            'SP': 'startPage',      // Start page
            'EP': 'endPage',        // End page
            'DO': 'doi',            // DOI
            'AN': 'accessionNumber', // Accession number (often PMID)
            'UR': 'url',            // URL
            'ID': 'id',             // ID
            'AB': 'abstract',       // Abstract
            'PB': 'publisher',      // Publisher
            'ER': 'endOfRecord'     // End of record marker
        };
    }
    
    /**
     * Parse RIS file and extract all references
     */
    async parse(risFilePath) {
        logger.info(`📖 Parsing RIS file: ${risFilePath}`);
        
        const content = await fs.readFile(risFilePath, 'utf-8');
        const lines = content.split('\n');
        
        const references = [];
        let currentRef = this._createEmptyReference();
        let lineNumber = 0;
        
        for (const line of lines) {
            lineNumber++;
            const trimmed = line.trim();
            
            if (!trimmed) continue;
            
            // Parse RIS field (format: "TAG  - VALUE")
            const match = trimmed.match(/^([A-Z0-9]{2})\s+-\s*(.*)$/);
            
            if (match) {
                const [, tag, value] = match;
                const field = this.fieldMapping[tag];
                
                if (tag === 'ER') {
                    // End of record - save and reset
                    if (this._isValidReference(currentRef)) {
                        this._cleanReference(currentRef);
                        references.push(currentRef);
                    }
                    currentRef = this._createEmptyReference();
                } else if (field) {
                    if (field === 'authors') {
                        // Authors are multi-line
                        currentRef.authors.push(value);
                    } else if (field === 'doi') {
                        // Extract clean DOI from URL
                        currentRef.doi = this._extractDOI(value);
                    } else if (field === 'accessionNumber') {
                        // Try to extract PMID
                        const pmid = this._extractPMID(value);
                        if (pmid) currentRef.pmid = pmid;
                        currentRef.accessionNumber = value;
                    } else {
                        currentRef[field] = value;
                    }
                }
            }
        }
        
        // Handle last record if file doesn't end with ER
        if (this._isValidReference(currentRef)) {
            this._cleanReference(currentRef);
            references.push(currentRef);
        }
        
        logger.info(`✅ Parsed ${references.length} references from RIS file`);
        this._printStatistics(references);
        
        return references;
    }
    
    /**
     * Extract clean DOI from various formats
     */
    _extractDOI(doiString) {
        if (!doiString) return null;
        
        // Remove common prefixes
        let doi = doiString
            .replace(/^https?:\/\/(dx\.)?doi\.org\//i, '')
            .replace(/^doi:\s*/i, '')
            .trim();
        
        // Validate DOI format (starts with 10.)
        if (doi && doi.startsWith('10.')) {
            return doi;
        }
        
        return null;
    }
    
    /**
     * Try to extract PMID from accession number
     */
    _extractPMID(accessionNumber) {
        if (!accessionNumber) return null;
        
        // PMID is typically all digits
        const match = accessionNumber.match(/\b(\d{7,8})\b/);
        if (match) {
            return match[1];
        }
        
        return null;
    }
    
    /**
     * Create empty reference object
     */
    _createEmptyReference() {
        return {
            type: null,
            title: null,
            authors: [],
            year: null,
            journal: null,
            volume: null,
            issue: null,
            startPage: null,
            endPage: null,
            doi: null,
            pmid: null,
            accessionNumber: null,
            url: null,
            id: null,
            abstract: null,
            publisher: null
        };
    }
    
    /**
     * Check if reference has minimum required fields
     */
    _isValidReference(ref) {
        return ref.title || ref.doi || ref.pmid;
    }
    
    /**
     * Clean up reference fields
     */
    _cleanReference(ref) {
        // Combine authors with semicolon
        if (ref.authors && ref.authors.length > 0) {
            ref.authorsString = ref.authors.join('; ');
            ref.firstAuthor = ref.authors[0];
        }
        
        // Clean title
        if (ref.title) {
            ref.title = ref.title.trim();
        }
        
        // Ensure year is numeric
        if (ref.year) {
            const yearMatch = ref.year.match(/\d{4}/);
            if (yearMatch) {
                ref.year = yearMatch[0];
            }
        }
    }
    
    /**
     * Print parsing statistics
     */
    _printStatistics(references) {
        const withDOI = references.filter(r => r.doi).length;
        const withPMID = references.filter(r => r.pmid).length;
        const withBoth = references.filter(r => r.doi && r.pmid).length;
        const withNeither = references.filter(r => !r.doi && !r.pmid).length;
        
        logger.info('\n📊 Reference Statistics:');
        logger.info(`   Total references: ${references.length}`);
        logger.info(`   With DOI: ${withDOI} (${((withDOI/references.length)*100).toFixed(1)}%)`);
        logger.info(`   With PMID: ${withPMID} (${((withPMID/references.length)*100).toFixed(1)}%)`);
        logger.info(`   With both: ${withBoth}`);
        logger.info(`   With neither: ${withNeither} (${((withNeither/references.length)*100).toFixed(1)}%)`);
    }
    
    /**
     * Export references to CSV format for batch retriever
     */
    async exportToCSV(references, outputPath) {
        logger.info(`\n💾 Exporting to CSV: ${outputPath}`);
        
        // CSV header
        const headers = ['DOI', 'PMID', 'Title', 'FirstAuthor', 'Year', 'Journal'];
        const rows = [headers.join(',')];
        
        for (const ref of references) {
            const row = [
                this._escapeCSV(ref.doi || ''),
                this._escapeCSV(ref.pmid || ''),
                this._escapeCSV(ref.title || ''),
                this._escapeCSV(ref.firstAuthor || ''),
                this._escapeCSV(ref.year || ''),
                this._escapeCSV(ref.journal || '')
            ];
            rows.push(row.join(','));
        }
        
        await fs.writeFile(outputPath, rows.join('\n'), 'utf-8');
        logger.info(`✅ Exported ${references.length} references to CSV`);
        
        return outputPath;
    }
    
    /**
     * Escape CSV field (handle commas, quotes)
     */
    _escapeCSV(field) {
        if (!field) return '';
        
        const str = String(field);
        
        // If contains comma, quote, or newline, wrap in quotes and escape quotes
        if (str.includes(',') || str.includes('"') || str.includes('\n')) {
            return `"${str.replace(/"/g, '""')}"`;
        }
        
        return str;
    }
    
    /**
     * Filter references by criteria
     */
    filterReferences(references, options = {}) {
        let filtered = references;
        
        if (options.requireDOI) {
            filtered = filtered.filter(r => r.doi);
            logger.info(`Filtered to ${filtered.length} references with DOI`);
        }
        
        if (options.requirePMID) {
            filtered = filtered.filter(r => r.pmid);
            logger.info(`Filtered to ${filtered.length} references with PMID`);
        }
        
        if (options.yearFrom) {
            filtered = filtered.filter(r => !r.year || parseInt(r.year) >= options.yearFrom);
            logger.info(`Filtered to ${filtered.length} references from year ${options.yearFrom}`);
        }
        
        if (options.yearTo) {
            filtered = filtered.filter(r => !r.year || parseInt(r.year) <= options.yearTo);
            logger.info(`Filtered to ${filtered.length} references up to year ${options.yearTo}`);
        }
        
        return filtered;
    }
}

// CLI usage
if (import.meta.url === `file://${process.argv[1]}`) {
    const risFile = process.argv[2];
    const outputFile = process.argv[3] || risFile.replace(/\.ris$/i, '_parsed.csv');
    
    if (!risFile) {
        console.error('Usage: node ris-parser.js <ris-file> [output-csv]');
        console.error('Example: node ris-parser.js references.ris');
        console.error('Example: node ris-parser.js references.ris output.csv');
        process.exit(1);
    }
    
    const parser = new RISParser();
    
    parser.parse(risFile)
        .then(references => {
            // Export to CSV
            return parser.exportToCSV(references, outputFile);
        })
        .then(csvPath => {
            console.log('\n✅ SUCCESS!');
            console.log(`📄 CSV file: ${csvPath}`);
            console.log(`\n💡 Next step: Download PDFs with:`);
            console.log(`   npm run batch ${path.basename(csvPath)}`);
        })
        .catch(error => {
            console.error('\n❌ ERROR:', error.message);
            process.exit(1);
        });
}

export default RISParser;

