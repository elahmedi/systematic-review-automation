#!/usr/bin/env node
/**
 * Library PDF Retriever
 * 
 * Retrieves PDFs using institutional library access via EZProxy.
 * Works with any EZProxy-enabled university library.
 * 
 * Strategies (in order):
 * 1. Unpaywall - Free open access PDFs
 * 2. Library EZProxy - Institutional access
 */

import { chromium } from 'playwright';
import dotenv from 'dotenv';
import path from 'path';
import fs from 'fs-extra';
import sanitize from 'sanitize-filename';
import logger from './logger.js';
import { fileURLToPath } from 'url';
import fetch from 'node-fetch';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Load environment variables from global .env in repository root
dotenv.config({ path: path.join(__dirname, '..', '.env') });

class LibraryPDFRetriever {
    constructor() {
        // EZProxy configuration - customize for your institution
        // Common format: https://lib-ezproxy.university.edu/login?url=
        this.ezproxyPrefix = process.env.EZPROXY_PREFIX || "https://lib-ezproxy.youruniversity.edu/login?url=";
        
        this.credentials = {
            username: process.env.LIBRARY_USERNAME,
            password: process.env.LIBRARY_PASSWORD
        };
        
        this.outputDir = path.resolve(__dirname, process.env.PDF_OUTPUT_DIR || '../pdf');
        this.headless = process.env.BROWSER_HEADLESS !== 'false';
        this.downloadTimeout = parseInt(process.env.DOWNLOAD_TIMEOUT_MS || '30000');
        this.unpaywallEmail = process.env.UNPAYWALL_EMAIL;
        
        // Ensure output directory exists
        fs.ensureDirSync(this.outputDir);
        fs.ensureDirSync(path.join(__dirname, 'logs'));
        
        this._validateConfig();
    }
    
    _validateConfig() {
        if (!this.ezproxyPrefix || this.ezproxyPrefix.includes('youruniversity')) {
            console.warn('⚠️  Warning: EZPROXY_PREFIX not configured. Set it in .env for institutional access.');
        }
        if (!this.credentials.username) {
            console.warn('⚠️  Warning: LIBRARY_USERNAME not set. Institutional access will fail.');
        }
        if (!this.credentials.password) {
            console.warn('⚠️  Warning: LIBRARY_PASSWORD not set. Institutional access will fail.');
        }
    }
    
    /**
     * Try to get PDF from Unpaywall (free, open access)
     */
    async tryUnpaywall(doi) {
        if (!this.unpaywallEmail) {
            logger.info('Unpaywall email not configured, skipping open access check');
            return null;
        }
        
        try {
            logger.info(`Trying Unpaywall for DOI: ${doi}`);
            const response = await fetch(
                `https://api.unpaywall.org/v2/${doi}?email=${this.unpaywallEmail}`
            );
            
            if (!response.ok) {
                return null;
            }
            
            const data = await response.json();
            
            if (data.best_oa_location?.url_for_pdf) {
                logger.info(`✅ Found open access PDF via Unpaywall`);
                return {
                    url: data.best_oa_location.url_for_pdf,
                    source: 'unpaywall',
                    license: data.best_oa_location.license
                };
            }
            
            return null;
        } catch (error) {
            logger.warn(`Unpaywall lookup failed: ${error.message}`);
            return null;
        }
    }
    
    /**
     * Download PDF directly from a URL (for open access)
     */
    async downloadDirectPDF(url, outputPath) {
        try {
            logger.info(`Downloading PDF directly from: ${url}`);
            const response = await fetch(url);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const buffer = await response.arrayBuffer();
            await fs.writeFile(outputPath, Buffer.from(buffer));
            
            logger.info(`✅ Downloaded: ${outputPath}`);
            return { success: true, path: outputPath, source: 'direct' };
        } catch (error) {
            logger.error(`Direct download failed: ${error.message}`);
            return { success: false, error: error.message };
        }
    }
    
