# RCT Extraction Pipeline

A comprehensive AI-driven pipeline for extracting structured data from randomized controlled trial (RCT) publications for systematic reviews.

## Overview

This pipeline automates the data extraction process for systematic reviews by:
1. **Document Processing**: Loading PDFs, chunking text, and creating vector embeddings
2. **Schema-Guided Extraction**: Using RAG (Retrieval-Augmented Generation) with Claude LLM
3. **Risk of Bias Assessment**: Automated RoB 2.0 evaluation using OpenAI models

## Technical Specifications

### Large Language Models (LLMs)

| Component | Provider | Model | Purpose |
|-----------|----------|-------|---------|
| Data Extraction | **Anthropic** | `claude-3-5-sonnet-20241022` | Extract 80+ structured fields from RCT manuscripts |
| Embeddings | **OpenAI** | `text-embedding-3-small` | Generate 1536-dimensional vector embeddings |
| Risk of Bias | **OpenAI** | `gpt-4o` | RoB 2.0 framework assessment |

### Vector Database

| Parameter | Value |
|-----------|-------|
| Database | **ChromaDB** |
| Type | In-memory (ephemeral per document) |
| Similarity Metric | Cosine similarity |
| Embedding Dimensions | 1536 |

### Document Chunking

| Parameter | Value | Description |
|-----------|-------|-------------|
| Strategy | `RecursiveCharacterTextSplitter` | Hierarchical splitting preserving structure |
| Chunk Size | 2000 characters | Optimal for context without fragmentation |
| Chunk Overlap | 400 characters | 20% overlap ensures context continuity |
| Tokenizer | `tiktoken` (cl100k_base) | Accurate token counting for Claude |

### Retrieval Configuration

| Parameter | Value | Description |
|-----------|-------|-------------|
| Top-K | 8 | Number of chunks retrieved per query |
| Search Type | Similarity | Cosine similarity-based retrieval |
| Multi-Query | 8 queries | Targeted queries for comprehensive coverage |

### Context Window

| Model | Context Window | Max Output |
|-------|---------------|------------|
| Claude 3.5 Sonnet | 200K tokens | 8,192 tokens |
| GPT-4o | 128K tokens | 16,384 tokens |

## Extraction Schema

The pipeline extracts **80+ structured fields** organized into domains:

### Publication Metadata
- Title, Journal, Year of Publication
- Total Authors, Corresponding Author Country
- Journal Quartile, Impact Factor

### Trial Registration
- Registration Status, Platform (ClinicalTrials.gov, ISRCTN, etc.)
- Registration Number

### Study Design
- Single/Multi-center, Geographic Location
- Therapeutic Area, Target Population
- Pilot RCT Status

### Methodology
- Randomization (method, ratio, unit)
- Stratification, Blocking, Concealment
- Blinding (single, double, open-label)

### Interventions
- Type (Pharmacological, Non-pharmacological)
- Intervention Names, Comparators
- Placebo, Standard of Care

### Outcomes & Statistics
- Primary Outcome, Statistical Type
- Power Calculation, Statistical Power
- ITT/PP Analysis, Effect Metrics

### Patient Flow
- Total Randomized, Completed Follow-up
- Loss to Follow-up, Missing Data Handling

### Risk of Bias (RoB 2.0)
- Domain 1: Randomization process
- Domain 2: Deviations from intended interventions
- Domain 3: Missing outcome data
- Domain 4: Measurement of outcome
- Domain 5: Selection of reported result
- Overall Judgment

## Installation

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -e .

# Set environment variables
export OPENAI_API_KEY="your-openai-key"
export ANTHROPIC_API_KEY="your-anthropic-key"
```

## Usage

### Command Line Interface

```bash
# Extract from a single PDF
rct-extract extract manuscript.pdf --output ./output

# Batch process a directory
rct-extract extract ./pdfs --output ./output --limit 100

# Skip Risk of Bias assessment
rct-extract extract ./pdfs --output ./output --no-rob

# Run RoB assessment only
rct-extract assess manuscript.pdf --output result.json

# Display pipeline information
rct-extract info
```

### Python API

```python
from rct_extraction_pipeline import run_pipeline, RCTExtractionPipeline, PipelineConfig

# Simple usage
results = run_pipeline(
    input_dir="./pdfs",
    output_dir="./output",
    limit=10,
    run_rob=True,
)

# Advanced configuration
config = PipelineConfig(
    extraction_model="claude-3-5-sonnet-20241022",
    extraction_temperature=0.0,
    chunk_size=2000,
    chunk_overlap=400,
    top_k=8,
    rob_model="gpt-4o",
    run_rob_assessment=True,
)

