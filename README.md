# Systematic Review Automation 🔬📚

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Node.js](https://img.shields.io/badge/Node.js-18%2B-green)](https://nodejs.org/)
[![Python](https://img.shields.io/badge/Python-3.12%2B-blue)](https://python.org/)

**A comprehensive toolkit for automating systematic review workflows** — from PDF retrieval to structured data extraction and risk of bias assessment.

---

## Important Disclaimer: AI augments human expertise — it doesn't replace the learning journey that makes you a better *researcher.*rio


Systematic reviews serve a dual purpose: advancing scientific knowledge and developing researcher expertise. For Master's and PhD students, conducting systematic reviews is a formative learning experience — developing critical appraisal skills, deep familiarity with a research domain, and rigorous methodology that cannot be replicated by automation alone.

**This toolkit is not a replacement for human judgment.** The established gold standard for systematic reviews — two independent human reviewers with a third for adjudication — remains paramount for rigorous assessment. This standard exists because:

- Human reviewers develop contextual understanding that AI cannot fully replicate
- The review process itself builds essential research competencies
- Critical thinking about evidence quality requires human expertise

**Where this toolkit fits:**

This toolkit offers an effective way to **externally validate, update, and augment** systematic reviews, particularly those:
- Submitted for publication and requiring quality assurance
- Informing clinical guidelines, policy decisions, or public health recommendations
- Being updated with new literature after initial publication

Recognizing that both human reviewers and AI systems carry inherent biases, incorporating AI perspectives can offer a complementary lens through which to evaluate studies. In resource-constrained settings where the full gold standard is difficult to achieve, AI tools can provide valuable support — elevating consistency and thoroughness while the field progresses toward universally ideal practices.

**Use AI to enhance your review process, not to shortcut the learning that makes you a better researcher.**

---

## 🎯 What This Does

Systematic reviews require processing hundreds of research papers. This toolkit automates the tedious parts while preserving human oversight:

| Step | Manual Time | With This Toolkit |
|------|-------------|-------------------|
| Download PDFs from Covidence | Hours | Minutes |
| Retrieve missing PDFs via DOI | Days | Hours |
| Extract study characteristics | Weeks | Hours |
| Risk of bias assessment | Days | Minutes |

---

## 📋 Prerequisites

Before you begin, you'll need:

### Required
- **RIS file** — An export of your included studies from your reference manager (EndNote, Zotero, Mendeley) or Covidence. This is how the system knows which papers to retrieve.
- **Node.js 18+** — For PDF retrieval and data extraction modules
- **Python 3.12+** — For risk of bias assessment

### For Full Functionality
- **Covidence account** — If downloading PDFs directly from Covidence
- **University library access** — For retrieving paywalled PDFs via EZProxy
- **Azure account** — For AI-powered data extraction ([free tier available](https://azure.microsoft.com/free/))
- **OpenAI API key** — For risk of bias assessment ([usage-based pricing](https://openai.com/pricing))

---

## 📦 Modules

### 1. [Covidence Downloader](./covidence-downloader/)
Automatically download PDFs from your Covidence systematic review.

### 2. [PDF Retriever](./pdf-retriever/)
Retrieve PDFs using DOIs via your university library's EZProxy access + Unpaywall for open access.

### 3. [RCT Extractor](./rct-extractor/)
Extract structured data from PDFs using Azure AI Content Understanding with your custom JSON schema.

### 4. [Risk of Bias](./risk-of-bias/)
AI-powered risk of bias assessment using the RoB 2 framework.

> **Note:** The Risk of Bias module is a fork of [rob-luke/risk-of-bias](https://github.com/rob-luke/risk-of-bias) by **Robert Luke**. Full credit goes to the original author for creating this excellent tool for AI-enabled RoB 2 assessment.

---

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/systematic-review-automation.git
cd systematic-review-automation

# Copy and configure environment file
cp env.example .env
# Edit .env with your credentials (see Configuration section)

# Install Node.js modules
cd covidence-downloader && npm install && cd ..
cd pdf-retriever && npm install && npm run install-browser && cd ..
cd rct-extractor && npm install && cd ..

# Install Python module
cd risk-of-bias && pip install -e ".[all]" && cd ..
```

### Configuration

All modules read from a single `.env` file in the repository root. Copy `env.example` to `.env` and fill in your credentials:

```bash
# Required for PDF retrieval
EZPROXY_PREFIX=https://lib-ezproxy.youruniversity.edu/login?url=
LIBRARY_USERNAME=your_username
LIBRARY_PASSWORD=your_password
UNPAYWALL_EMAIL=your_email@example.com

# Required for data extraction
AZURE_CONTENT_UNDERSTANDING_ENDPOINT=https://your-resource.cognitiveservices.azure.com/
AZURE_CONTENT_UNDERSTANDING_SUBSCRIPTION_KEY=your_key
AZURE_CONTENT_UNDERSTANDING_ANALYZER_ID=your_analyzer_id

# Required for risk of bias
OPENAI_API_KEY=sk-your-key
```

---

## 📚 Complete Workflow: From RIS File to Extracted Data

Here's how to use this toolkit for a complete systematic review workflow:

### Step 1: Export Your Included Studies

Export your included studies from your reference manager or Covidence as a **RIS file** (`.ris`). This file contains the bibliographic information including DOIs that the retriever needs.

```
# Example: Export from Covidence or your reference manager
# Save as: my_systematic_review.ris
```

### Step 2: Parse RIS to CSV

Convert your RIS file to a CSV with DOIs:

```bash
cd pdf-retriever
node ris-parser.js ../my_systematic_review.ris
# Output: my_systematic_review_parsed.csv
```

### Step 3: Retrieve PDFs

The retriever will try Unpaywall first (free, open access) then fall back to your library:

```bash
npm run batch ../my_systematic_review_parsed.csv
# Output: 
#   ./pdf/*.pdf (downloaded PDFs)
#   ./reports/success_*.csv (successful retrievals)
#   ./reports/failed_*.csv (failed - may need manual retrieval)
```

### Step 4: Extract Structured Data

Define what data you want to extract in a JSON schema (see `rct-extractor/field-schema.json` for an example with 65+ RCT fields), then run:

```bash
cd ../rct-extractor

# View available options
node extract-rct.js --help

# Run extraction with your schema
node extract-rct.js --folder=../pdf-retriever/pdf --schema=./field-schema.json
# Output: ./output/extraction_*/rct_extraction.csv
```

### Step 5: Assess Risk of Bias

Run AI-powered RoB 2 assessment on your PDFs:

```bash
cd ../risk-of-bias
risk-of-bias analyse ../pdf-retriever/pdf/
# Output: JSON, HTML, and Markdown reports for each study
```

### Step 6: Review and Validate

**Critical step:** Review the AI-generated extractions and assessments. The AI provides a starting point and external validation, but human judgment remains essential for:

- Verifying extracted data accuracy
- Resolving ambiguous cases
- Making final risk of bias judgments
- Ensuring clinical/methodological context is properly interpreted

---

## 🔧 Customizing Data Extraction

The RCT Extractor uses a JSON schema to define what fields to extract. You can:

1. **Use the provided schema** — `field-schema.json` includes 65+ fields specific to RCTs
2. **Create your own schema** — Define custom fields for your review type

### Schema Structure

```json
{
  "fieldSchema": {
    "fields": {
      "title": {
        "type": "string",
        "method": "extract",
        "description": "The exact title of the research paper"
      },
      "sampleSize": {
        "type": "integer",
        "method": "generate",
        "description": "Total number of participants"
      },
      "studyDesign": {
        "type": "string",
        "method": "classify",
        "description": "Type of study design",
        "enum": ["RCT", "Cohort", "Case-Control", "Cross-sectional"],
        "enumDescriptions": {
          "RCT": "Randomized controlled trial",
          "Cohort": "Prospective or retrospective cohort study"
        }
      }
    }
  }
}
```

**Field methods:**
- `extract` — Direct extraction from text
- `generate` — AI-generated based on content analysis
- `classify` — Categorization into predefined options

---

## 💰 Cost Considerations

| Service | Cost | Notes |
|---------|------|-------|
| Covidence | Your subscription | No additional API costs |
| Library EZProxy | Free | Uses your institutional access |
| Unpaywall | Free | Open access lookup |
| Azure Content Understanding | ~$0.01-0.05/page | [Pricing](https://azure.microsoft.com/pricing/details/ai-document-intelligence/) |
| OpenAI API | ~$0.01-0.10/assessment | Depends on model choice |

**Tip:** Test on a small batch (10-20 PDFs) first to estimate costs for your full review.

---

## 🙏 Acknowledgments

- **[Robert Luke](https://github.com/rob-luke)** — Creator of the [risk-of-bias](https://github.com/rob-luke/risk-of-bias) package. The risk-of-bias module in this repository is based on his excellent work.
- **Covidence** — For systematic review management
- **Unpaywall** — For free open access PDF lookup
- **Azure AI** — For document understanding capabilities
- **OpenAI** — For powering risk of bias assessment

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

The risk-of-bias module maintains its original license from [rob-luke/risk-of-bias](https://github.com/rob-luke/risk-of-bias).

---

## 📚 Citation

If you use this toolkit in your research, please cite:

```bibtex
@software{systematic_review_automation,
  title = {Systematic Review Automation Toolkit},
  year = {2025},
  url = {https://github.com/yourusername/systematic-review-automation}
}
```

For the risk-of-bias module specifically, please also cite:
```bibtex
@software{risk_of_bias,
  author = {Luke, Robert},
  title = {Risk of Bias: AI Enabled Risk of Bias Assessment},
  url = {https://github.com/rob-luke/risk-of-bias}
}
```

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

**Made with ❤️ for the systematic review community**

*Remember: AI augments human expertise — it doesn't replace the learning journey that makes you a better researcher.*