    /**
     * Main retrieval method - tries multiple strategies
     */
    async retrievePDF(doi, customFilename = null) {
        logger.info(`\n${'='.repeat(60)}`);
        logger.info(`Starting retrieval for DOI: ${doi}`);
        logger.info(`${'='.repeat(60)}`);
        
        // Generate filename
        const filename = customFilename || sanitize(doi.replace(/[\/\\]/g, '_')) + '.pdf';
        const outputPath = path.join(this.outputDir, filename);
        
        // Check if already downloaded
        if (await fs.pathExists(outputPath)) {
            logger.info(`✓ PDF already exists: ${outputPath}`);
            return { 
                success: true, 
                path: outputPath, 
                source: 'cached',
                alreadyExists: true 
            };
        }
        
        // Strategy 1: Try Unpaywall (open access)
        const openAccess = await this.tryUnpaywall(doi);
        if (openAccess) {
            const result = await this.downloadDirectPDF(openAccess.url, outputPath);
            if (result.success) {
                result.source = 'unpaywall';
                return result;
            }
        }
        
        // Strategy 2: Use Library EZProxy
        if (this.credentials.username && this.credentials.password) {
            logger.info(`Attempting retrieval via Library EZProxy...`);
            return await this.retrieveViaLibrary(doi, outputPath);
        } else {
            logger.error('Library credentials not configured. Cannot access institutional resources.');
            return {
                success: false,
                error: 'Library credentials not configured',
                doi: doi
            };
        }
    }
    
    /**
     * Retrieve PDF via Library EZProxy
     */
    async retrieveViaLibrary(doi, outputPath) {
        const browser = await chromium.launch({ 
            headless: this.headless,
            downloadsPath: this.outputDir
        });
        
        const context = await browser.newContext({
            acceptDownloads: true
        });
        
        const page = await context.newPage();
        
        try {
            // Build EZProxy URL
            const url = `${this.ezproxyPrefix}https://doi.org/${doi}`;
            logger.info(`Navigating to: ${url}`);
            
            await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 30000 });
            
            // Handle library login if needed
            await this._handleLibraryLogin(page);
            
            // Wait for publisher page to load
            await page.waitForLoadState('load');
            logger.info(`Reached publisher page: ${page.url()}`);
            
            // Find and download PDF
            const downloadResult = await this._findAndDownloadPDF(page, outputPath);
            