pipeline = RCTExtractionPipeline(config)
result = pipeline.process_single(Path("manuscript.pdf"))
```

## Output Format

### JSON Output

```json
{
    "filename": "study.pdf",
    "processed_at": "2025-01-12T15:30:00",
    "status": "success",
    "extraction": {
        "title": "A Randomized Controlled Trial of...",
        "journalName": "JAMA",
        "yearOfPublication": 2024,
        "totalParticipants": 500,
        "randomization": true,
        "randomizationRatio": "1:1",
        "blinding": "double-blind",
        "primaryOutcome": "Overall survival at 12 months",
        ...
    },
    "risk_of_bias": {
        "overall": "Low",
        "domains": {
            "randomization": {"judgment": "Low", ...},
            "deviations": {"judgment": "Low", ...},
            "missing_data": {"judgment": "Some concerns", ...},
            "measurement": {"judgment": "Low", ...},
            "selection": {"judgment": "Low", ...}
        }
    }
}
```

### CSV Output

Flattened extraction results with one row per manuscript, suitable for data analysis and comparison with human-extracted data.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    RCT Extraction Pipeline                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐       │
│  │   PDF Input  │───▶│   PyPDF      │───▶│   Text       │       │
│  │              │    │   Loader     │    │   Chunks     │       │
│  └──────────────┘    └──────────────┘    └──────┬───────┘       │
│                                                  │               │
│                                                  ▼               │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐       │
│  │   OpenAI     │───▶│   ChromaDB   │◀───│   Vector     │       │
│  │   Embeddings │    │   Store      │    │   Index      │       │
│  └──────────────┘    └──────┬───────┘    └──────────────┘       │
│                             │                                    │
│                             ▼                                    │
│  ┌──────────────────────────────────────────────────────┐       │
│  │               Multi-Query Retrieval                   │       │
│  │  • Study metadata queries                             │       │
│  │  • Methodology queries                                │       │
│  │  • Outcome queries                                    │       │
│  │  • Statistical queries                                │       │
│  └──────────────────────────┬───────────────────────────┘       │
│                             │                                    │
│                             ▼                                    │
│  ┌──────────────────────────────────────────────────────┐       │
│  │            Claude 3.5 Sonnet (Anthropic)              │       │
│  │                                                        │       │
│  │  • Schema-guided extraction                           │       │
│  │  • Structured JSON output                             │       │
│  │  • 80+ extraction fields                              │       │
│  └──────────────────────────┬───────────────────────────┘       │
│                             │                                    │
│                             ▼                                    │
│  ┌──────────────────────────────────────────────────────┐       │
│  │              GPT-4o (OpenAI) - RoB 2.0                │       │
│  │                                                        │       │
│  │  • 5 bias domains + overall judgment                  │       │
│  │  • Evidence-based reasoning                           │       │
│  │  • Cochrane methodology                               │       │
│  └──────────────────────────┬───────────────────────────┘       │
│                             │                                    │
│                             ▼                                    │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐       │
│  │   JSON       │    │   CSV        │    │   Metrics    │       │
│  │   Output     │    │   Export     │    │   Report     │       │
│  └──────────────┘    └──────────────┘    └──────────────┘       │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Dependencies

### Core Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| langchain | ≥0.3.0 | LLM orchestration framework |
| langchain-anthropic | ≥0.2.0 | Claude integration |
| langchain-openai | ≥0.2.0 | OpenAI integration |
| langchain-chroma | ≥0.1.0 | ChromaDB vector store |
| chromadb | ≥0.5.0 | Vector database |
| tiktoken | ≥0.7.0 | Token counting |
| pypdf | ≥4.0.0 | PDF parsing |
| pydantic | ≥2.9.0 | Data validation |
| pandas | ≥2.2.0 | Data processing |

### Risk of Bias

The RoB 2.0 assessment uses a fork of the [risk-of-bias](https://github.com/rob-luke/risk-of-bias) package by Robert Luke, which implements the Cochrane Risk of Bias 2.0 tool.

Reference: Sterne JAC, et al. RoB 2: a revised tool for assessing risk of bias in randomised trials. BMJ 2019;366:l4898.

## Performance Considerations

- **API Rate Limits**: Default sequential processing (1 worker) to respect API limits
- **Memory**: ChromaDB uses ephemeral in-memory storage per document
- **Cost**: Estimated $0.01-0.05 per manuscript (extraction + RoB)
- **Speed**: ~30-60 seconds per manuscript (depends on length)

## Comparison with Human Extraction

This pipeline is designed for validation against human-extracted data:

| Field Type | Extraction Method | Comparison Metric |
|------------|-------------------|-------------------|
| Numeric | Direct extraction | ICC, MAE |
| Boolean | Inference | Cohen's Kappa |
| Categorical | Classification | Weighted Kappa |
| Free-text | Generation | Semantic Similarity |
| Risk of Bias | Framework | Domain-level Kappa |

## License

MIT License

## Acknowledgments

- Risk of Bias assessment based on [rob-luke/risk-of-bias](https://github.com/rob-luke/risk-of-bias)
- Inspired by LangChain RAG patterns from [ped-surg-ai](./ped-surg-ai)
- Cochrane RoB 2.0 methodology
