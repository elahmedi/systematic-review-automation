const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');
const { createObjectCsvWriter } = require('csv-writer');

// Load environment variables from global .env in repository root
require('dotenv').config({ path: path.join(__dirname, '..', '.env') });

/**
 * Covidence PDF Downloader
 * Automates downloading PDFs from Covidence study list
 * 
 * Usage:
 *   node covidence-pdf-downloader.js
 * 
 * Environment variables (set in root .env file):
 *   COVIDENCE_REVIEW_ID - Your Covidence review ID (e.g., 405558)
 *   COVIDENCE_DOWNLOAD_PATH - Directory to save PDFs (default: ./downloads)
 *   RESUME_FROM_STUDY - Study ID to resume from (e.g., #40132)
 */

// Configuration - customize these or use environment variables
const CONFIG = {
    // Headless mode: 'new' for headless, false for visible browser
    // Auto-detects VNC display for visible mode
    headless: process.env.DISPLAY && process.env.DISPLAY.includes(':1') ? false : 'new',
    
    // Delay between actions (milliseconds)
    delay: 1500,
    
    // Timeout for waiting for elements (milliseconds)
    timeout: 30000,
    
    // Directory to save PDFs - customize this path
    downloadPath: process.env.COVIDENCE_DOWNLOAD_PATH || path.join(__dirname, 'downloads'),
    
    // CSV file for external links
    csvPath: path.join(__dirname, 'external_links.csv'),
    
    // Log file
    logPath: path.join(__dirname, 'download_log.txt'),
    
    // Covidence Review ID - REPLACE WITH YOUR REVIEW ID
    // Find it in your Covidence URL: https://app.covidence.org/reviews/YOUR_ID
    covidenceReviewId: process.env.COVIDENCE_REVIEW_ID || 'YOUR_REVIEW_ID_HERE',
    
    // Resume from this study ID (set to null to start from beginning)
    // Example: '#40132'
    resumeFromStudyId: process.env.RESUME_FROM_STUDY || null,
};

// Construct Covidence URL from review ID
CONFIG.covidenceUrl = `https://app.covidence.org/reviews/${CONFIG.covidenceReviewId}`;
CONFIG.extractionUrl = `https://app.covidence.org/reviews/${CONFIG.covidenceReviewId}/extraction/index`;

// Logging function
function log(message, type = 'INFO') {
    const timestamp = new Date().toISOString();
    const logMessage = `[${timestamp}] [${type}] ${message}`;
    console.log(logMessage);
    
    // Append to log file
    fs.appendFileSync(CONFIG.logPath, logMessage + '\n');
}

// Create directories if they don't exist
if (!fs.existsSync(CONFIG.downloadPath)) {
    fs.mkdirSync(CONFIG.downloadPath, { recursive: true });
}

// Initialize CSV writer for external links
const csvWriter = createObjectCsvWriter({
    path: CONFIG.csvPath,
    header: [
        { id: 'studyId', title: 'Study ID' },
        { id: 'title', title: 'Title' },
        { id: 'link', title: 'External Link' },
        { id: 'timestamp', title: 'Timestamp' },
    ],
});

// Initialize CSV writer for studies with no PDF
const noPdfCsvPath = path.join(__dirname, 'no_pdf_available.csv');
const noPdfCsvWriter = createObjectCsvWriter({
    path: noPdfCsvPath,
    header: [
        { id: 'studyId', title: 'Study ID' },
        { id: 'title', title: 'Title' },
        { id: 'reason', title: 'Reason' },
        { id: 'timestamp', title: 'Timestamp' },
    ],
});

// Array to store external links
const externalLinks = [];

// Array to store studies with no PDF
const noPdfStudies = [];

