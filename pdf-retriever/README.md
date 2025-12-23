# Library PDF Retriever 📚

Automated PDF retrieval system using **university library access** via EZProxy. Retrieves full-text PDFs from research papers using DOI identifiers.

## Features

- ✅ **EZProxy Integration** - Works with any university library's EZProxy
- ✅ **Unpaywall Fallback** - Tries open access sources first (faster, no auth needed)
- ✅ **Batch Processing** - Handle hundreds of DOIs from CSV files
- ✅ **Smart Caching** - Skip already downloaded PDFs
- ✅ **Publisher Agnostic** - Works with Elsevier, Springer, Wiley, Nature, JAMA, etc.
- ✅ **Detailed Logging** - Track success/failure with timestamps
- ✅ **RIS Parser** - Parse RIS files from reference managers

## Installation

```bash
cd pdf-retriever
npm install
npm run install-browser  # Install Playwright Chromium
```

## Configuration

Configure your library credentials in the **root `.env` file**:

```bash
# In repository root, copy env.example to .env (if not already done)
cp ../env.example ../.env

# Edit the PDF RETRIEVER section:
EZPROXY_PREFIX=https://lib-ezproxy.youruniversity.edu/login?url=
LIBRARY_USERNAME=your_username
LIBRARY_PASSWORD=your_password
UNPAYWALL_EMAIL=your_email@example.com
PDF_OUTPUT_DIR=./downloads/pdf
```

### Finding Your EZProxy Prefix

1. Go to your university library's website
2. Access any database (e.g., PubMed, Google Scholar via library)
3. Look at the URL - it usually starts with something like:
   - `https://lib-ezproxy.university.edu/login?url=`
   - `https://ezproxy.library.edu/login?url=`

## Usage

### Single DOI Retrieval

```bash
# Basic usage
node library-retriever.js 10.1001/jama.2023.12345

# With custom filename
node library-retriever.js 10.1001/jama.2023.12345 my_study.pdf
```

### Batch Processing (CSV Input)

Prepare a CSV file with at least a `DOI` column:

```csv
DOI,Title,Year,Journal
10.1001/jama.2023.12345,"Effect of X on Y",2023,JAMA
10.1016/j.lancet.2023.01.001,"Trial of Z",2023,Lancet
```

Run batch retrieval:

```bash
# Process entire CSV
npm run batch your_studies.csv

# Process first 10 only (for testing)
node batch-retriever.js your_studies.csv 0 10

# Skip first 50, process next 25
node batch-retriever.js your_studies.csv 50 25
```

### Parse RIS Files

Convert RIS exports from reference managers to CSV:

```bash
npm run parse-ris your_export.ris
```

## Retrieval Strategy

The retriever tries sources in this order:

1. **Check cache** - Already downloaded?
2. **Unpaywall API** - Free open access? (~50% success rate)
3. **Library EZProxy** - Full institutional access (~95% success rate)

## Output

| File | Description |
|------|-------------|
| `pdf/*.pdf` | Downloaded PDF files |
| `reports/success_*.csv` | Successfully retrieved DOIs |
| `reports/failed_*.csv` | Failed retrievals (for retry) |
| `logs/combined.log` | Detailed operation log |

## Troubleshooting

### "Login failed" or "Authentication error"

- Verify credentials in `.env`
- Try logging into your library's EZProxy manually first
- Check if your account requires 2FA (may need manual intervention)

### "PDF download button not found"

- Some publishers have unusual layouts
- Try with `BROWSER_HEADLESS=false` to see what happens
- The script logs the publisher URL for manual inspection

### Browser crashes or hangs

- Increase timeout: `DOWNLOAD_TIMEOUT_MS=60000`
- Check system resources
- Try running fewer concurrent downloads

## Security Notes

- **Never commit `.env`** - Already in `.gitignore`
- Credentials are only used locally for browser automation
- No credentials are sent to external services
- PDFs are stored locally only

## License

MIT