            if (downloadResult.success) {
                logger.info(`✅ Successfully retrieved PDF via Library EZProxy`);
                return { 
                    success: true, 
                    path: outputPath, 
                    source: 'library-ezproxy',
                    publisherURL: page.url()
                };
            } else {
                throw new Error(downloadResult.error || 'PDF download failed');
            }
            
        } catch (error) {
            logger.error(`❌ Failed to retrieve via Library: ${error.message}`);
            return { 
                success: false, 
                error: error.message,
                doi: doi
            };
        } finally {
            await browser.close();
        }
    }
    
    /**
     * Handle library authentication if login page appears
     */
    async _handleLibraryLogin(page) {
        const currentURL = page.url();
        
        // Check if we're on a login page by URL pattern
        const isLoginPage = currentURL.includes('adfs') || 
                           currentURL.includes('login') || 
                           currentURL.includes('authentication') ||
                           currentURL.includes('shibboleth') ||
                           currentURL.includes('idp') ||
                           currentURL.includes('ezproxy');
        
        if (!isLoginPage) {
            logger.info('✓ No login required (already past authentication)');
            return;
        }
        
        logger.info('🔐 Login page detected - attempting authentication...');
        logger.info(`   Current URL: ${currentURL}`);
        
        try {
            // Wait for any form input to appear
            await page.waitForSelector('input[type="text"], input[type="email"], input[name*="user"], input[id*="user"]', { 
                timeout: 5000 
            });
            
            // Common login form selectors (works with most institutions)
            const usernameSelectors = [
                'input[name="UserName"]',           // ADFS typical
                'input[id="userNameInput"]',        // ADFS alternative
                'input[name="j_username"]',         // Shibboleth
                'input[name="user"]',               // Generic
                'input[id="username"]',             // Generic
                'input[name="login"]',              // EZProxy
                'input[type="email"]',              // Email-based
                'input[type="text"]'                // Fallback
            ];
            
            const passwordSelectors = [
                'input[name="Password"]',           // ADFS typical
                'input[id="passwordInput"]',        // ADFS alternative
                'input[name="j_password"]',         // Shibboleth
                'input[name="pass"]',               // Generic
                'input[id="password"]',             // Generic
                'input[type="password"]'            // Fallback
            ];
            
            const submitSelectors = [
                'button[type="submit"]',
                'input[type="submit"]',
                'button:has-text("Sign in")',
                'button:has-text("Log in")',
                'button:has-text("Login")',
                'input[value="Sign in"]',
                'input[value="Login"]',
                '#submitButton'
            ];
            
            // Fill username
            let usernameEntered = false;
            for (const selector of usernameSelectors) {
                try {
                    const element = await page.$(selector);
                    if (element && await element.isVisible()) {
                        await element.fill(this.credentials.username);
                        logger.info(`✓ Username entered (selector: ${selector})`);
                        usernameEntered = true;
                        break;
                    }
                } catch (e) {
                    continue;
                }
            }
            
            if (!usernameEntered) {
                throw new Error('Could not find username field');
            }
            
            // Fill password
            let passwordEntered = false;
            for (const selector of passwordSelectors) {
                try {
                    const element = await page.$(selector);
                    if (element && await element.isVisible()) {
                        await element.fill(this.credentials.password);
                        logger.info(`✓ Password entered (selector: ${selector})`);
                        passwordEntered = true;
                        break;
                    }
                } catch (e) {
                    continue;
                }
            }
            
            if (!passwordEntered) {
                throw new Error('Could not find password field');
            }
            
            // Click submit
            let submitClicked = false;
            for (const selector of submitSelectors) {
                try {
                    const element = await page.$(selector);
                    if (element && await element.isVisible()) {
                        logger.info(`✓ Clicking submit button (selector: ${selector})`);
                        await element.click();
                        submitClicked = true;
                        break;
                    }
                } catch (e) {
                    continue;
                }
            }
            
            if (!submitClicked) {
                logger.info('⌨️  Pressing Enter to submit...');
                await page.keyboard.press('Enter');
            }
            
            // Wait for navigation after login
            logger.info('⏳ Waiting for authentication to complete...');
            await page.waitForNavigation({ timeout: 20000 });
            
            const newURL = page.url();
            logger.info(`✅ Authentication complete - now at: ${newURL}`);
            
        } catch (error) {
            logger.error(`❌ Login failed: ${error.message}`);
            throw new Error(`Authentication failed: ${error.message}`);
        }
    }
    
    /**
     * Find and download PDF from publisher page
     */
    async _findAndDownloadPDF(page, outputPath) {
        // Common PDF link selectors across major publishers
        const pdfSelectors = [
            // Direct PDF links
            'a[href*=".pdf"]',
            'a[href*="/pdf/"]',
            'a[href*="pdf?"]',
            
            // Text-based selectors
            'a:has-text("PDF")',
            'a:has-text("Download PDF")',
            'a:has-text("Full Text PDF")',
            'a:has-text("Download Article")',
            'button:has-text("PDF")',
            'button:has-text("Download")',
            
            // Aria labels (accessibility)
            'a[aria-label*="PDF"]',
            'a[aria-label*="Download"]',
            'button[aria-label*="PDF"]',
            
            // Class/ID based (common publishers)
            '.pdf-download',
            '.download-pdf',
            '.view-pdf',
            '.show-pdf',
            '#pdfLink',
            '[data-article-format="pdf"]',
            '[title*="PDF"]'
        ];
        
        logger.info('🔍 Searching for PDF download/view button...');
        
        for (const selector of pdfSelectors) {
            try {
                const element = await page.$(selector);
                if (element) {
                    const text = await element.textContent().catch(() => '');
                    logger.info(`Found potential PDF link: "${selector}" with text "${text}"`);
                    
                    const isVisible = await element.isVisible().catch(() => false);
                    if (!isVisible) {
                        logger.info(`   ⚠️ Element not visible, skipping...`);
                        continue;
                    }
                    
                    const href = await element.getAttribute('href').catch(() => null);
                    
                    const result = await this._tryDownloadClick(page, element, selector, outputPath, href);
                    if (result.success) {
                        return result;
                    }
                }
            } catch (error) {
                continue;
            }
        }
        
        logger.error('❌ Could not find or download PDF from publisher page');
        return { 
            success: false, 
            error: 'PDF download button not found on publisher page',
            url: page.url()
        };
    }
    
    /**
     * Try different strategies to download PDF after clicking
     */
    async _tryDownloadClick(page, element, selector, outputPath, href) {
        try {
            logger.info(`Attempting to click: ${selector}`);
            
            // Strategy 1: Direct download (wait for download event)
            try {
                const downloadPromise = page.waitForEvent('download', { timeout: 15000 }).catch(() => null);
                await element.click({ timeout: 10000 }).catch(() => {});
                const download = await downloadPromise;
                
                if (download) {
                    logger.info(`Download started: ${download.suggestedFilename()}`);
                    await download.saveAs(outputPath);
                    
                    const stats = await fs.stat(outputPath);
                    if (stats.size > 1000) {
                        logger.info(`✅ PDF downloaded successfully: ${outputPath} (${stats.size} bytes)`);
                        return { success: true, path: outputPath };
                    }
                }
            } catch (downloadError) {
                logger.info(`No immediate download, trying alternative strategies...`);
            }
            
            // Strategy 2: Check if clicking navigated to a PDF page
            await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {});
            const currentURL = page.url();
            
            if (currentURL.includes('.pdf') || currentURL.includes('/pdf')) {
                logger.info(`Navigated to PDF page: ${currentURL}`);
                return await this._downloadFromPDFPage(page, currentURL, outputPath);
            }
            
            // Strategy 3: Check if PDF opened in new popup/tab
            const context = page.context();
            const pages = context.pages();
            if (pages.length > 1) {
                logger.info(`New tab/window detected, checking for PDF...`);
                const newPage = pages[pages.length - 1];
                const newURL = newPage.url();
                
                if (newURL.includes('.pdf') || newURL.includes('/pdf')) {
                    logger.info(`PDF found in new tab: ${newURL}`);
                    const result = await this._downloadFromPDFPage(newPage, newURL, outputPath);
                    await newPage.close().catch(() => {});
                    return result;
                }
            }
            
            // Strategy 4: If href is a direct PDF link, fetch it
            if (href && (href.includes('.pdf') || href.includes('/pdf'))) {
                logger.info(`Direct PDF link found in href: ${href}`);
                const fullURL = new URL(href, page.url()).href;
                return await this._downloadFromPDFPage(page, fullURL, outputPath);
            }
            
            logger.warn(`Click succeeded but no PDF download triggered for ${selector}`);
            return { success: false };
            
        } catch (error) {
            logger.warn(`Click/download failed for ${selector}: ${error.message}`);
            return { success: false };
        }
    }
    
    /**
     * Download PDF from a page that displays the PDF directly
     */
    async _downloadFromPDFPage(page, pdfURL, outputPath) {
        try {
            logger.info(`Downloading PDF directly from: ${pdfURL}`);
            
            const response = await page.goto(pdfURL, { 
                waitUntil: 'load',
                timeout: 30000 
            });
            
            const contentType = response.headers()['content-type'] || '';
            logger.info(`Response content-type: ${contentType}`);
            
            if (contentType.includes('pdf')) {
                const pdfBuffer = await response.body();
                await fs.writeFile(outputPath, pdfBuffer);
                
                const stats = await fs.stat(outputPath);
                if (stats.size > 1000) {
                    logger.info(`✅ PDF downloaded successfully: ${outputPath} (${stats.size} bytes)`);
                    return { success: true, path: outputPath };
                } else {
                    logger.warn(`Downloaded file is too small (${stats.size} bytes)`);
                    await fs.remove(outputPath);
                    return { success: false };
                }
            } else {
                logger.warn(`Expected PDF but got: ${contentType}`);
                return { success: false };
            }
            
        } catch (error) {
            logger.error(`Failed to download from PDF page: ${error.message}`);
            return { success: false };
        }
    }
}

// CLI usage
if (import.meta.url === `file://${process.argv[1]}`) {
    const doi = process.argv[2];
    const customFilename = process.argv[3];
    
    if (!doi) {
        console.error('Usage: node library-retriever.js <DOI> [custom-filename.pdf]');
        console.error('Example: node library-retriever.js 10.1001/jama.2023.12345');
        process.exit(1);
    }
    
    const retriever = new LibraryPDFRetriever();
    
    retriever.retrievePDF(doi, customFilename)
        .then(result => {
            if (result.success) {
                console.log('\n✅ SUCCESS!');
                console.log(`📄 PDF saved to: ${result.path}`);
                console.log(`📊 Source: ${result.source}`);
                process.exit(0);
            } else {
                console.error('\n❌ FAILED!');
                console.error(`Error: ${result.error}`);
                process.exit(1);
            }
        })
        .catch(error => {
            console.error('\n❌ FATAL ERROR!');
            console.error(error);
            process.exit(1);
        });
}

export default LibraryPDFRetriever;

