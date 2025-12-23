# Covidence PDF Downloader 📚

Automates downloading PDFs from your Covidence systematic review study list.

## Features

- ✅ **Automatic PDF extraction** from Covidence study entries
- ✅ **Resume functionality** - continue from where you left off
- ✅ **External link tracking** - saves non-downloadable links to CSV
- ✅ **Crash recovery** - automatically recovers from browser crashes
- ✅ **Progress logging** - detailed logs with timestamps

## Installation

```bash
cd covidence-downloader
npm install
```

## Configuration

Configure your Covidence Review ID in the **root `.env` file**:

```bash
# In repository root, copy env.example to .env
cp ../env.example ../.env

# Edit the COVIDENCE section:
COVIDENCE_REVIEW_ID=405558  # Find in your URL: https://app.covidence.org/reviews/YOUR_ID
COVIDENCE_DOWNLOAD_PATH=./downloads/covidence
```

## Usage

```bash
# Start the downloader
npm start

# Or directly
node covidence-pdf-downloader.js
```

### What Happens

1. Browser opens and navigates to your Covidence review
2. **You log in manually** (the script waits for you)
3. Press Enter after logging in
4. Script automatically downloads all PDFs

### Resume After Interruption

If the script stops midway, you can resume:

```bash
# Set the study ID to resume from in .env
RESUME_FROM_STUDY=#40132
```

## Output

| File | Description |
|------|-------------|
| `downloads/*.pdf` | Downloaded PDF files |
| `external_links.csv` | Studies with external links (not downloadable) |
| `no_pdf_available.csv` | Studies without PDF attachments |
| `download_log.txt` | Detailed operation log |

## Requirements

- Node.js 18+
- Covidence account with review access
- Display server (for non-headless operation) or run headless

## Headless Operation

For server environments without display:

```bash
# The script auto-detects headless mode
# Or force headless in the CONFIG object:
headless: 'new'
```

## Troubleshooting

### "No study articles found"
- Ensure you're logged in to Covidence
- Check that the Review ID is correct
- Navigate to the extraction page manually

### Browser crashes
- The script has automatic crash recovery
- It will reload the page and resume from where it left off

### Session timeout
- Long downloads may cause session expiry
- The script will prompt you to log in again

## License

MIT

