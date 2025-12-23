# RCT Data Extractor 🔬

Automated data extraction from Randomized Controlled Trial (RCT) PDFs using **Azure AI Content Understanding**.

## Features

- ✅ **AI-Powered Extraction** - Uses Azure Content Understanding to extract structured data
- ✅ **65+ Data Fields** - Comprehensive RCT characteristics extraction
- ✅ **Batch Processing** - Process entire folders of PDFs
- ✅ **CSV Output** - Clean, analysis-ready CSV files
- ✅ **Demographics Handling** - Separate handling for complex demographic data
- ✅ **Progress Tracking** - Detailed logs and error reports
- ✅ **Resumable** - Skip already-processed files

## Extracted Fields

The extractor captures key RCT characteristics including:

| Category | Fields |
|----------|--------|
| **Publication** | Title, Journal, Year, Authors, Funding |
| **Study Design** | Type, Phase, Blinding, Randomization |
| **Population** | Sample size, Age, Sex, Target group |
| **Intervention** | Type, Name, Comparator, Domain |
| **Outcomes** | Primary outcomes, Statistical type, Power |
| **Results** | Effect size, P-values, ITT/PP analysis |

See `field-schema.json` for the complete schema.

## Prerequisites

1. **Azure Account** with Content Understanding resource
2. **Custom Analyzer** created in Azure AI Studio with the RCT field schema

### Setting Up Azure Content Understanding

1. Go to [Azure AI Studio](https://ai.azure.com)
2. Create a Content Understanding resource
3. Create a custom analyzer with the fields from `field-schema.json`
4. Note your:
   - Endpoint URL
   - API Key
   - Analyzer ID

## Installation

```bash
cd rct-extractor
npm install
```

## Configuration

Configure your Azure credentials in the **root `.env` file**:

```bash
# In repository root, copy env.example to .env (if not already done)
cp ../env.example ../.env

# Edit the RCT EXTRACTOR section:
AZURE_CONTENT_UNDERSTANDING_ENDPOINT=https://your-resource.cognitiveservices.azure.com/
AZURE_CONTENT_UNDERSTANDING_SUBSCRIPTION_KEY=your_api_key
AZURE_CONTENT_UNDERSTANDING_API_VERSION=2025-05-01-preview
AZURE_CONTENT_UNDERSTANDING_ANALYZER_ID=your_analyzer_id
```

## Usage

### Extract from a folder of PDFs

```bash
# Basic usage
node extract-rct.js --folder=/path/to/pdfs

# With custom output directory
node extract-rct.js --folder=/path/to/pdfs --output=/path/to/output
```

### Output Files

| File | Description |
|------|-------------|
| `rct_extraction.csv` | Main extraction results |
| `rct_extraction_demographics.csv` | Demographic data (age/sex by group) |
| `error_report.json` | Failed extractions with error details |

## Field Schema

The analyzer uses a comprehensive schema for RCT data. Key field types:

- **Extract**: Direct extraction from text (e.g., title, journal name)
- **Generate**: AI-generated answers (e.g., funding status, outcomes)
- **Classify**: Categorization into predefined options (e.g., study phase, therapeutic area)

### Customizing the Schema

To modify extracted fields:

1. Edit `field-schema.json`
2. Update your Azure analyzer with the new schema
3. The extraction script will automatically use the updated fields

## Cost Considerations

Azure Content Understanding charges per document analyzed. For large systematic reviews:

- Test on a small batch first (10-20 PDFs)
- Monitor your Azure spending
- Consider processing in batches

## Troubleshooting

### "Analysis failed" errors

- Check Azure resource quotas
- Verify API key and endpoint
- Some PDFs may be scanned images (OCR quality issues)

### Missing fields

- The AI extracts what it finds - some fields may be empty
- Check the source PDF for the expected information
- Review confidence scores in the output

### Timeout errors

- Large PDFs take longer to process
- Increase `TIMEOUT_SECONDS` in `.env`
- Default is 3600 seconds (1 hour)

## Integration with Other Modules

This extractor works best as part of the full pipeline:

```bash
# 1. Download PDFs from Covidence
cd ../covidence-downloader && npm start

# 2. Retrieve missing PDFs via library access
cd ../pdf-retriever && npm run batch missing_dois.csv

# 3. Extract RCT data
cd ../rct-extractor && node extract-rct.js --folder=../pdf

# 4. Assess risk of bias
cd ../risk-of-bias && risk-of-bias analyse ../pdf/
```

## License

MIT