async function wait(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

async function downloadPDF(pdfUrl, filename) {
    try {
        const filePath = path.join(CONFIG.downloadPath, filename);
        
        // Check if file already exists (skip for resume functionality)
        if (fs.existsSync(filePath)) {
            const stats = fs.statSync(filePath);
            if (stats.size > 0) {
                log(`⏭ Skipping (already exists): ${filename}`, 'INFO');
                return 'skipped';
            }
            // If file exists but is empty, delete and re-download
            fs.unlinkSync(filePath);
        }
        
        log(`Downloading: ${filename}`);
        
        // Use Node.js fetch/https to download the file directly
        const https = require('https');
        const http = require('http');
        
        return new Promise((resolve, reject) => {
            const protocol = pdfUrl.startsWith('https') ? https : http;
            
            const file = fs.createWriteStream(filePath);
            
            const request = protocol.get(pdfUrl, (response) => {
                // Handle redirects
                if (response.statusCode === 301 || response.statusCode === 302) {
                    file.close();
                    fs.unlinkSync(filePath);
                    downloadPDF(response.headers.location, filename)
                        .then(resolve)
                        .catch(reject);
                    return;
                }
                
                if (response.statusCode !== 200) {
                    file.close();
                    fs.unlinkSync(filePath);
                    reject(new Error(`HTTP ${response.statusCode}`));
                    return;
                }
                
                response.pipe(file);
                
                file.on('finish', () => {
                    file.close();
                    log(`✓ Successfully saved: ${filename}`, 'SUCCESS');
                    resolve(true);
                });
            });
            
            request.on('error', (err) => {
                file.close();
                fs.unlink(filePath, () => {}); // Delete incomplete file
                log(`✗ Download error: ${err.message}`, 'ERROR');
                reject(err);
            });
            
            request.setTimeout(CONFIG.timeout, () => {
                request.destroy();
                file.close();
                fs.unlink(filePath, () => {});
                reject(new Error('Download timeout'));
            });
        });
    } catch (error) {
        log(`✗ Failed to download ${filename}: ${error.message}`, 'ERROR');
        return false;
    }
}

async function login(page) {
    try {
        log('Navigating to Covidence review page...');
        await page.goto(CONFIG.covidenceUrl, {
            waitUntil: 'networkidle0',
        });
        
        await wait(CONFIG.delay * 2);
        
        // Check if we're on a login page
        const currentUrl = page.url();
        log(`Current URL: ${currentUrl}`);
        
        // Check if there's a login form on the page
        const hasLoginForm = await page.evaluate(() => {
            const emailInput = document.querySelector('input[type="email"], input[name*="email"], input[id*="email"]');
            const passwordInput = document.querySelector('input[type="password"]');
            const signInText = document.body.innerText.toLowerCase().includes('sign in') || 
                              document.body.innerText.toLowerCase().includes('log in');
            return !!(emailInput && passwordInput) || signInText;
        });
        
        const isLoginPage = currentUrl.includes('/users/sign_in') || 
                           currentUrl.includes('/login') || 
                           currentUrl.includes('sign_in') ||
                           hasLoginForm;
        
        if (!isLoginPage) {
            log('Already logged in, skipping login...');
            return true;
        }
        
        log(`Login page detected (URL: ${currentUrl}, hasLoginForm: ${hasLoginForm})`)
        
        log('');
        log('========================================', 'INFO');
        log('LOGIN REQUIRED - PLEASE LOG IN MANUALLY', 'WARNING');
        log('========================================', 'INFO');
        log('');
        log('Please enter your credentials in the browser window.');
        log('Press ENTER here once you have logged in successfully...');
        log('');
        
        // Wait for user to log in manually
        await new Promise((resolve) => {
            process.stdin.once('data', () => {
                resolve();
            });
        });
        
        log('Checking if login was successful...');
        await wait(CONFIG.delay);
        
        return true;
    } catch (error) {
        log(`Login failed: ${error.message}`, 'ERROR');
        log('Please check the login selectors or log in manually', 'WARNING');
        return false;
    }
}

// Load studies until we find the target study ID (for resuming)
async function loadUntilStudyFound(page, targetStudyId) {
    log(`Loading studies until we find: ${targetStudyId}...`);
    let loadMoreClicks = 0;
    
    while (loadMoreClicks < 200) { // Safety limit
        // Check if target study is on the page
        const found = await page.evaluate((targetId) => {
            const articles = document.querySelectorAll('article[aria-labelledby^="study-"]');
            for (const article of articles) {
                const identifierEl = article.querySelector('[id^="study-"]');
                if (identifierEl) {
                    const studyId = identifierEl.textContent.trim();
                    if (studyId.includes(targetId)) {
                        return true;
                    }
                }
            }
            return false;
        }, targetStudyId);
        
        if (found) {
            const articleCount = await page.$$eval('article[aria-labelledby^="study-"]', a => a.length);
            log(`✓ Found target study ${targetStudyId} after ${loadMoreClicks} "Load more" clicks (${articleCount} studies loaded)`);
            return true;
        }
        
        // Scroll to bottom to ensure "Load more" button is visible
        await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
        await wait(300);
        
        // Find "Load more" button
        const loadMoreButton = await page.evaluateHandle(() => {
            const buttons = Array.from(document.querySelectorAll('button'));
            for (const btn of buttons) {
                const text = btn.textContent.trim().toLowerCase();
                if (text.includes('load more')) {
                    return btn;
                }
            }
            return null;
        });
        
        const buttonExists = await page.evaluate(btn => btn !== null, loadMoreButton);
        
        if (!buttonExists) {
            log(`⚠ No more "Load more" button found. Target study ${targetStudyId} may not exist.`, 'WARNING');
            return false;
        }
        
        loadMoreClicks++;
        const articleCount = await page.$$eval('article[aria-labelledby^="study-"]', a => a.length);
        log(`  [Load more #${loadMoreClicks}] ${articleCount} studies loaded, searching for ${targetStudyId}...`);
        
        try {
            await loadMoreButton.click();
            await wait(2000);
        } catch (clickError) {
            log(`Could not click Load more: ${clickError.message}`, 'WARNING');
            return false;
        }
    }
    
    log(`⚠ Reached safety limit of ${loadMoreClicks} clicks. Target study not found.`, 'WARNING');
    return false;
}

async function extractPDFLink(page, articleElement) {
    try {
        // Look for PDF link in the expanded article
        const pdfData = await page.evaluate((article) => {
            const links = Array.from(article.querySelectorAll('a[href]'));
            
            for (const link of links) {
                const href = link.getAttribute('href');
                const className = link.getAttribute('class') || '';
                const linkText = link.textContent.trim();
                
                // Check if it's an AWS S3 PDF link
                if (href && (href.includes('s3.amazonaws.com') || href.includes('.pdf'))) {
                    const decodedHref = href
                        .replace(/&amp;/g, '&')
                        .replace(/&lt;/g, '<')
                        .replace(/&gt;/g, '>');
                    
                    return {
                        type: 'pdf',
                        url: decodedHref,
                        text: linkText,
                    };
                }
                
                // Check if it's an external reference link
                if (className.includes('referenceLink') || className.includes('reference')) {
                    const decodedHref = href
                        .replace(/&amp;/g, '&')
                        .replace(/&lt;/g, '<')
                        .replace(/&gt;/g, '>');
                    
                    return {
                        type: 'external',
                        url: decodedHref,
                        text: linkText,
                    };
                }
            }
            
            return null;
        }, articleElement);
        
        return pdfData;
    } catch (error) {
        log(`Error extracting PDF link: ${error.message}`, 'ERROR');
        return null;
    }
}

async function downloadAllPDFs() {
    // Validate configuration
    if (CONFIG.covidenceReviewId === 'YOUR_REVIEW_ID_HERE') {
        console.error('\n❌ ERROR: Please set your Covidence Review ID!');
        console.error('');
        console.error('Option 1: Set environment variable:');
        console.error('  export COVIDENCE_REVIEW_ID=your_review_id');
        console.error('');
        console.error('Option 2: Edit CONFIG.covidenceReviewId in this file');
        console.error('');
        console.error('Find your Review ID in your Covidence URL:');
        console.error('  https://app.covidence.org/reviews/YOUR_ID');
        console.error('');
        process.exit(1);
    }
    
    const browser = await puppeteer.launch({
        headless: CONFIG.headless,
        defaultViewport: { width: 1920, height: 1080 },
        args: [
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-dev-shm-usage',
            '--disable-accelerated-2d-canvas',
            '--disable-gpu',
            '--window-size=1920,1080',
        ],
    });
    
    const page = await browser.newPage();
    
    try {
        // Initialize log file
        log('=== Covidence PDF Downloader Started ===');
        log(`Review ID: ${CONFIG.covidenceReviewId}`);
        log(`Download directory: ${CONFIG.downloadPath}`);
        log(`CSV file: ${CONFIG.csvPath}`);
        
        // Login (will navigate to review page)
        const loginSuccess = await login(page);
        if (!loginSuccess) {
            log('Login failed. Please check credentials or log in manually.', 'ERROR');
            log(`Current page URL: ${page.url()}`, 'INFO');
            log('Waiting 10 seconds for you to manually log in, then press Enter to continue...', 'WARNING');
            await wait(10000);
            await new Promise((resolve) => {
                process.stdin.once('data', () => {
                    resolve();
                });
            });
            
            // Verify we're logged in after manual intervention
            const currentUrl = page.url();
            const stillOnLogin = currentUrl.includes('/users/sign_in') || currentUrl.includes('/login');
            if (stillOnLogin) {
                log('Still on login page. Please log in manually in the browser.', 'ERROR');
                log('Press Enter once you have logged in and navigated to the study list...');
                await new Promise((resolve) => {
                    process.stdin.once('data', () => {
                        resolve();
                    });
                });
            }
        }
        
        // Navigate to extraction/index page (study list)
        log('Navigating to study list (extraction/index)...');
        await page.goto(CONFIG.extractionUrl, {
            waitUntil: 'networkidle0',
        });
        
        await wait(CONFIG.delay * 2);
        
        // Verify we're actually on the extraction page
        const finalUrl = page.url();
        if (finalUrl.includes('/users/sign_in') || finalUrl.includes('/login')) {
            log('ERROR: Redirected to login page. Authentication failed!', 'ERROR');
            log('Please log in manually and restart the script.', 'ERROR');
            await browser.close();
            return;
        }
        
        // Check if we can see study articles
        const hasStudies = await page.$('article[aria-labelledby^="study-"]');
        if (!hasStudies) {
            log('WARNING: No study articles found. Make sure you are on the extraction/index page.', 'WARNING');
            log('Current URL:', finalUrl, 'INFO');
        }
        
        let successCount = 0;
        let failCount = 0;
        let skippedCount = 0;
        let skippedExisting = 0;
        let totalProcessed = 0;
        let batchNumber = 0;
        let crashRecovery = false;
        const processedStudyIds = new Set();
        let foundResumePoint = !CONFIG.resumeFromStudyId;
        let resumeStudyIndex = -1;
        let lastProcessedIndex = -1;
        
        // If we have a resume point, load studies until we find it
        if (CONFIG.resumeFromStudyId) {
            log(`\n${'='.repeat(50)}`);
            log(`🔄 RESUME MODE: Looking for study ${CONFIG.resumeFromStudyId}`);
            log(`${'='.repeat(50)}`);
            const found = await loadUntilStudyFound(page, CONFIG.resumeFromStudyId);
            if (!found) {
                log('Could not find resume point. Do you want to continue from the beginning? (Press Enter to continue or Ctrl+C to exit)', 'WARNING');
                await new Promise((resolve) => {
                    process.stdin.once('data', () => resolve());
                });
                foundResumePoint = true;
            } else {
                // Get ALL study IDs in a single page.evaluate call
                const allStudyIds = await page.evaluate((targetId) => {
                    const articles = document.querySelectorAll('article[aria-labelledby^="study-"]');
                    const ids = [];
                    let targetIndex = -1;
                    
                    for (let i = 0; i < articles.length; i++) {
                        const el = articles[i].querySelector('[id^="study-"]');
                        const studyId = el ? el.textContent.trim() : `unknown-${i}`;
                        ids.push(studyId);
                        
                        if (targetIndex === -1 && studyId.includes(targetId)) {
                            targetIndex = i;
                        }
                    }
                    
                    return { ids, targetIndex };
                }, CONFIG.resumeFromStudyId);
                
                resumeStudyIndex = allStudyIds.targetIndex;
                
                if (resumeStudyIndex >= 0) {
                    log(`Found resume point at index ${resumeStudyIndex} (${allStudyIds.ids[resumeStudyIndex]})`);
                    
                    // Mark all studies before the resume point as already processed
                    log(`Marking ${resumeStudyIndex} studies before resume point as processed...`);
                    for (let i = 0; i < resumeStudyIndex; i++) {
                        processedStudyIds.add(allStudyIds.ids[i]);
                    }
                    lastProcessedIndex = resumeStudyIndex - 1;
                    log(`Skipped indices 0-${resumeStudyIndex - 1} (${processedStudyIds.size} unique IDs). Starting at index ${resumeStudyIndex}...`);
                    foundResumePoint = true;
                } else {
                    log(`Could not find resume point ${CONFIG.resumeFromStudyId} in loaded studies`, 'WARNING');
                }
            }
        }
        
        // Main loop: process current batch, then load more
        while (true) {
            if (crashRecovery) {
                log(`Crash recovery complete. Continuing from index ${lastProcessedIndex + 1}...`);
                crashRecovery = false;
            }
            
            batchNumber++;
            const batchStartTime = Date.now();
            log(`\n${'='.repeat(50)}`);
            log(`=== Processing Batch ${batchNumber} === [${new Date().toLocaleTimeString()}]`);
            log(`${'='.repeat(50)}`);
            
            // Find all study articles currently on page
            const articles = await page.$$('article[aria-labelledby^="study-"]');
            const totalOnPage = articles.length;
            const startFrom = lastProcessedIndex + 1;
            const toProcess = totalOnPage - startFrom;
            log(`📊 Total on page: ${totalOnPage} | Last index: ${lastProcessedIndex} | Starting at: ${startFrom} | To process: ${toProcess}`);
            
            if (totalOnPage === 0 && batchNumber === 1) {
                log('No study articles found. You may need to log in.', 'WARNING');
                log('');
                log('Please log in manually in the browser window if needed.');
                log('Then navigate to: ' + CONFIG.covidenceUrl);
                log('Press ENTER here once you can see the study articles...');
                log('');
                
                await new Promise((resolve) => {
                    process.stdin.once('data', () => {
                        resolve();
                    });
                });
                
                log('Checking for study articles again...');
                await wait(CONFIG.delay);
                
                const retryArticles = await page.$$('article[aria-labelledby^="study-"]');
                if (retryArticles.length === 0) {
                    log('Still no study articles found. Please check the page manually.', 'ERROR');
                    log('Press ENTER to close the browser...');
                    await new Promise((resolve) => {
                        process.stdin.once('data', () => {
                            resolve();
                        });
                    });
                    await browser.close();
                    return;
                }
                
                log(`Found ${retryArticles.length} study articles after login!`);
                continue;
            }
            
            let newStudiesProcessed = 0;
            
            // Loop through only NEW articles
            for (let i = startFrom; i < totalOnPage; i++) {
            try {
                // Re-find articles (DOM might have changed)
                const currentArticles = await page.$$('article[aria-labelledby^="study-"]');
                if (!currentArticles[i]) {
                    log(`Article ${i + 1} not found, skipping...`, 'WARNING');
                    skippedCount++;
                    continue;
                }
                
                const articleElement = currentArticles[i];
                
                // Get study info
                const studyInfo = await page.evaluate((article) => {
                    const identifierEl = article.querySelector('[id^="study-"]');
                    const titleEl = article.querySelector('h2');
                    
                    return {
                        id: identifierEl ? identifierEl.textContent.trim() : `study-${Date.now()}`,
                        title: titleEl ? titleEl.textContent.trim() : 'unknown',
                    };
                }, articleElement);
                
                // Skip if we've already processed this study ID
                if (processedStudyIds.has(studyInfo.id)) {
                    lastProcessedIndex = i;
                    continue;
                }
                processedStudyIds.add(studyInfo.id);
                lastProcessedIndex = i;
                
                totalProcessed++;
                newStudiesProcessed++;
                
                const progressPct = ((i - startFrom + 1) / (totalOnPage - startFrom) * 100).toFixed(1);
                log(`\n[${totalProcessed}] (${progressPct}% of batch) ${studyInfo.id} - ${studyInfo.title.substring(0, 50)}...`);
                
                // Check if "View full text" button exists
                const buttonInfo = await page.evaluate((article) => {
                    const buttons = Array.from(article.querySelectorAll('button'));
                    for (const btn of buttons) {
                        const text = btn.textContent.trim();
                        if (text.includes('View full text')) {
                            const ariaExpanded = btn.getAttribute('aria-expanded');
                            return {
                                exists: true,
                                isExpanded: ariaExpanded === 'true',
                            };
                        }
                    }
                    return { exists: false, isExpanded: false };
                }, articleElement);
                
                if (!buttonInfo.exists) {
                    log(`  ⚠ No "View full text" button found, skipping...`, 'WARNING');
                    noPdfStudies.push({
                        studyId: studyInfo.id,
                        title: studyInfo.title,
                        reason: 'No "View full text" button',
                        timestamp: new Date().toISOString(),
                    });
                    skippedCount++;
                    continue;
                }
                
                if (buttonInfo.isExpanded) {
                    log(`  📂 Already expanded, extracting link...`);
                } else {
                    // Find and click the "View full text" button
                    const button = await page.evaluateHandle((article) => {
                        const buttons = Array.from(article.querySelectorAll('button'));
                        for (const btn of buttons) {
                            const text = btn.textContent.trim();
                            if (text.includes('View full text')) {
                                const ariaExpanded = btn.getAttribute('aria-expanded');
                                if (ariaExpanded === 'false') {
                                    return btn;
                                }
                            }
                        }
                        return null;
                    }, articleElement);
                    
                    if (button) {
                        log(`  🖱️ Clicking "View full text"...`);
                        await button.click();
                        await wait(1000);
                    }
                }
                
                // Extract PDF link
                const pdfData = await extractPDFLink(page, articleElement);
                
                if (!pdfData) {
                    log(`  ⚠ No PDF link found`, 'WARNING');
                    noPdfStudies.push({
                        studyId: studyInfo.id,
                        title: studyInfo.title,
                        reason: 'No PDF link in expanded section',
                        timestamp: new Date().toISOString(),
                    });
                    skippedCount++;
                    continue;
                }
                
                if (pdfData.type === 'pdf') {
                    // Download PDF
                    const safeTitle = studyInfo.title.replace(/[^a-z0-9]/gi, '_').toLowerCase().substring(0, 100);
                    const safeId = studyInfo.id.replace(/[^a-z0-9]/gi, '_');
                    const filename = `${safeId}_${safeTitle}.pdf`;
                    
                    const downloaded = await downloadPDF(pdfData.url, filename);
                    
                    if (downloaded === 'skipped') {
                        skippedExisting++;
                    } else if (downloaded) {
                        successCount++;
                    } else {
                        failCount++;
                    }
                } else if (pdfData.type === 'external') {
                    // Log external link to CSV
                    log(`  External link found: ${pdfData.url}`, 'INFO');
                    externalLinks.push({
                        studyId: studyInfo.id,
                        title: studyInfo.title,
                        link: pdfData.url,
                        timestamp: new Date().toISOString(),
                    });
                    skippedCount++;
                }
                
            } catch (error) {
                log(`  ✗ Error processing study ${i + 1}: ${error.message}`, 'ERROR');
                failCount++;
                
                // Detect browser crash or timeout
                const isCrash = error.message.includes('crashed') || 
                               error.message.includes('timed out') ||
                               error.message.includes('Target closed') ||
                               error.message.includes('Session closed') ||
                               error.message.includes('Protocol error');
                
                if (isCrash) {
                    log('');
                    log('==========================================', 'WARNING');
                    log('BROWSER CRASH/TIMEOUT DETECTED - RECOVERING...', 'WARNING');
                    log('==========================================', 'WARNING');
                    log('');
                    
                    // Auto-recover
                    log('Navigating back to Covidence extraction page...');
                    try {
                        await page.goto(CONFIG.extractionUrl, { 
                            waitUntil: 'networkidle0', 
                            timeout: 60000 
                        });
                        await wait(2000);
                        
                        // Check if we got redirected to login page
                        const currentUrl = page.url();
                        if (currentUrl.includes('/sign_in') || currentUrl.includes('/login')) {
                            log('⚠️ Session expired - redirected to login page!', 'WARNING');
                            log('Please log in manually in the browser, then press ENTER to continue...');
                            await new Promise((resolve) => {
                                process.stdin.once('data', () => resolve());
                            });
                            await page.goto(CONFIG.extractionUrl, {
                                waitUntil: 'networkidle0',
                                timeout: 60000
                            });
                            await wait(2000);
                        }
                        
                        // Verify we're on the extraction page with studies
                        const studiesOnPage = await page.$$('article[aria-labelledby^="study-"]');
                        if (studiesOnPage.length === 0) {
                            log('⚠️ No studies found after recovery. May need to log in again.', 'WARNING');
                            log('Please check the browser and press ENTER when ready...');
                            await new Promise((resolve) => {
                                process.stdin.once('data', () => resolve());
                            });
                        }
                        
                        // Click "Load more" until we have enough studies to resume
                        const targetCount = lastProcessedIndex + 50;
                        log(`Loading studies until we have at least ${targetCount}...`);
                        
                        let loadMoreClicks = 0;
                        while (true) {
                            const currentCount = await page.$$eval(
                                'article[aria-labelledby^="study-"]', 
                                articles => articles.length
                            );
                            
                            if (currentCount >= targetCount) {
                                log(`  Reached ${currentCount} studies - enough to resume.`);
                                break;
                            }
                            
                            const loadMoreBtn = await page.evaluateHandle(() => {
                                const buttons = Array.from(document.querySelectorAll('button'));
                                for (const btn of buttons) {
                                    if (btn.textContent.trim().toLowerCase().includes('load more')) {
                                        return btn;
                                    }
                                }
                                return null;
                            });
                            
                            const hasMore = await page.evaluate(btn => btn !== null, loadMoreBtn);
                            if (!hasMore) {
                                log(`  No more "Load more" button - all ${currentCount} studies loaded.`);
                                break;
                            }
                            
                            await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
                            await wait(300);
                            
                            await loadMoreBtn.click();
                            loadMoreClicks++;
                            log(`  Clicked "Load more" (${loadMoreClicks}) - ${currentCount} studies so far...`);
                            await wait(2000);
                        }
                        
                        log(`Recovery complete after ${loadMoreClicks} clicks.`);
                        crashRecovery = true;
                        break;
                        
                    } catch (recoveryError) {
                        log(`Auto-recovery failed: ${recoveryError.message}`, 'ERROR');
                        log('Please manually reload the page and press ENTER to continue...', 'WARNING');
                        await new Promise((resolve) => {
                            process.stdin.once('data', () => resolve());
                        });
                        crashRecovery = true;
                        break;
                    }
                }
            }
            
            // Small delay between studies
            await wait(500);
        }
        
        const batchDuration = ((Date.now() - batchStartTime) / 1000).toFixed(1);
        const avgPerStudy = newStudiesProcessed > 0 ? ((Date.now() - batchStartTime) / newStudiesProcessed / 1000).toFixed(2) : 0;
        log(`\n✅ Batch ${batchNumber} complete: ${newStudiesProcessed} studies in ${batchDuration}s (${avgPerStudy}s per study)`);
        
        // Scroll to bottom to ensure "Load more" button is visible
        await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
        await wait(500);
        
        // Check if there's a "Load more" button
        log(`\n🔍 Checking for "Load more" button...`);
        const loadMoreButton = await page.evaluateHandle(() => {
            const buttons = Array.from(document.querySelectorAll('button'));
            for (const btn of buttons) {
                const text = btn.textContent.trim().toLowerCase();
                if (text.includes('load more')) {
                    return btn;
                }
            }
            return null;
        });
        
        const hasMoreStudies = await page.evaluate(btn => btn !== null, loadMoreButton);
        
        if (hasMoreStudies) {
            log('Found "Load more" button - clicking to load more studies...');
            try {
                await loadMoreButton.click();
                await wait(2000);
            } catch (clickError) {
                log(`Error clicking Load more: ${clickError.message}`, 'WARNING');
                break;
            }
        } else {
            log('No "Load more" button found - all studies have been loaded');
            break;
        }
        
        } // End of while loop
        
        log(`\n=== All batches complete ===`);
        log(`Total studies processed: ${totalProcessed}`);
        
        // Write external links to CSV
        if (externalLinks.length > 0) {
            log(`\nWriting ${externalLinks.length} external links to CSV...`);
            await csvWriter.writeRecords(externalLinks);
            log(`External links saved to: ${CONFIG.csvPath}`);
        }
        
        // Write "no PDF" studies to CSV
        if (noPdfStudies.length > 0) {
            log(`\nWriting ${noPdfStudies.length} studies with no PDF to CSV...`);
            await noPdfCsvWriter.writeRecords(noPdfStudies);
            log(`No-PDF studies saved to: ${noPdfCsvPath}`);
        }
        
        // Summary
        log('\n=== Download Complete ===');
        log(`✓ Successfully downloaded: ${successCount}`);
        log(`⏭ Skipped (already existed): ${skippedExisting}`);
        log(`⚠ External links (saved to CSV): ${externalLinks.length}`);
        log(`✗ Failed: ${failCount}`);
        log(`⊘ Skipped (no PDF available): ${skippedCount}`);
        log(`\nPDFs saved to: ${CONFIG.downloadPath}`);
        log(`Log file: ${CONFIG.logPath}`);
        
    } catch (error) {
        log(`Fatal error: ${error.message}`, 'ERROR');
        console.error(error);
    } finally {
        log('\nPress Enter to close the browser...');
        await new Promise((resolve) => {
            process.stdin.once('data', () => {
                resolve();
            });
        });
        await browser.close();
    }
}

// Run the script
if (require.main === module) {
    downloadAllPDFs().catch((error) => {
        log(`Unhandled error: ${error.message}`, 'ERROR');
        console.error(error);
        process.exit(1);
    });
}

module.exports = { downloadAllPDFs };

