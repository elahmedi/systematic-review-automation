# Systematic Literature Review Automation Pipeline
## Technical Requirements Document — Detailed Technical Specification (Version 2)

**Document Version:** 2.0  
**Date:** January 2026  
**Status:** Technical Specification for Development Teams  
**Audience:** Software Engineers, ML Engineers, Data Scientists

---

## Table of Contents

1. [System Architecture](#1-system-architecture)
2. [Stage 1: Research Question & Hypothesis Generation](#2-stage-1-research-question--hypothesis-generation)
3. [Stage 2: Search Strategy Development & Execution](#3-stage-2-search-strategy-development--execution)
4. [Stage 3: Deduplication Engine](#4-stage-3-deduplication-engine)
5. [Stage 4: Title & Abstract Screening](#5-stage-4-title--abstract-screening)
6. [Stage 5: Full-Text Review & PDF Retrieval](#6-stage-5-full-text-review--pdf-retrieval)
7. [Stage 6: Structured Data Extraction](#7-stage-6-structured-data-extraction)
8. [Stage 7: Risk of Bias Assessment](#8-stage-7-risk-of-bias-assessment)
9. [Stage 8: Statistical Analysis & Meta-Analysis](#9-stage-8-statistical-analysis--meta-analysis)
10. [Stage 9: Visualisation Engine](#10-stage-9-visualisation-engine)
11. [Stage 10: Manuscript Generation](#11-stage-10-manuscript-generation)
12. [Knowledge Graph Engine](#12-knowledge-graph-engine)
13. [Data Models & Schemas](#13-data-models--schemas)
14. [API Specifications](#14-api-specifications)
15. [Security & Compliance](#15-security--compliance)
16. [Performance Requirements](#16-performance-requirements)

---

## 1. System Architecture

### 1.1 Technology Stack

| Layer | Technology | Rationale |
|-------|------------|-----------|
| **Frontend** | React/Next.js + TypeScript | Modern SPA with SSR support |
| **Backend API** | FastAPI (Python 3.12+) | Async support, Pydantic validation |
| **Workflow Orchestration** | Temporal.io | Durable execution, retry logic |
| **Message Queue** | Redis Streams / RabbitMQ | Task distribution |
| **Primary Database** | PostgreSQL 16+ | Relational data, JSON support |
| **Vector Database** | ChromaDB / Qdrant | Embedding storage and similarity search |
| **Graph Database** | Neo4j 5+ | Knowledge graph storage |
| **Document Storage** | MinIO / S3 | PDF and file storage |
| **Search Engine** | Elasticsearch 8+ | Full-text search, faceting |
| **Caching** | Redis | Session, API response caching |
| **LLM Integration** | LangChain | Multi-provider orchestration |
| **Containerisation** | Docker + Kubernetes | Deployment and scaling |

### 1.2 LLM/AI Model Requirements

| Task | Model Class | Recommended Models | Fallback |
|------|-------------|-------------------|----------|
| **General Extraction** | Frontier LLM | Claude Opus 4, GPT-4o, GPT-4.1 | Claude Sonnet, GPT-4o-mini |
| **Reasoning Tasks** | Reasoning LLM | o3, o4-mini, Claude with thinking | Standard LLM with CoT |
| **Embeddings** | Embedding Model | text-embedding-3-large, Titan V2 | text-embedding-3-small |
| **Document Parsing** | Vision-Language | GPT-4V, Claude 3 Opus | GROBID + LLM |
| **Fine-tuned Screening** | Custom Classifier | Fine-tuned BERT/RoBERTa | Zero-shot LLM |
| **NER/Relation Extraction** | Biomedical NLP | PubMedBERT, BioBERT | SpaCy with custom models |

### 1.3 External Service Dependencies

```yaml
external_services:
  literature_databases:
    - name: PubMed/MEDLINE
      api: E-utilities API
      rate_limit: 10 req/s with API key
    - name: Embase
      api: Embase API (institutional)
      auth: OAuth 2.0
    - name: Cochrane Library
      api: Cochrane API
      auth: API key
    - name: Web of Science
      api: WoS API
      auth: Institutional
    - name: Scopus
      api: Scopus Search API
      auth: API key
    
  pdf_sources:
    - name: Unpaywall
      api: REST API
      rate_limit: 100,000/day
    - name: Semantic Scholar
      api: Graph API
      rate_limit: 100/5min (unauthenticated)
    - name: CrossRef
      api: REST API
      rate_limit: Polite pool
    
  ai_providers:
    - name: OpenAI
      models: [gpt-4o, gpt-4.1, o3, text-embedding-3-large]
      auth: API key
    - name: Anthropic
      models: [claude-opus-4, claude-sonnet-4]
      auth: API key
    - name: AWS Bedrock
      models: [claude-v3, titan-embed-v2]
      auth: IAM credentials
```

---

## 2. Stage 1: Research Question & Hypothesis Generation

### 2.1 Functional Requirements

#### FR-1.1: PICO Framework Extraction
```python
@dataclass
class PICOFramework:
    population: str
    intervention: str
    comparator: str
    outcome: str
    study_design: Optional[str] = None  # For PICOS
    timeframe: Optional[str] = None
    setting: Optional[str] = None
    
@dataclass
class ResearchQuestion:
    id: UUID
    free_text_question: str
    pico: PICOFramework
    secondary_questions: List[str]
    hypotheses: List[Hypothesis]
    suggested_search_terms: Dict[str, List[str]]
    created_at: datetime
    refined_versions: List["ResearchQuestion"]
```

#### FR-1.2: AI-Assisted Question Refinement

**Input:** User's preliminary research question (free text)

**Process:**
1. Parse free text using LLM to extract PICO elements
2. Identify ambiguities and suggest clarifications
3. Generate alternative phrasings ranked by specificity
4. Suggest related questions based on literature gaps
5. Generate testable hypotheses

**Output:** Structured PICO with refinement suggestions

```python
class QuestionRefinementService:
    async def refine_question(
        self,
        raw_question: str,
        domain_context: Optional[str] = None,
        existing_reviews: Optional[List[str]] = None
    ) -> RefinedQuestionResult:
        """
        Refine a research question using LLM with RAG.
        
        Args:
            raw_question: User's initial question
            domain_context: Optional domain knowledge to include
            existing_reviews: Titles of existing reviews to avoid duplication
            
        Returns:
            RefinedQuestionResult with PICO extraction and suggestions
        """
        pass
```

#### FR-1.3: Protocol Template Generation

Generate PROSPERO-compatible protocol from refined question:

```python
class ProtocolGenerator:
    def generate_protocol(
        self,
        research_question: ResearchQuestion,
        template: ProtocolTemplate = ProtocolTemplate.PROSPERO
    ) -> ProtocolDocument:
        """Generate systematic review protocol document."""
        pass
```

### 2.2 Technical Specifications

| Specification | Requirement |
|--------------|-------------|
| LLM Model | Claude Opus 4 / GPT-4.1 |
| Prompt Strategy | Few-shot with domain examples |
| Response Format | Structured JSON with Pydantic validation |
| Latency Target | < 10 seconds for initial refinement |
| Caching | Cache PICO extractions by input hash |

---

## 3. Stage 2: Search Strategy Development & Execution

### 3.1 Functional Requirements

#### FR-2.1: Search Query Generation

```python
@dataclass
class SearchQuery:
    database: DatabaseType
    query_string: str
    query_tree: QueryNode  # AST representation
    mesh_terms: List[MeSHTerm]
    free_text_terms: List[str]
    filters: SearchFilters
    expected_results: Optional[int]
    
@dataclass
class QueryNode:
    operator: Literal["AND", "OR", "NOT", "TERM"]
    children: Optional[List["QueryNode"]]
    term: Optional[str]
    field: Optional[str]  # e.g., [tiab], [MeSH]

class SearchStrategyGenerator:
    async def generate_strategy(
        self,
        pico: PICOFramework,
        databases: List[DatabaseType],
        sensitivity_level: Literal["high", "balanced", "precise"] = "balanced"
    ) -> Dict[DatabaseType, SearchQuery]:
        """
        Generate database-specific search strategies from PICO.
        
        High sensitivity: Maximize recall (more terms, fewer filters)
        Balanced: Trade-off between sensitivity and precision
        Precise: Maximize precision (specific terms, more filters)
        """
        pass
```

#### FR-2.2: Medical Ontology Integration

```python
class OntologyService:
    """Interface with MeSH, EMTREE, SNOMED-CT, ICD ontologies."""
    
    def get_mesh_terms(
        self,
        concept: str,
        include_subheadings: bool = True,
        explode: bool = True
    ) -> List[MeSHTerm]:
        """Get MeSH terms for a concept with explosion."""
        pass
    
    def get_synonyms(
        self,
        term: str,
        sources: List[str] = ["mesh", "umls", "emtree"]
    ) -> List[str]:
        """Get synonyms from multiple ontologies."""
        pass
    
    def translate_mesh_to_emtree(
        self,
        mesh_terms: List[MeSHTerm]
    ) -> List[EMTREETerm]:
        """Translate MeSH terms to EMTREE equivalents."""
        pass
```

#### FR-2.3: Multi-Database Query Execution

```python
class DatabaseExecutor:
    """Execute searches across multiple databases."""
    
    async def execute_search(
        self,
        query: SearchQuery,
        database: DatabaseType,
        max_results: int = 10000
    ) -> SearchResult:
        """
        Execute search and return citations.
        
        Supports: PubMed, Embase, Cochrane, Web of Science, Scopus,
                  PsycINFO, CINAHL, Google Scholar, Semantic Scholar
        """
        pass
    
    async def batch_execute(
        self,
        strategies: Dict[DatabaseType, SearchQuery]
    ) -> Dict[DatabaseType, SearchResult]:
        """Execute searches across all databases concurrently."""
        pass
```

### 3.2 Database-Specific Query Translation

| Database | Query Syntax | Field Codes | API |
|----------|--------------|-------------|-----|
| PubMed | Boolean with [field] tags | [tiab], [MeSH], [pt] | E-utilities |
| Embase | Boolean with /field | /ti, /ab, /exp | Embase API |
| Cochrane | Boolean with :field | :ti, :ab, :kw | Cochrane API |
| Web of Science | Boolean with TS=, TI= | TS, TI, AU | WoS API |
| Scopus | Boolean with TITLE-ABS | TITLE-ABS-KEY | Scopus API |

### 3.3 Technical Specifications

| Specification | Requirement |
|--------------|-------------|
| Supported Databases | ≥ 8 major bibliographic databases |
| Query Languages | Database-specific Boolean syntax |
| API Rate Limiting | Respect per-database limits with backoff |
| Result Export | RIS, BibTeX, EndNote XML, CSV |
| Search Audit | Full provenance tracking |
| Reproducibility | Deterministic query generation |

---

## 4. Stage 3: Deduplication Engine

### 4.1 Functional Requirements

#### FR-3.1: Multi-Level Deduplication

```python
@dataclass
class DeduplicationResult:
    unique_citations: List[Citation]
    duplicate_groups: List[DuplicateGroup]
    merge_decisions: List[MergeDecision]
    statistics: DeduplicationStats

class DeduplicationEngine:
    """Multi-strategy deduplication engine."""
    
    def deduplicate(
        self,
        citations: List[Citation],
        strategies: List[DeduplicationStrategy] = None
    ) -> DeduplicationResult:
        """
        Apply deduplication strategies in order:
        1. Exact match on DOI/PMID
        2. Title + year exact match
        3. Fuzzy title matching (Levenshtein > 0.9)
        4. Embedding similarity (cosine > 0.95)
        5. Author + year + journal heuristics
        """
        pass
```

#### FR-3.2: Embedding-Based Similarity

```python
class EmbeddingDeduplicator:
    """Use embeddings for fuzzy duplicate detection."""
    
    def __init__(
        self,
        embedding_model: str = "text-embedding-3-small",
        similarity_threshold: float = 0.95
    ):
        self.model = embedding_model
        self.threshold = similarity_threshold
    
    async def find_similar(
        self,
        citations: List[Citation]
    ) -> List[Tuple[Citation, Citation, float]]:
        """Find similar citation pairs above threshold."""
        # 1. Generate embeddings for title + abstract
        # 2. Build approximate nearest neighbor index (FAISS/Annoy)
        # 3. Find pairs above similarity threshold
        pass
```

### 4.2 Technical Specifications

| Specification | Requirement |
|--------------|-------------|
| Exact Match Fields | DOI, PMID, PMC ID, ISBN |
| Fuzzy Match Algorithm | Levenshtein + Jaro-Winkler |
| Embedding Model | text-embedding-3-small (1536 dims) |
| Similarity Threshold | Configurable (default 0.95) |
| Performance | Process 100K citations in < 5 minutes |
| Merge Strategy | Prefer records with DOI, then PMID, then most complete |

---

## 5. Stage 4: Title & Abstract Screening

### 5.1 Functional Requirements

#### FR-4.1: Binary Classification with Confidence

```python
@dataclass
class ScreeningDecision:
    citation_id: UUID
    decision: Literal["include", "exclude", "uncertain"]
    confidence: float  # 0.0 to 1.0
    reasoning: str
    evidence_excerpts: List[str]
    screened_by: str  # "ai", "human_1", "human_2"
    screened_at: datetime

class ScreeningClassifier:
    """AI-powered title/abstract screening."""
    
    async def screen(
        self,
        citation: Citation,
        inclusion_criteria: List[str],
        exclusion_criteria: List[str]
    ) -> ScreeningDecision:
        """
        Screen a single citation against criteria.
        
        Uses LLM with inclusion/exclusion criteria in prompt.
        Returns decision with confidence and reasoning.
        """
        pass
    
    async def batch_screen(
        self,
        citations: List[Citation],
        criteria: ScreeningCriteria,
        prioritize_by: Literal["random", "confidence", "year"] = "confidence"
    ) -> List[ScreeningDecision]:
        """
        Batch screen with prioritization.
        
        'confidence': Screen uncertain cases first (active learning)
        'year': Screen newest publications first
        """
        pass
```

#### FR-4.2: Active Learning Loop

```python
class ActiveLearningScreener:
    """Screening with active learning from human feedback."""
    
    def __init__(
        self,
        base_model: str = "gpt-4o-mini",
        uncertainty_threshold: float = 0.3
    ):
        self.model = base_model
        self.uncertainty_threshold = uncertainty_threshold
        self.human_decisions: List[ScreeningDecision] = []
    
    async def get_next_batch_for_human_review(
        self,
        n: int = 50
    ) -> List[Citation]:
        """
        Get citations most valuable for human review.
        
        Prioritizes:
        1. Citations near decision boundary (confidence 0.4-0.6)
        2. Citations where AI disagrees with initial prediction
        3. Random sample for calibration
        """
        pass
    
    def update_from_human_feedback(
        self,
        decisions: List[ScreeningDecision]
    ) -> None:
        """Incorporate human decisions for improved predictions."""
        pass
```

#### FR-4.3: Dual-Reviewer Workflow

```python
class DualReviewerWorkflow:
    """Manage dual-reviewer screening with arbitration."""
    
    async def assign_reviewers(
        self,
        citations: List[Citation],
        reviewers: List[Reviewer],
        overlap_percentage: float = 0.2
    ) -> Dict[UUID, List[Reviewer]]:
        """Assign citations to reviewers with overlap."""
        pass
    
    def calculate_agreement(
        self,
        decisions_1: List[ScreeningDecision],
        decisions_2: List[ScreeningDecision]
    ) -> AgreementMetrics:
        """
        Calculate inter-rater agreement.
        
        Returns: Cohen's kappa, percent agreement, PABAK
        """
        pass
    
    async def resolve_conflicts(
        self,
        conflicts: List[Conflict],
        arbitrator: Reviewer
    ) -> List[ScreeningDecision]:
        """Third reviewer arbitration for disagreements."""
        pass
```

### 5.2 Technical Specifications

| Specification | Requirement |
|--------------|-------------|
| Screening Model | LLM (GPT-4o-mini) or fine-tuned classifier |
| Confidence Calibration | Platt scaling on validation set |
| Target Sensitivity | ≥ 95% (miss < 5% of relevant studies) |
| Throughput | ≥ 1000 citations/minute |
| Human-AI Agreement | Target κ ≥ 0.8 |
| Audit Trail | Full decision history with timestamps |

---

## 6. Stage 5: Full-Text Review & PDF Retrieval

### 6.1 Functional Requirements

#### FR-5.1: Multi-Source PDF Retrieval

```python
class PDFRetriever:
    """Retrieve PDFs from multiple sources."""
    
    def __init__(
        self,
        unpaywall_email: str,
        ezproxy_config: Optional[EZProxyConfig] = None
    ):
        self.sources = [
            UnpaywallSource(unpaywall_email),
            SemanticScholarSource(),
            CrossRefSource(),
            PubMedCentralSource(),
            EZProxySource(ezproxy_config) if ezproxy_config else None,
        ]
    
    async def retrieve(
        self,
        citation: Citation,
        fallback_chain: bool = True
    ) -> PDFRetrievalResult:
        """
        Attempt to retrieve PDF from multiple sources.
        
        Order: PMC (free) → Unpaywall (OA) → Semantic Scholar → EZProxy (institutional)
        """
        pass
    
    async def batch_retrieve(
        self,
        citations: List[Citation],
        concurrency: int = 5
    ) -> Dict[UUID, PDFRetrievalResult]:
        """Batch retrieve with rate limiting."""
        pass
```

#### FR-5.2: Full-Text Eligibility Screening

```python
class FullTextScreener:
    """Screen full-text documents for eligibility."""
    
    async def screen_full_text(
        self,
        pdf_path: Path,
        inclusion_criteria: List[str],
        exclusion_criteria: List[str]
    ) -> FullTextScreeningResult:
        """
        Screen full-text PDF against criteria.
        
        Process:
        1. Parse PDF to text (GROBID or PyPDF)
        2. Extract relevant sections (Methods, Results)
        3. Evaluate against each criterion
        4. Return decision with exclusion reasons
        """
        pass
```

#### FR-5.3: PRISMA Flow Tracking

```python
@dataclass
class PRISMAFlow:
    """Track PRISMA flow diagram statistics."""
    
    identification: IdentificationStats
    screening: ScreeningStats
    eligibility: EligibilityStats
    included: IncludedStats
    
    def to_prisma_diagram(self) -> str:
        """Generate PRISMA 2020 flow diagram (SVG)."""
        pass

@dataclass
class ExclusionReason:
    reason_code: str
    reason_text: str
    count: int
    examples: List[UUID]
```

### 6.2 Technical Specifications

| Specification | Requirement |
|--------------|-------------|
| PDF Sources | Unpaywall, PMC, EZProxy, Semantic Scholar |
| Parser | GROBID (primary), PyPDF (fallback) |
| Document Processing | Section-aware chunking (IMRaD) |
| Retrieval Success Target | ≥ 85% of citations |
| Storage | S3-compatible object storage |
| PRISMA Compliance | PRISMA 2020 checklist |

---

## 7. Stage 6: Structured Data Extraction

### 7.1 Functional Requirements

#### FR-6.1: Schema-Guided Extraction

```python
EXTRACTION_FIELDS = {
    # Publication Metadata
    "title": {"type": "string", "required": True},
    "journal": {"type": "string", "required": True},
    "year": {"type": "integer", "required": True},
    "doi": {"type": "string", "required": False},
    "authors": {"type": "array[string]", "required": True},
    
    # Study Design
    "study_design": {"type": "enum", "options": ["RCT", "quasi-RCT", "cohort", "case-control"]},
    "randomization_method": {"type": "string"},
    "blinding": {"type": "enum", "options": ["double-blind", "single-blind", "open-label", "unclear"]},
    "allocation_concealment": {"type": "enum", "options": ["adequate", "inadequate", "unclear"]},
    
    # Population
    "total_participants": {"type": "integer"},
    "inclusion_criteria": {"type": "string"},
    "exclusion_criteria": {"type": "string"},
    "mean_age": {"type": "float"},
    "female_percentage": {"type": "float"},
    
    # Intervention
    "intervention_name": {"type": "string"},
    "intervention_details": {"type": "string"},
    "comparator": {"type": "string"},
    "follow_up_duration": {"type": "string"},
    
    # Outcomes
    "primary_outcome": {"type": "string"},
    "secondary_outcomes": {"type": "array[string]"},
    "outcome_timepoints": {"type": "array[string]"},
    
    # Results
    "effect_estimate": {"type": "float"},
    "effect_type": {"type": "enum", "options": ["OR", "RR", "HR", "MD", "SMD"]},
    "ci_lower": {"type": "float"},
    "ci_upper": {"type": "float"},
    "p_value": {"type": "float"},
    
    # Demographics by arm
    "demographics": {"type": "array[DemographicsGroup]"},
}

class DataExtractor:
    """Extract structured data from full-text PDFs."""
    
    async def extract(
        self,
        pdf_path: Path,
        schema: Dict[str, FieldSpec] = EXTRACTION_FIELDS,
        extraction_model: str = "claude-opus-4"
    ) -> ExtractionResult:
        """
        Extract data using RAG with schema guidance.
        
        Process:
        1. Parse PDF with GROBID (section-aware)
        2. Generate embeddings for chunks
        3. For each field, retrieve relevant chunks
        4. Extract field value with LLM
        5. Validate against schema
        """
        pass
```

#### FR-6.2: Table and Figure Extraction

```python
class TableExtractor:
    """Extract data from tables in PDFs."""
    
    async def extract_tables(
        self,
        pdf_path: Path,
        table_types: List[str] = ["baseline", "results", "adverse_events"]
    ) -> List[ExtractedTable]:
        """
        Extract tables using vision-language model.
        
        1. Detect table regions in PDF
        2. Use GPT-4V/Claude to parse table structure
        3. Map to structured format
        """
        pass

class FigureExtractor:
    """Extract data from figures (forest plots, etc.)."""
    
    async def extract_forest_plot_data(
        self,
        pdf_path: Path
    ) -> Optional[ForestPlotData]:
        """Extract effect sizes from forest plot images."""
        pass
```

### 7.2 Technical Specifications

| Specification | Requirement |
|--------------|-------------|
| Extraction Fields | ≥ 80 standardised fields |
| Extraction Model | Claude Opus 4 / GPT-4.1 |
| RAG Architecture | ChromaDB + multi-query retrieval |
| Chunk Size | 2000 chars with 400 char overlap |
| Top-K Retrieval | 8 chunks per field |
| Validation | Pydantic schema validation |
| Output Format | JSON, CSV, Excel |

---

## 8. Stage 7: Risk of Bias Assessment

### 8.1 Functional Requirements

#### FR-7.1: RoB 2 Framework Implementation

```python
@dataclass
class RoB2Assessment:
    study_id: UUID
    domains: Dict[str, DomainAssessment]
    overall_judgment: RiskLevel
    assessed_by: str
    assessed_at: datetime

@dataclass
class DomainAssessment:
    domain_name: str
    questions: List[QuestionResponse]
    domain_judgment: RiskLevel
    support_for_judgment: str

class RoBAssessor:
    """AI-powered Risk of Bias assessment."""
    
    async def assess_rob2(
        self,
        pdf_path: Path,
        guidance_document: Optional[Path] = None,
        model: str = "gpt-4o"
    ) -> RoB2Assessment:
        """
        Perform RoB 2 assessment on a study.
        
        Domains:
        1. Randomization process
        2. Deviations from intended interventions
        3. Missing outcome data
        4. Measurement of the outcome
        5. Selection of the reported result
        """
        pass
    
    def compare_assessments(
        self,
        assessment_1: RoB2Assessment,
        assessment_2: RoB2Assessment
    ) -> ComparisonResult:
        """Compare two assessments (e.g., AI vs human)."""
        pass
```

#### FR-7.2: Evidence Extraction with Citations

```python
class EvidenceExtractor:
    """Extract evidence supporting RoB judgments."""
    
    async def extract_evidence(
        self,
        pdf_path: Path,
        domain: str,
        question: str
    ) -> EvidenceResult:
        """
        Extract verbatim evidence from PDF.
        
        Returns:
            - Relevant text excerpts
            - Page numbers
            - Section locations
        """
        pass
```

### 8.2 Technical Specifications

| Specification | Requirement |
|--------------|-------------|
| Framework | RoB 2 (Cochrane Collaboration) |
| Model | GPT-4o / o3 (reasoning) |
| Evidence Tracking | Verbatim excerpts with page references |
| Output Format | JSON, RobVis-compatible CSV |
| Multi-assessor Support | AI + 2 human reviewers |
| Agreement Metrics | Cohen's kappa by domain |

---

## 9. Stage 8: Statistical Analysis & Meta-Analysis

### 9.1 Functional Requirements

#### FR-8.1: Effect Size Calculation

```python
class EffectSizeCalculator:
    """Calculate effect sizes from extracted data."""
    
    def calculate_odds_ratio(
        self,
        events_treatment: int,
        n_treatment: int,
        events_control: int,
        n_control: int
    ) -> EffectSize:
        """Calculate OR with 95% CI."""
        pass
    
    def calculate_risk_ratio(self, ...) -> EffectSize:
        pass
    
    def calculate_mean_difference(
        self,
        mean_treatment: float,
        sd_treatment: float,
        n_treatment: int,
        mean_control: float,
        sd_control: float,
        n_control: int
    ) -> EffectSize:
        """Calculate MD with 95% CI."""
        pass
    
    def calculate_smd(self, ...) -> EffectSize:
        """Calculate Hedges' g or Cohen's d."""
        pass
```

#### FR-8.2: Meta-Analysis Engine

```python
class MetaAnalysisEngine:
    """Perform meta-analyses with various models."""
    
    def fixed_effects(
        self,
        studies: List[StudyEffect],
        method: Literal["inverse_variance", "mantel_haenszel", "peto"] = "inverse_variance"
    ) -> MetaAnalysisResult:
        """Fixed effects meta-analysis."""
        pass
    
    def random_effects(
        self,
        studies: List[StudyEffect],
        method: Literal["DL", "REML", "PM", "SJ"] = "REML"
    ) -> MetaAnalysisResult:
        """Random effects meta-analysis with heterogeneity."""
        pass
    
    def subgroup_analysis(
        self,
        studies: List[StudyEffect],
        grouping_variable: str
    ) -> SubgroupResult:
        """Subgroup analysis with test for interaction."""
        pass
    
    def sensitivity_analysis(
        self,
        studies: List[StudyEffect],
        analysis_type: Literal["leave_one_out", "influence", "cumulative"]
    ) -> SensitivityResult:
        """Sensitivity analyses."""
        pass
    
    def publication_bias(
        self,
        studies: List[StudyEffect]
    ) -> PublicationBiasResult:
        """
        Assess publication bias.
        
        Methods: Funnel plot, Egger's test, Begg's test, trim-and-fill
        """
        pass
```

### 9.2 Technical Specifications

| Specification | Requirement |
|--------------|-------------|
| Effect Measures | OR, RR, HR, MD, SMD |
| Heterogeneity | I², τ², Q statistic, prediction intervals |
| Models | Fixed effects (IV, MH, Peto), Random effects (DL, REML) |
| Statistical Backend | Python (scipy, statsmodels) or R (metafor) via rpy2 |
| Sensitivity Analyses | Leave-one-out, influence analysis, cumulative |
| Publication Bias | Funnel plot, Egger's, Begg's, trim-and-fill |

---

## 10. Stage 9: Visualisation Engine

### 10.1 Functional Requirements

#### FR-9.1: Forest Plot Generation

```python
class ForestPlotGenerator:
    """Generate publication-quality forest plots."""
    
    def generate(
        self,
        meta_result: MetaAnalysisResult,
        style: ForestPlotStyle = ForestPlotStyle.COCHRANE,
        output_format: Literal["svg", "pdf", "png"] = "svg"
    ) -> bytes:
        """
        Generate forest plot.
        
        Features:
        - Study labels with year
        - Effect estimates with CI
        - Weights (%)
        - Diamond for pooled estimate
        - Heterogeneity statistics
        - Subgroup separators
        """
        pass
```

#### FR-9.2: Additional Visualisations

```python
class VisualisationEngine:
    """Generate systematic review visualisations."""
    
    def funnel_plot(self, studies: List[StudyEffect]) -> bytes:
        """Generate funnel plot for publication bias."""
        pass
    
    def rob_traffic_light(
        self,
        assessments: List[RoB2Assessment],
        format: Literal["robvis", "custom"] = "robvis"
    ) -> bytes:
        """Generate RoB traffic light plot."""
        pass
    
    def rob_summary(
        self,
        assessments: List[RoB2Assessment]
    ) -> bytes:
        """Generate RoB summary (bar) plot."""
        pass
    
    def prisma_diagram(
        self,
        flow: PRISMAFlow
    ) -> bytes:
        """Generate PRISMA 2020 flow diagram."""
        pass
    
    def grade_sof_table(
        self,
        outcomes: List[GRADEOutcome]
    ) -> bytes:
        """Generate GRADE Summary of Findings table."""
        pass
```

### 10.2 Technical Specifications

| Specification | Requirement |
|--------------|-------------|
| Output Formats | SVG (vector), PDF, PNG (raster) |
| Styling | Cochrane-compliant, customisable |
| Resolution | 300 DPI minimum for publication |
| Libraries | Matplotlib, Plotly, custom SVG |
| Interactivity | Optional interactive HTML versions |

---

## 11. Stage 10: Manuscript Generation

### 11.1 Functional Requirements

#### FR-10.1: Section-by-Section Generation

```python
class ManuscriptGenerator:
    """AI-assisted manuscript generation."""
    
    async def generate_manuscript(
        self,
        review_data: SystematicReviewData,
        template: ManuscriptTemplate = ManuscriptTemplate.COCHRANE,
        target_journal: Optional[str] = None
    ) -> Manuscript:
        """
        Generate complete manuscript draft.
        
        Sections:
        1. Title and Abstract (structured)
        2. Introduction
        3. Methods (PRISMA-compliant)
        4. Results
        5. Discussion
        6. Conclusion
        7. References
        8. Tables and Figures
        9. Supplementary Material
        """
        pass
    
    async def generate_section(
        self,
        section: ManuscriptSection,
        review_data: SystematicReviewData,
        previous_sections: List[str]
    ) -> str:
        """Generate individual manuscript section."""
        pass
```

#### FR-10.2: Citation Management

```python
class CitationManager:
    """Manage references and citations."""
    
    def insert_citations(
        self,
        text: str,
        citations: List[Citation],
        style: CitationStyle = CitationStyle.VANCOUVER
    ) -> str:
        """Insert citations into text in specified style."""
        pass
    
    def generate_bibliography(
        self,
        citations: List[Citation],
        style: CitationStyle
    ) -> str:
        """Generate formatted bibliography."""
        pass
    
    def export_to_reference_manager(
        self,
        citations: List[Citation],
        format: Literal["ris", "bibtex", "endnote"]
    ) -> bytes:
        """Export citations for reference manager."""
        pass
```

#### FR-10.3: PRISMA Checklist Compliance

```python
class PRISMAChecker:
    """Verify PRISMA 2020 checklist compliance."""
    
    def check_compliance(
        self,
        manuscript: Manuscript
    ) -> PRISMAComplianceReport:
        """
        Check manuscript against PRISMA 2020 checklist.
        
        Returns:
            - Checklist item status (met/not met/NA)
            - Page/section references
            - Suggestions for missing items
        """
        pass
```

### 11.2 Technical Specifications

| Specification | Requirement |
|--------------|-------------|
| Generation Model | Claude Opus 4 / GPT-4.1 |
| Templates | Cochrane, PRISMA 2020, Journal-specific |
| Citation Styles | Vancouver, APA, AMA, Harvard, Chicago |
| Output Formats | DOCX, LaTeX, Markdown, HTML |
| PRISMA Compliance | Automated checklist verification |
| Plagiarism | Original text generation, no direct copying |

---

## 12. Knowledge Graph Engine

### 12.1 Functional Requirements

#### FR-12.1: Entity Extraction

```python
class EntityExtractor:
    """Extract entities from study texts."""
    
    ENTITY_TYPES = [
        "Intervention",
        "Comparator", 
        "Population",
        "Outcome",
        "Disease",
        "Drug",
        "Gene",
        "Biomarker",
        "Study",
        "Author",
        "Institution",
    ]
    
    async def extract_entities(
        self,
        text: str,
        entity_types: List[str] = None
    ) -> List[Entity]:
        """Extract named entities using NER models."""
        pass
```

#### FR-12.2: Relation Extraction

```python
class RelationExtractor:
    """Extract relationships between entities."""
    
    RELATION_TYPES = [
        "TREATS",
        "CAUSES",
        "ASSOCIATED_WITH",
        "COMPARED_TO",
        "MEASURED_BY",
        "CONDUCTED_AT",
        "AUTHORED_BY",
        "FUNDED_BY",
    ]
    
    async def extract_relations(
        self,
        text: str,
        entities: List[Entity]
    ) -> List[Relation]:
        """Extract relationships between entities."""
        pass
```

#### FR-12.3: Graph Storage and Querying

```python
class KnowledgeGraph:
    """Manage knowledge graph in Neo4j."""
    
    def __init__(self, neo4j_uri: str, auth: Tuple[str, str]):
        self.driver = GraphDatabase.driver(neo4j_uri, auth=auth)
    
    def add_study(
        self,
        study: StudyNode,
        entities: List[Entity],
        relations: List[Relation]
    ) -> None:
        """Add study and its relationships to graph."""
        pass
    
    def query_natural_language(
        self,
        query: str
    ) -> QueryResult:
        """
        Query graph using natural language.
        
        Examples:
        - "What interventions have been tested for diabetes?"
        - "Which studies compare Drug A to placebo?"
        - "What are the outcomes measured for Population X?"
        """
        pass
    
    def find_evidence_gaps(
        self,
        pico: PICOFramework
    ) -> List[EvidenceGap]:
        """Identify evidence gaps for a research question."""
        pass
```

### 12.2 Graph Schema

```cypher
// Node Types
(Study:Study {id, title, year, journal, doi})
(Intervention:Treatment {name, type, dose})
(Population:Population {description, disease, age_group})
(Outcome:Outcome {name, type, timepoint})
(Author:Author {name, affiliation, country})

// Relationship Types
(Study)-[:STUDIED_INTERVENTION]->(Intervention)
(Study)-[:STUDIED_POPULATION]->(Population)
(Study)-[:MEASURED_OUTCOME]->(Outcome)
(Study)-[:AUTHORED_BY]->(Author)
(Intervention)-[:COMPARED_TO]->(Intervention)
(Intervention)-[:TREATS]->(Population)
```

### 12.3 Technical Specifications

| Specification | Requirement |
|--------------|-------------|
| Graph Database | Neo4j 5+ |
| NER Models | PubMedBERT, BioBERT, custom fine-tuned |
| Ontology Linking | MeSH, SNOMED-CT, DrugBank, UMLS |
| Query Language | Cypher + Natural Language interface |
| Update Strategy | Incremental (living reviews) |
| Export Formats | RDF/Turtle, JSON-LD, GraphML |

---

## 13. Data Models & Schemas

### 13.1 Core Data Models

```python
# Citation Model
@dataclass
class Citation:
    id: UUID
    title: str
    abstract: Optional[str]
    authors: List[str]
    journal: Optional[str]
    year: Optional[int]
    doi: Optional[str]
    pmid: Optional[str]
    source_database: str
    raw_record: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

# Study Model (post-extraction)
@dataclass
class Study:
    id: UUID
    citation: Citation
    extraction: ExtractionResult
    rob_assessment: Optional[RoB2Assessment]
    pdf_path: Optional[str]
    inclusion_status: InclusionStatus
    exclusion_reason: Optional[str]

# Review Project Model
@dataclass
class ReviewProject:
    id: UUID
    title: str
    research_question: ResearchQuestion
    protocol: ProtocolDocument
    search_strategies: Dict[str, SearchQuery]
    citations: List[Citation]
    studies: List[Study]
    meta_analyses: List[MetaAnalysisResult]
    manuscript: Optional[Manuscript]
    created_at: datetime
    updated_at: datetime
    owner_id: UUID
    collaborators: List[UUID]
```

### 13.2 Database Schema (PostgreSQL)

```sql
-- Core Tables
CREATE TABLE review_projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(500) NOT NULL,
    description TEXT,
    status VARCHAR(50) DEFAULT 'draft',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    owner_id UUID REFERENCES users(id)
);

CREATE TABLE citations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES review_projects(id),
    title TEXT NOT NULL,
    abstract TEXT,
    authors JSONB,
    journal VARCHAR(500),
    year INTEGER,
    doi VARCHAR(100),
    pmid VARCHAR(20),
    source_database VARCHAR(100),
    raw_record JSONB,
    embedding VECTOR(1536),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE screening_decisions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    citation_id UUID REFERENCES citations(id),
    decision VARCHAR(20) NOT NULL,
    confidence FLOAT,
    reasoning TEXT,
    screened_by VARCHAR(50),
    screened_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE extractions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    citation_id UUID REFERENCES citations(id),
    extraction_data JSONB NOT NULL,
    model_used VARCHAR(100),
    extracted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE rob_assessments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    citation_id UUID REFERENCES citations(id),
    assessment_data JSONB NOT NULL,
    overall_judgment VARCHAR(20),
    assessed_by VARCHAR(50),
    assessed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_citations_project ON citations(project_id);
CREATE INDEX idx_citations_doi ON citations(doi);
CREATE INDEX idx_citations_pmid ON citations(pmid);
CREATE INDEX idx_citations_embedding ON citations USING ivfflat (embedding vector_cosine_ops);
```

---

## 14. API Specifications

### 14.1 REST API Endpoints

```yaml
openapi: 3.0.3
info:
  title: SLR Automation Pipeline API
  version: 1.0.0

paths:
  # Project Management
  /api/v1/projects:
    get:
      summary: List review projects
    post:
      summary: Create new review project
      
  /api/v1/projects/{project_id}:
    get:
      summary: Get project details
    put:
      summary: Update project
    delete:
      summary: Delete project
      
  # Search Strategy
  /api/v1/projects/{project_id}/search-strategy:
    post:
      summary: Generate search strategy from PICO
    get:
      summary: Get current search strategies
      
  /api/v1/projects/{project_id}/search-execute:
    post:
      summary: Execute search across databases
      
  # Citations
  /api/v1/projects/{project_id}/citations:
    get:
      summary: List citations with filtering
    post:
      summary: Import citations (RIS/BibTeX)
      
  /api/v1/projects/{project_id}/deduplicate:
    post:
      summary: Run deduplication
      
  # Screening
  /api/v1/projects/{project_id}/screen:
    post:
      summary: AI screening of citations
      
  /api/v1/projects/{project_id}/screening-decisions:
    get:
      summary: Get screening decisions
    put:
      summary: Update screening decision (human)
      
  # Extraction
  /api/v1/projects/{project_id}/extract:
    post:
      summary: Extract data from PDFs
      
  # Risk of Bias
  /api/v1/projects/{project_id}/rob-assess:
    post:
      summary: Run RoB assessment
      
  # Meta-Analysis
  /api/v1/projects/{project_id}/meta-analysis:
    post:
      summary: Run meta-analysis
      
  # Manuscript
  /api/v1/projects/{project_id}/manuscript:
    post:
      summary: Generate manuscript
    get:
      summary: Get current manuscript
```

### 14.2 WebSocket Events (Real-time Updates)

```typescript
// Client subscribes to project updates
socket.on('project:progress', (data: {
  project_id: string;
  stage: string;
  progress: number;
  message: string;
}) => void);

socket.on('screening:complete', (data: {
  citation_id: string;
  decision: string;
  confidence: number;
}) => void);

socket.on('extraction:complete', (data: {
  citation_id: string;
  fields_extracted: number;
}) => void);
```

---

## 15. Security & Compliance

### 15.1 Authentication & Authorisation

| Requirement | Implementation |
|-------------|----------------|
| Authentication | OAuth 2.0 / OIDC (Auth0, Keycloak) |
| Authorisation | Role-based (Admin, Reviewer, Reader) |
| API Security | JWT tokens with refresh |
| Rate Limiting | Per-user and per-endpoint limits |

### 15.2 Data Protection

| Requirement | Implementation |
|-------------|----------------|
| Encryption at Rest | AES-256 for files, TDE for database |
| Encryption in Transit | TLS 1.3 |
| PII Handling | Anonymisation options |
| Audit Logging | All data access logged |
| Data Retention | Configurable retention policies |

### 15.3 Compliance

| Standard | Applicability |
|----------|---------------|
| GDPR | EU user data |
| HIPAA | If handling PHI |
| SOC 2 Type II | Enterprise deployments |

---

## 16. Performance Requirements

### 16.1 Latency Targets

| Operation | Target Latency |
|-----------|----------------|
| Citation search (1000 results) | < 5 seconds |
| Single abstract screening | < 2 seconds |
| Batch screening (1000) | < 30 minutes |
| PDF retrieval | < 30 seconds |
| Data extraction (single PDF) | < 60 seconds |
| RoB assessment (single study) | < 120 seconds |
| Forest plot generation | < 5 seconds |
| Manuscript section generation | < 30 seconds |

### 16.2 Throughput Targets

| Operation | Target Throughput |
|-----------|-------------------|
| Citation import | 10,000/minute |
| Deduplication | 100,000/5 minutes |
| Abstract screening | 1,000/minute |
| Data extraction | 50 PDFs/hour |
| RoB assessment | 30 studies/hour |

### 16.3 Scalability

| Dimension | Target |
|-----------|--------|
| Concurrent projects | 100+ |
| Citations per project | 100,000+ |
| Concurrent users | 500+ |
| Storage per project | 10 GB (PDFs) |

---

## Appendix A: Glossary

| Term | Definition |
|------|------------|
| **PICO** | Population, Intervention, Comparator, Outcome |
| **RoB 2** | Risk of Bias 2 tool (Cochrane) |
| **PRISMA** | Preferred Reporting Items for Systematic Reviews |
| **GRADE** | Grading of Recommendations Assessment, Development and Evaluation |
| **RAG** | Retrieval-Augmented Generation |
| **NER** | Named Entity Recognition |
| **MeSH** | Medical Subject Headings |
| **EMTREE** | Embase Thesaurus |

---

*End of Technical Specification Document - Version 2*
