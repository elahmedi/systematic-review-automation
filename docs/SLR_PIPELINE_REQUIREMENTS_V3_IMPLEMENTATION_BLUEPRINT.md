# Systematic Literature Review Automation Pipeline
## Technical Requirements Document — Implementation Blueprint (Version 3)

**Document Version:** 3.0  
**Date:** January 2026  
**Status:** Implementation Guide for Development Teams  
**Audience:** Project Managers, Tech Leads, DevOps Engineers, Development Teams

---

## Table of Contents

1. [Implementation Strategy](#1-implementation-strategy)
2. [System Architecture Blueprint](#2-system-architecture-blueprint)
3. [Phase 1: Foundation & Integration](#3-phase-1-foundation--integration)
4. [Phase 2: Search & Screening Modules](#4-phase-2-search--screening-modules)
5. [Phase 3: Extraction & Assessment](#5-phase-3-extraction--assessment)
6. [Phase 4: Analysis & Visualisation](#6-phase-4-analysis--visualisation)
7. [Phase 5: Knowledge Graph & Manuscript](#7-phase-5-knowledge-graph--manuscript)
8. [Infrastructure Setup](#8-infrastructure-setup)
9. [Development Workflows](#9-development-workflows)
10. [Testing Strategy](#10-testing-strategy)
11. [Deployment Pipeline](#11-deployment-pipeline)
12. [Cost Estimation & Budgeting](#12-cost-estimation--budgeting)
13. [Risk Management](#13-risk-management)
14. [Team Structure & Responsibilities](#14-team-structure--responsibilities)

---

## 1. Implementation Strategy

### 1.1 Guiding Principles

1. **Incremental Value Delivery**: Each phase delivers usable functionality
2. **Build on Existing Assets**: Integrate the four existing modules early
3. **Human-in-the-Loop First**: Always include human validation workflows
4. **API-First Design**: All components expose REST/GraphQL APIs
5. **Modularity**: Each stage is an independent, replaceable service
6. **Observability**: Comprehensive logging, metrics, and tracing from day one

### 1.2 Implementation Timeline Overview

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                           IMPLEMENTATION TIMELINE                                    │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                      │
│  PHASE 1: Foundation & Integration (Months 1-3)                                     │
│  ════════════════════════════════════════════════                                   │
│  │▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓│                                                  │
│  ├── Core infrastructure setup                                                       │
│  ├── Integrate existing modules (PDF retriever, RCT extractor, RoB assessor)        │
│  ├── Unified API layer                                                               │
│  └── Basic web interface                                                             │
│                                                                                      │
│  PHASE 2: Search & Screening (Months 4-6)                                           │
│  ═════════════════════════════════════════                                          │
│                         │▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓│                           │
│                         ├── PICO refinement module                                   │
│                         ├── Search strategy generator                                │
│                         ├── Multi-database search execution                          │
│                         ├── Deduplication engine                                     │
│                         └── Title/abstract screening                                 │
│                                                                                      │
│  PHASE 3: Extraction & Assessment (Months 7-9)                                      │
│  ═════════════════════════════════════════════                                      │
│                                              │▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓│      │
│                                              ├── Enhanced data extraction            │
│                                              ├── Table/figure extraction             │
│                                              ├── Multi-reviewer workflow             │
│                                              └── PRISMA flow automation              │
│                                                                                      │
│  PHASE 4: Analysis & Visualisation (Months 10-12)                                   │
│  ════════════════════════════════════════════════                                   │
│                                                                  │▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓│  │
│                                                                  ├── Meta-analysis   │
│                                                                  ├── Forest plots    │
│                                                                  └── GRADE tables    │
│                                                                                      │
│  PHASE 5: Knowledge Graph & Manuscript (Months 13-15)                               │
│  ════════════════════════════════════════════════════                               │
│                                                                            │▓▓▓▓▓▓│ │
│                                                                            ├── KG    │
│                                                                            └── MS    │
│                                                                                      │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. System Architecture Blueprint

### 2.1 High-Level Architecture

```
┌────────────────────────────────────────────────────────────────────────────────────┐
│                              PRESENTATION LAYER                                     │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  ┌───────────────┐  │
│  │   Web Dashboard │  │   CLI Tools     │  │   API Gateway   │  │ Jupyter/      │  │
│  │   (React/Next)  │  │   (Python)      │  │   (Kong/Traefik)│  │ Notebooks     │  │
│  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘  └───────┬───────┘  │
└───────────┴────────────────────┴────────────────────┴───────────────────┴──────────┘
                                         │
┌────────────────────────────────────────▼───────────────────────────────────────────┐
│                              APPLICATION LAYER                                      │
│  ┌─────────────────────────────────────────────────────────────────────────────┐   │
│  │                        FastAPI Application Server                            │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────────┐   │   │
│  │  │ Project  │ │ Search   │ │ Screening│ │Extraction│ │ Analysis Service │   │   │
│  │  │ Service  │ │ Service  │ │ Service  │ │ Service  │ │                  │   │   │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────────────┘   │   │
│  └─────────────────────────────────────────────────────────────────────────────┘   │
└────────────────────────────────────────────────────────────────────────────────────┘
                                         │
┌────────────────────────────────────────▼───────────────────────────────────────────┐
│                            ORCHESTRATION LAYER                                      │
│  ┌─────────────────────────────────────────────────────────────────────────────┐   │
│  │                    Temporal.io Workflow Engine                               │   │
│  │  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────────┐    │   │
│  │  │ Search       │ │ Screening    │ │ Extraction   │ │ Analysis         │    │   │
│  │  │ Workflow     │ │ Workflow     │ │ Workflow     │ │ Workflow         │    │   │
│  │  └──────────────┘ └──────────────┘ └──────────────┘ └──────────────────┘    │   │
│  └─────────────────────────────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────────────────────────┐   │
│  │                    Redis / RabbitMQ (Task Queue)                             │   │
│  └─────────────────────────────────────────────────────────────────────────────┘   │
└────────────────────────────────────────────────────────────────────────────────────┘
                                         │
┌────────────────────────────────────────▼───────────────────────────────────────────┐
│                              AI/ML LAYER                                            │
│  ┌────────────────┐ ┌────────────────┐ ┌────────────────┐ ┌────────────────────┐   │
│  │ LLM Gateway    │ │ Embedding      │ │ Document       │ │ Custom Models      │   │
│  │ (LangChain)    │ │ Service        │ │ Intelligence   │ │ (Fine-tuned)       │   │
│  │                │ │                │ │ (GROBID)       │ │                    │   │
│  │ ├─ OpenAI      │ │ ├─ Titan V2    │ │                │ │ ├─ Screening       │   │
│  │ ├─ Anthropic   │ │ ├─ text-emb-3  │ │                │ │ ├─ NER             │   │
│  │ └─ Bedrock     │ │ └─ Custom      │ │                │ │ └─ Relation Ext    │   │
│  └────────────────┘ └────────────────┘ └────────────────┘ └────────────────────┘   │
└────────────────────────────────────────────────────────────────────────────────────┘
                                         │
┌────────────────────────────────────────▼───────────────────────────────────────────┐
│                               DATA LAYER                                            │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────┐  │
│  │ PostgreSQL   │ │ ChromaDB/    │ │ Neo4j        │ │ MinIO/S3     │ │ Redis    │  │
│  │ (Primary)    │ │ Qdrant       │ │ (Knowledge   │ │ (PDFs/Files) │ │ (Cache)  │  │
│  │              │ │ (Vectors)    │ │  Graph)      │ │              │ │          │  │
│  └──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘ └──────────┘  │
│  ┌──────────────────────────────────────────────────────────────────────────────┐  │
│  │                    Elasticsearch (Full-text Search)                          │  │
│  └──────────────────────────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────────────────────────┘
                                         │
┌────────────────────────────────────────▼───────────────────────────────────────────┐
│                            INFRASTRUCTURE LAYER                                     │
│  ┌──────────────────────────────────────────────────────────────────────────────┐  │
│  │                     Kubernetes Cluster (EKS/GKE/AKS)                         │  │
│  │  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐                 │  │
│  │  │ Ingress    │ │ Service    │ │ Prometheus │ │ Grafana    │                 │  │
│  │  │ Controller │ │ Mesh       │ │ + Loki     │ │            │                 │  │
│  │  └────────────┘ └────────────┘ └────────────┘ └────────────┘                 │  │
│  └──────────────────────────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Service Communication

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         SERVICE COMMUNICATION PATTERNS                           │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│  SYNCHRONOUS (REST/gRPC)                    ASYNCHRONOUS (Events/Tasks)         │
│  ════════════════════════                   ═══════════════════════════         │
│                                                                                  │
│  ┌─────────┐  HTTP/JSON  ┌─────────┐       ┌─────────┐  Redis   ┌─────────┐    │
│  │ Client  │────────────▶│ API     │       │ API     │─────────▶│ Worker  │    │
│  │         │◀────────────│ Gateway │       │ Service │          │ Pool    │    │
│  └─────────┘             └─────────┘       └─────────┘          └─────────┘    │
│                                                                                  │
│  Use Cases:                                 Use Cases:                           │
│  • Project CRUD                             • Batch screening                    │
│  • Citation queries                         • PDF retrieval                      │
│  • Real-time screening                      • Data extraction                    │
│  • Status checks                            • Meta-analysis                      │
│                                                                                  │
│  WORKFLOW ORCHESTRATION (Temporal)          EVENT STREAMING (WebSocket)         │
│  ═════════════════════════════════          ═══════════════════════════         │
│                                                                                  │
│  ┌─────────┐  Workflow  ┌─────────┐         ┌─────────┐  Events ┌─────────┐    │
│  │ Temporal│───────────▶│Activity │         │ Server  │────────▶│ Client  │    │
│  │ Server  │◀───────────│ Workers │         │         │         │         │    │
│  └─────────┘            └─────────┘         └─────────┘         └─────────┘    │
│                                                                                  │
│  Use Cases:                                 Use Cases:                           │
│  • Multi-step pipelines                     • Progress updates                   │
│  • Long-running extractions                 • Real-time notifications            │
│  • Retry handling                           • Collaborative editing              │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### 2.3 Directory Structure

```
slr-automation-pipeline/
├── .github/
│   ├── workflows/
│   │   ├── ci.yml
│   │   ├── cd-staging.yml
│   │   └── cd-production.yml
│   └── CODEOWNERS
│
├── apps/
│   ├── web/                          # React/Next.js frontend
│   │   ├── src/
│   │   ├── package.json
│   │   └── Dockerfile
│   │
│   └── api/                          # FastAPI backend
│       ├── src/
│       │   ├── main.py
│       │   ├── config.py
│       │   ├── routers/
│       │   ├── services/
│       │   ├── models/
│       │   └── workflows/
│       ├── pyproject.toml
│       └── Dockerfile
│
├── packages/                         # Shared packages (monorepo)
│   ├── core/                         # Core data models
│   ├── search-engine/                # Search strategy & execution
│   ├── screening/                    # Screening classifiers
│   ├── extraction/                   # Data extraction (existing RCT extractor)
│   ├── risk-of-bias/                 # RoB assessment (existing)
│   ├── pdf-retriever/                # PDF retrieval (existing)
│   ├── meta-analysis/                # Statistical analysis
│   ├── visualisation/                # Charts and plots
│   ├── manuscript/                   # Manuscript generation
│   └── knowledge-graph/              # KG engine
│
├── infrastructure/
│   ├── terraform/                    # IaC for cloud resources
│   ├── kubernetes/                   # K8s manifests
│   │   ├── base/
│   │   ├── staging/
│   │   └── production/
│   └── docker-compose.yml            # Local development
│
├── docs/
│   ├── architecture/
│   ├── api/
│   └── user-guide/
│
├── scripts/
│   ├── setup.sh
│   ├── migrate.py
│   └── seed-data.py
│
├── tests/
│   ├── integration/
│   └── e2e/
│
├── .env.example
├── docker-compose.yml
├── pyproject.toml                    # Root Python config
├── package.json                      # Root Node config (nx/turborepo)
└── README.md
```

---

## 3. Phase 1: Foundation & Integration

### 3.1 Objectives
- Set up core infrastructure
- Integrate existing modules into unified architecture
- Create basic project management API
- Deploy initial web interface

### 3.2 Sprint Breakdown

#### Sprint 1.1: Infrastructure Setup (2 weeks)

**Tasks:**
```yaml
infrastructure:
  - task: Set up Kubernetes cluster (EKS/GKE)
    owner: DevOps
    estimate: 3 days
    
  - task: Configure PostgreSQL (RDS/Cloud SQL)
    owner: DevOps
    estimate: 1 day
    
  - task: Deploy Redis cluster
    owner: DevOps
    estimate: 1 day
    
  - task: Set up MinIO/S3 bucket
    owner: DevOps
    estimate: 0.5 days
    
  - task: Configure CI/CD pipelines (GitHub Actions)
    owner: DevOps
    estimate: 2 days
    
  - task: Set up monitoring (Prometheus/Grafana)
    owner: DevOps
    estimate: 2 days
    
  - task: Configure secrets management (Vault/AWS Secrets)
    owner: DevOps
    estimate: 1 day
```

**Deliverables:**
- [ ] Kubernetes cluster running
- [ ] Databases provisioned
- [ ] CI/CD pipelines functional
- [ ] Monitoring dashboards available

#### Sprint 1.2: Core API Development (2 weeks)

**Tasks:**
```yaml
backend:
  - task: FastAPI project scaffold
    owner: Backend
    estimate: 1 day
    
  - task: Database models and migrations (Alembic)
    owner: Backend
    estimate: 2 days
    
  - task: Project CRUD endpoints
    owner: Backend
    estimate: 2 days
    
  - task: Citation import endpoint (RIS/BibTeX)
    owner: Backend
    estimate: 2 days
    
  - task: Authentication integration (Auth0)
    owner: Backend
    estimate: 2 days
    
  - task: API documentation (OpenAPI)
    owner: Backend
    estimate: 1 day
```

**Deliverables:**
- [ ] `/api/v1/projects` endpoints working
- [ ] `/api/v1/citations` import working
- [ ] Authentication flow complete
- [ ] Swagger documentation available

#### Sprint 1.3: Existing Module Integration (2 weeks)

**Tasks:**
```yaml
integration:
  - task: Refactor PDF Retriever as Python package
    owner: Backend
    estimate: 3 days
    
  - task: Integrate RCT Extractor package
    owner: Backend
    estimate: 2 days
    
  - task: Integrate Risk-of-Bias package
    owner: Backend
    estimate: 2 days
    
  - task: Create unified extraction endpoint
    owner: Backend
    estimate: 2 days
    
  - task: Create unified RoB assessment endpoint
    owner: Backend
    estimate: 1 day
```

**Integration Architecture:**
```python
# packages/extraction/__init__.py
from rct_extractor import RCTExtractor

# packages/risk_of_bias/__init__.py  
from risk_of_bias import RoBAssessor

# apps/api/src/services/extraction_service.py
class ExtractionService:
    def __init__(self):
        self.extractor = RCTExtractor()
        self.rob_assessor = RoBAssessor()
    
    async def process_pdf(self, pdf_path: Path) -> ProcessingResult:
        extraction = await self.extractor.extract_from_pdf(pdf_path)
        rob = await self.rob_assessor.assess_rob2(pdf_path)
        return ProcessingResult(extraction=extraction, rob=rob)
```

#### Sprint 1.4: Basic Web Interface (2 weeks)

**Tasks:**
```yaml
frontend:
  - task: Next.js project scaffold
    owner: Frontend
    estimate: 1 day
    
  - task: Project list/create pages
    owner: Frontend
    estimate: 2 days
    
  - task: Citation import interface
    owner: Frontend
    estimate: 2 days
    
  - task: Citation list with search/filter
    owner: Frontend
    estimate: 2 days
    
  - task: PDF upload and processing UI
    owner: Frontend
    estimate: 2 days
    
  - task: Extraction results viewer
    owner: Frontend
    estimate: 1 day
```

### 3.3 Phase 1 Exit Criteria

- [ ] Create project with title and description
- [ ] Import citations from RIS file
- [ ] Upload PDF and extract data
- [ ] Run RoB assessment on PDF
- [ ] View extraction and RoB results
- [ ] All CI/CD pipelines passing
- [ ] 80% test coverage on core modules

---

## 4. Phase 2: Search & Screening Modules

### 4.1 Objectives
- Develop PICO refinement AI assistant
- Build multi-database search strategy generator
- Implement search execution across databases
- Create intelligent deduplication engine
- Build AI-powered title/abstract screening

### 4.2 Sprint Breakdown

#### Sprint 2.1: PICO Refinement Module (2 weeks)

**Tasks:**
```yaml
pico_module:
  - task: PICO extraction prompts and templates
    owner: ML Engineer
    estimate: 2 days
    
  - task: Question refinement LLM chain
    owner: ML Engineer
    estimate: 3 days
    
  - task: PICO API endpoints
    owner: Backend
    estimate: 2 days
    
  - task: PICO refinement UI wizard
    owner: Frontend
    estimate: 3 days
```

**Implementation Example:**
```python
# packages/search_engine/pico.py
class PICORefiner:
    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client
        self.template = PromptTemplate.from_file("prompts/pico_extraction.txt")
    
    async def extract_pico(self, question: str) -> PICOFramework:
        prompt = self.template.format(question=question)
        response = await self.llm.complete(
            prompt,
            response_format=PICOFramework,
            temperature=0.0
        )
        return response
    
    async def suggest_refinements(
        self,
        pico: PICOFramework,
        domain_context: str
    ) -> List[RefinementSuggestion]:
        # Identify ambiguities and suggest clarifications
        pass
```

#### Sprint 2.2: Search Strategy Generator (3 weeks)

**Tasks:**
```yaml
search_strategy:
  - task: MeSH/EMTREE ontology integration
    owner: Backend
    estimate: 3 days
    
  - task: Boolean query AST builder
    owner: Backend
    estimate: 2 days
    
  - task: Database-specific query translators
    owner: Backend
    estimate: 4 days
    
  - task: Search strategy review UI
    owner: Frontend
    estimate: 3 days
    
  - task: Query export (reproducible format)
    owner: Backend
    estimate: 2 days
```

**Query Translation Example:**
```python
# packages/search_engine/translators.py
class QueryTranslator:
    """Translate generic query AST to database-specific syntax."""
    
    TRANSLATORS = {
        "pubmed": PubMedTranslator(),
        "embase": EmbaseTranslator(),
        "cochrane": CochraneTranslator(),
        "scopus": ScopusTranslator(),
    }
    
    def translate(
        self,
        query_ast: QueryNode,
        target_database: str
    ) -> str:
        translator = self.TRANSLATORS[target_database]
        return translator.translate(query_ast)

class PubMedTranslator:
    def translate(self, node: QueryNode) -> str:
        if node.operator == "TERM":
            field = self._map_field(node.field)
            return f"{node.term}[{field}]"
        elif node.operator in ["AND", "OR", "NOT"]:
            children = [self.translate(c) for c in node.children]
            return f"({f' {node.operator} '.join(children)})"
    
    def _map_field(self, field: str) -> str:
        return {
            "title_abstract": "tiab",
            "mesh": "MeSH Terms",
            "title": "ti",
        }.get(field, "tw")
```

#### Sprint 2.3: Search Execution (2 weeks)

**Tasks:**
```yaml
search_execution:
  - task: PubMed E-utilities client
    owner: Backend
    estimate: 2 days
    
  - task: Embase API client
    owner: Backend
    estimate: 2 days
    
  - task: Cochrane API client
    owner: Backend
    estimate: 2 days
    
  - task: Rate limiting and retry logic
    owner: Backend
    estimate: 1 day
    
  - task: Search results aggregation
    owner: Backend
    estimate: 1 day
    
  - task: Search execution UI
    owner: Frontend
    estimate: 2 days
```

#### Sprint 2.4: Deduplication Engine (2 weeks)

**Tasks:**
```yaml
deduplication:
  - task: Exact match deduplication (DOI/PMID)
    owner: Backend
    estimate: 1 day
    
  - task: Fuzzy title matching
    owner: Backend
    estimate: 2 days
    
  - task: Embedding-based similarity
    owner: ML Engineer
    estimate: 3 days
    
  - task: Merge decision logic
    owner: Backend
    estimate: 1 day
    
  - task: Deduplication review UI
    owner: Frontend
    estimate: 2 days
    
  - task: Deduplication report generation
    owner: Backend
    estimate: 1 day
```

#### Sprint 2.5: Title/Abstract Screening (3 weeks)

**Tasks:**
```yaml
screening:
  - task: Screening classifier prompts
    owner: ML Engineer
    estimate: 2 days
    
  - task: Confidence calibration
    owner: ML Engineer
    estimate: 2 days
    
  - task: Active learning pipeline
    owner: ML Engineer
    estimate: 3 days
    
  - task: Dual-reviewer workflow
    owner: Backend
    estimate: 3 days
    
  - task: Agreement metrics calculation
    owner: Backend
    estimate: 1 day
    
  - task: Screening interface (Covidence-like)
    owner: Frontend
    estimate: 4 days
    
  - task: Conflict resolution UI
    owner: Frontend
    estimate: 2 days
```

**Screening UI Wireframe:**
```
┌─────────────────────────────────────────────────────────────────────────────┐
│  SCREENING QUEUE                                                    [1/500] │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │ Effect of metformin on glycemic control in type 2 diabetes:           │ │
│  │ a randomized controlled trial                                          │ │
│  │                                                                        │ │
│  │ Authors: Smith J, Johnson K, Williams L et al.                        │ │
│  │ Journal: Diabetes Care, 2024                                          │ │
│  │ DOI: 10.1234/dc.2024.12345                                            │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                                                              │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │ ABSTRACT                                                               │ │
│  │                                                                        │ │
│  │ Background: Type 2 diabetes mellitus affects millions worldwide...    │ │
│  │ Methods: We conducted a double-blind, placebo-controlled RCT...       │ │
│  │ Results: The intervention group showed significant improvement...      │ │
│  │ Conclusion: Metformin demonstrated efficacy in...                     │ │
│  │                                                                        │ │
│  │ [Highlight: RCT] [Highlight: placebo-controlled] [Highlight: diabetes]│ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                                                              │
│  AI SUGGESTION: INCLUDE (Confidence: 92%)                                   │
│  Reason: RCT design, relevant population, outcome aligned with criteria     │
│                                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │   INCLUDE    │  │   EXCLUDE    │  │   UNSURE     │  │   SKIP       │    │
│  │     (I)      │  │     (E)      │  │     (U)      │  │    (S)       │    │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘    │
│                                                                              │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │ EXCLUSION REASON (if excluding):                                       │ │
│  │ ○ Wrong population  ○ Wrong intervention  ○ Wrong outcome             │ │
│  │ ○ Wrong study design  ○ Duplicate  ○ Other: ____________              │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 4.3 Phase 2 Exit Criteria

- [ ] Generate PICO from free-text question
- [ ] Generate PubMed/Embase/Cochrane search strategies
- [ ] Execute searches and import results
- [ ] Deduplicate citations with >99% accuracy
- [ ] Screen 1000 abstracts in <30 minutes
- [ ] Achieve κ ≥ 0.8 with human reviewers
- [ ] Calculate inter-rater agreement

---

## 5. Phase 3: Extraction & Assessment

### 5.1 Objectives
- Enhance existing extraction with table/figure support
- Build multi-reviewer extraction workflow
- Automate PRISMA flow diagram generation
- Add full-text eligibility screening

### 5.2 Sprint Breakdown

#### Sprint 3.1: Enhanced Extraction (3 weeks)

**Tasks:**
```yaml
extraction:
  - task: Vision-language table extraction
    owner: ML Engineer
    estimate: 4 days
    
  - task: Figure data extraction (forest plots)
    owner: ML Engineer
    estimate: 3 days
    
  - task: Demographics by treatment arm
    owner: Backend
    estimate: 2 days
    
  - task: Extraction validation module
    owner: Backend
    estimate: 2 days
    
  - task: Extraction comparison UI
    owner: Frontend
    estimate: 3 days
```

#### Sprint 3.2: Multi-Reviewer Workflow (2 weeks)

**Tasks:**
```yaml
workflow:
  - task: Reviewer assignment algorithm
    owner: Backend
    estimate: 2 days
    
  - task: Extraction discrepancy detection
    owner: Backend
    estimate: 2 days
    
  - task: Consensus resolution workflow
    owner: Backend
    estimate: 2 days
    
  - task: Reviewer dashboard
    owner: Frontend
    estimate: 3 days
```

#### Sprint 3.3: PRISMA Automation (2 weeks)

**Tasks:**
```yaml
prisma:
  - task: PRISMA 2020 flow tracking
    owner: Backend
    estimate: 2 days
    
  - task: Exclusion reason categorisation
    owner: Backend
    estimate: 1 day
    
  - task: SVG flow diagram generator
    owner: Backend
    estimate: 3 days
    
  - task: Interactive PRISMA editor
    owner: Frontend
    estimate: 3 days
```

### 5.3 Phase 3 Exit Criteria

- [ ] Extract data from tables in PDFs
- [ ] Extract effect sizes from forest plot images
- [ ] Dual-extraction with discrepancy flagging
- [ ] Auto-generate PRISMA flow diagram
- [ ] Full-text eligibility screening
- [ ] Export to Excel/CSV with all fields

---

## 6. Phase 4: Analysis & Visualisation

### 6.1 Objectives
- Build meta-analysis statistical engine
- Generate publication-quality forest plots
- Create GRADE summary of findings tables
- Implement sensitivity and subgroup analyses

### 6.2 Sprint Breakdown

#### Sprint 4.1: Meta-Analysis Engine (3 weeks)

**Tasks:**
```yaml
meta_analysis:
  - task: Effect size calculators (OR, RR, MD, SMD)
    owner: Backend/Stats
    estimate: 3 days
    
  - task: Fixed effects models (IV, MH, Peto)
    owner: Backend/Stats
    estimate: 3 days
    
  - task: Random effects models (DL, REML)
    owner: Backend/Stats
    estimate: 3 days
    
  - task: Heterogeneity statistics
    owner: Backend/Stats
    estimate: 2 days
    
  - task: Meta-analysis configuration UI
    owner: Frontend
    estimate: 3 days
```

**Implementation:**
```python
# packages/meta_analysis/engine.py
import numpy as np
from scipy import stats

class MetaAnalysisEngine:
    def fixed_effects_iv(
        self,
        effects: np.ndarray,
        variances: np.ndarray
    ) -> MetaAnalysisResult:
        """Inverse variance fixed effects."""
        weights = 1 / variances
        pooled_effect = np.sum(weights * effects) / np.sum(weights)
        pooled_variance = 1 / np.sum(weights)
        pooled_se = np.sqrt(pooled_variance)
        
        ci_lower = pooled_effect - 1.96 * pooled_se
        ci_upper = pooled_effect + 1.96 * pooled_se
        
        # Heterogeneity
        q = np.sum(weights * (effects - pooled_effect) ** 2)
        df = len(effects) - 1
        i_squared = max(0, (q - df) / q * 100)
        
        return MetaAnalysisResult(
            pooled_effect=pooled_effect,
            ci_lower=ci_lower,
            ci_upper=ci_upper,
            q_statistic=q,
            i_squared=i_squared,
            model="fixed_iv"
        )
    
    def random_effects_dl(
        self,
        effects: np.ndarray,
        variances: np.ndarray
    ) -> MetaAnalysisResult:
        """DerSimonian-Laird random effects."""
        # First, run fixed effects to get Q
        fixed = self.fixed_effects_iv(effects, variances)
        
        # Calculate tau-squared
        weights = 1 / variances
        c = np.sum(weights) - np.sum(weights ** 2) / np.sum(weights)
        tau_squared = max(0, (fixed.q_statistic - len(effects) + 1) / c)
        
        # Random effects weights
        re_weights = 1 / (variances + tau_squared)
        pooled_effect = np.sum(re_weights * effects) / np.sum(re_weights)
        pooled_variance = 1 / np.sum(re_weights)
        pooled_se = np.sqrt(pooled_variance)
        
        return MetaAnalysisResult(
            pooled_effect=pooled_effect,
            ci_lower=pooled_effect - 1.96 * pooled_se,
            ci_upper=pooled_effect + 1.96 * pooled_se,
            tau_squared=tau_squared,
            i_squared=fixed.i_squared,
            model="random_dl"
        )
```

#### Sprint 4.2: Forest Plot Generator (2 weeks)

**Tasks:**
```yaml
visualisation:
  - task: Forest plot SVG renderer
    owner: Frontend/Backend
    estimate: 4 days
    
  - task: Subgroup forest plots
    owner: Backend
    estimate: 2 days
    
  - task: Customisation options UI
    owner: Frontend
    estimate: 2 days
    
  - task: Export to PDF/PNG
    owner: Backend
    estimate: 2 days
```

#### Sprint 4.3: Additional Analyses (2 weeks)

**Tasks:**
```yaml
analyses:
  - task: Sensitivity analyses (leave-one-out)
    owner: Backend
    estimate: 2 days
    
  - task: Subgroup analysis
    owner: Backend
    estimate: 2 days
    
  - task: Publication bias (funnel, Egger's)
    owner: Backend
    estimate: 2 days
    
  - task: GRADE assessment module
    owner: Backend
    estimate: 3 days
```

### 6.3 Phase 4 Exit Criteria

- [ ] Run fixed and random effects meta-analysis
- [ ] Generate Cochrane-style forest plots
- [ ] Perform subgroup and sensitivity analyses
- [ ] Assess publication bias
- [ ] Export GRADE summary of findings
- [ ] All plots exportable as SVG/PDF

---

## 7. Phase 5: Knowledge Graph & Manuscript

### 7.1 Objectives
- Build knowledge graph from extracted entities
- Implement natural language graph querying
- Create AI-assisted manuscript generation
- Ensure PRISMA compliance verification

### 7.2 Sprint Breakdown

#### Sprint 5.1: Knowledge Graph (3 weeks)

**Tasks:**
```yaml
knowledge_graph:
  - task: Neo4j schema design
    owner: Backend
    estimate: 2 days
    
  - task: Entity extraction pipeline (NER)
    owner: ML Engineer
    estimate: 4 days
    
  - task: Relation extraction
    owner: ML Engineer
    estimate: 4 days
    
  - task: Ontology linking (MeSH, SNOMED)
    owner: ML Engineer
    estimate: 3 days
    
  - task: Graph query API
    owner: Backend
    estimate: 2 days
    
  - task: Graph visualisation UI
    owner: Frontend
    estimate: 3 days
```

**Graph Schema:**
```cypher
// Neo4j Schema
CREATE CONSTRAINT study_id IF NOT EXISTS
FOR (s:Study) REQUIRE s.id IS UNIQUE;

CREATE CONSTRAINT intervention_name IF NOT EXISTS
FOR (i:Intervention) REQUIRE i.name IS UNIQUE;

// Example queries
// Find all interventions for a condition
MATCH (i:Intervention)-[:TREATS]->(p:Population {disease: 'Type 2 Diabetes'})
RETURN i.name, COUNT(*) as study_count
ORDER BY study_count DESC;

// Find evidence gaps
MATCH (i:Intervention)-[:STUDIED_IN]->(s:Study)-[:MEASURED]->(o:Outcome)
WHERE NOT (i)-[:COMPARED_TO]->(:Intervention {name: 'Placebo'})
RETURN i.name, o.name
```

#### Sprint 5.2: Manuscript Generation (3 weeks)

**Tasks:**
```yaml
manuscript:
  - task: Section templates (Introduction, Methods, etc.)
    owner: ML Engineer
    estimate: 3 days
    
  - task: Citation insertion logic
    owner: Backend
    estimate: 2 days
    
  - task: PRISMA compliance checker
    owner: Backend
    estimate: 2 days
    
  - task: Multi-format export (DOCX, LaTeX, MD)
    owner: Backend
    estimate: 2 days
    
  - task: Manuscript editor UI
    owner: Frontend
    estimate: 4 days
    
  - task: Revision tracking
    owner: Backend
    estimate: 2 days
```

### 7.3 Phase 5 Exit Criteria

- [ ] Build knowledge graph from review data
- [ ] Query graph with natural language
- [ ] Generate complete manuscript draft
- [ ] Insert citations automatically
- [ ] Verify PRISMA compliance
- [ ] Export to DOCX/LaTeX

---

## 8. Infrastructure Setup

### 8.1 Local Development Environment

```yaml
# docker-compose.yml
version: '3.8'

services:
  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: slr_pipeline
      POSTGRES_USER: slr_user
      POSTGRES_PASSWORD: slr_password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  neo4j:
    image: neo4j:5-community
    environment:
      NEO4J_AUTH: neo4j/password
    ports:
      - "7474:7474"
      - "7687:7687"
    volumes:
      - neo4j_data:/data

  minio:
    image: minio/minio:latest
    command: server /data --console-address ":9001"
    environment:
      MINIO_ROOT_USER: minioadmin
      MINIO_ROOT_PASSWORD: minioadmin
    ports:
      - "9000:9000"
      - "9001:9001"
    volumes:
      - minio_data:/data

  elasticsearch:
    image: elasticsearch:8.11.0
    environment:
      - discovery.type=single-node
      - xpack.security.enabled=false
    ports:
      - "9200:9200"
    volumes:
      - es_data:/usr/share/elasticsearch/data

  grobid:
    image: grobid/grobid:0.8.2.1-crf
    ports:
      - "8070:8070"

  temporal:
    image: temporalio/auto-setup:1.22
    ports:
      - "7233:7233"
    depends_on:
      - postgres

  api:
    build: ./apps/api
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://slr_user:slr_password@postgres:5432/slr_pipeline
      REDIS_URL: redis://redis:6379
      NEO4J_URI: bolt://neo4j:7687
      MINIO_ENDPOINT: minio:9000
      OPENAI_API_KEY: ${OPENAI_API_KEY}
    depends_on:
      - postgres
      - redis
      - neo4j
      - minio

  web:
    build: ./apps/web
    ports:
      - "3000:3000"
    environment:
      NEXT_PUBLIC_API_URL: http://localhost:8000
    depends_on:
      - api

volumes:
  postgres_data:
  neo4j_data:
  minio_data:
  es_data:
```

### 8.2 Kubernetes Production Setup

```yaml
# infrastructure/kubernetes/base/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: slr-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: slr-api
  template:
    metadata:
      labels:
        app: slr-api
    spec:
      containers:
        - name: api
          image: slr-pipeline/api:latest
          ports:
            - containerPort: 8000
          env:
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: slr-secrets
                  key: database-url
            - name: OPENAI_API_KEY
              valueFrom:
                secretKeyRef:
                  name: slr-secrets
                  key: openai-api-key
          resources:
            requests:
              memory: "512Mi"
              cpu: "250m"
            limits:
              memory: "2Gi"
              cpu: "1000m"
          livenessProbe:
            httpGet:
              path: /health
              port: 8000
            initialDelaySeconds: 10
            periodSeconds: 5
          readinessProbe:
            httpGet:
              path: /ready
              port: 8000
            initialDelaySeconds: 5
            periodSeconds: 3
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: slr-api-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: slr-api
  minReplicas: 2
  maxReplicas: 10
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
```

---

## 9. Development Workflows

### 9.1 Git Branching Strategy

```
main (production)
  │
  ├── develop (staging)
  │     │
  │     ├── feature/search-strategy
  │     ├── feature/screening-module
  │     ├── feature/meta-analysis
  │     │
  │     └── bugfix/extraction-error
  │
  └── release/v1.0.0
```

### 9.2 Code Review Guidelines

```markdown
## Pull Request Checklist

- [ ] Code follows project style guide
- [ ] Tests added/updated for new functionality
- [ ] Documentation updated
- [ ] No secrets committed
- [ ] CI pipeline passes
- [ ] Performance impact considered
- [ ] Security implications reviewed
```

### 9.3 Commit Message Convention

```
type(scope): subject

Types: feat, fix, docs, style, refactor, test, chore
Scope: search, screening, extraction, rob, meta, kg, web, api

Examples:
feat(screening): add active learning loop
fix(extraction): handle malformed PDF tables
docs(api): update OpenAPI specification
```

---

## 10. Testing Strategy

### 10.1 Test Pyramid

```
                    ┌───────────────┐
                    │    E2E Tests  │  (10%)
                    │   (Playwright)│
                   ┌┴───────────────┴┐
                   │ Integration Tests│  (20%)
                   │    (pytest)      │
                  ┌┴──────────────────┴┐
                  │    Unit Tests       │  (70%)
                  │    (pytest/jest)    │
                  └────────────────────┘
```

### 10.2 Test Categories

```python
# Unit test example
def test_effect_size_calculation():
    calculator = EffectSizeCalculator()
    
    or_result = calculator.calculate_odds_ratio(
        events_treatment=20, n_treatment=100,
        events_control=10, n_control=100
    )
    
    assert abs(or_result.effect - 2.25) < 0.01
    assert or_result.ci_lower < or_result.effect < or_result.ci_upper

# Integration test example
@pytest.mark.integration
async def test_extraction_pipeline():
    service = ExtractionService()
    result = await service.process_pdf(Path("tests/fixtures/sample_rct.pdf"))
    
    assert result.extraction.title is not None
    assert result.rob.overall_judgment in ["Low", "Some concerns", "High"]

# E2E test example
async def test_create_project_and_import_citations(page: Page):
    await page.goto("/projects/new")
    await page.fill('input[name="title"]', "Test Review")
    await page.click('button[type="submit"]')
    
    await page.click('text=Import Citations')
    await page.set_input_files('input[type="file"]', "tests/fixtures/citations.ris")
    await page.click('text=Import')
    
    await expect(page.locator(".citation-count")).to_have_text("150")
```

### 10.3 Test Data Management

```yaml
# tests/fixtures/README.md
fixtures/
  ├── citations/
  │   ├── sample_10.ris          # 10 diverse citations
  │   ├── duplicates_20.ris      # 20 citations with duplicates
  │   └── large_1000.ris         # 1000 citations for performance
  │
  ├── pdfs/
  │   ├── rct_standard.pdf       # Standard RCT paper
  │   ├── rct_with_tables.pdf    # RCT with complex tables
  │   └── rct_poor_quality.pdf   # Low-quality scan
  │
  └── expected_outputs/
      ├── extraction_rct_standard.json
      └── rob_rct_standard.json
```

---

## 11. Deployment Pipeline

### 11.1 CI/CD Workflow

```yaml
# .github/workflows/ci.yml
name: CI Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - name: Lint
        run: |
          pip install ruff mypy
          ruff check .
          mypy apps/api/src

  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_PASSWORD: test
        ports:
          - 5432:5432
    steps:
      - uses: actions/checkout@v4
      - name: Test
        run: |
          pip install -e ".[test]"
          pytest --cov=src --cov-report=xml

  build:
    needs: [lint, test]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Build Docker images
        run: |
          docker build -t slr-api:${{ github.sha }} ./apps/api
          docker build -t slr-web:${{ github.sha }} ./apps/web
      - name: Push to registry
        run: |
          docker push slr-api:${{ github.sha }}
          docker push slr-web:${{ github.sha }}

  deploy-staging:
    needs: build
    if: github.ref == 'refs/heads/develop'
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to staging
        run: |
          kubectl set image deployment/slr-api api=slr-api:${{ github.sha }}
          kubectl rollout status deployment/slr-api

  deploy-production:
    needs: build
    if: github.ref == 'refs/heads/main'
    environment: production
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to production
        run: |
          kubectl set image deployment/slr-api api=slr-api:${{ github.sha }}
          kubectl rollout status deployment/slr-api
```

---

## 12. Cost Estimation & Budgeting

### 12.1 Infrastructure Costs (Monthly)

| Resource | Specification | Cost (USD) |
|----------|---------------|------------|
| **Kubernetes (EKS)** | 3 x m5.large nodes | ~$300 |
| **PostgreSQL (RDS)** | db.r5.large, 100GB | ~$200 |
| **Redis (ElastiCache)** | cache.r5.large | ~$150 |
| **Neo4j (EC2)** | r5.large, 100GB EBS | ~$180 |
| **S3 Storage** | 500GB | ~$12 |
| **Data Transfer** | 500GB out | ~$45 |
| **Load Balancer** | ALB | ~$25 |
| **Monitoring** | CloudWatch | ~$30 |
| **TOTAL Infrastructure** | | **~$942/month** |

### 12.2 AI/API Costs (Per Review)

| Operation | Model | Cost/Unit | Units/Review | Cost |
|-----------|-------|-----------|--------------|------|
| PICO Refinement | GPT-4o | $0.01/1K tokens | 10K | $0.10 |
| Search Generation | GPT-4o | $0.01/1K tokens | 20K | $0.20 |
| Abstract Screening | GPT-4o-mini | $0.0015/1K tokens | 500K | $0.75 |
| Data Extraction | Claude Opus | $0.015/1K tokens | 200K | $3.00 |
| RoB Assessment | GPT-4o | $0.01/1K tokens | 100K | $1.00 |
| Manuscript Gen | Claude Opus | $0.015/1K tokens | 50K | $0.75 |
| Embeddings | text-embed-3 | $0.0001/1K tokens | 1M | $0.10 |
| **TOTAL AI/Review** | | | | **~$6-10** |

### 12.3 Total Cost of Ownership

| Review Size | Citations | AI Cost | Infra (prorated) | Total |
|-------------|-----------|---------|------------------|-------|
| Small | 1,000 | ~$8 | $5 | ~$13 |
| Medium | 5,000 | ~$25 | $15 | ~$40 |
| Large | 20,000 | ~$80 | $50 | ~$130 |

---

## 13. Risk Management

### 13.1 Technical Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| LLM API downtime | Medium | High | Multi-provider fallback |
| Extraction accuracy issues | Medium | High | Human validation workflow |
| Database performance | Low | High | Query optimisation, indexing |
| Security breach | Low | Critical | SOC 2 compliance, audits |
| Cost overrun on AI APIs | Medium | Medium | Token budgeting, caching |

### 13.2 Project Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Scope creep | High | Medium | Strict sprint planning |
| Key person dependency | Medium | High | Documentation, pair programming |
| Integration complexity | Medium | Medium | API-first design |
| Timeline slippage | Medium | Medium | Buffer time in estimates |

### 13.3 Contingency Plans

```yaml
contingency_plans:
  llm_provider_failure:
    trigger: "OpenAI API unavailable for >1 hour"
    action: "Switch to Anthropic Claude via LangChain"
    rollback: "Automatic when OpenAI recovers"
    
  database_failure:
    trigger: "PostgreSQL unresponsive"
    action: "Failover to read replica"
    rollback: "Promote replica to primary"
    
  cost_overrun:
    trigger: "Monthly AI costs exceed 150% of budget"
    action: "Enable token limiting, disable non-essential features"
    rollback: "Remove limits when budget allows"
```

---

## 14. Team Structure & Responsibilities

### 14.1 Recommended Team

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            TEAM STRUCTURE                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  PRODUCT OWNER (1)                                                          │
│  └── Requirements, prioritisation, stakeholder communication                │
│                                                                              │
│  TECH LEAD (1)                                                              │
│  └── Architecture, code review, technical decisions                         │
│                                                                              │
│  BACKEND ENGINEERS (2-3)                                                    │
│  ├── Core API development                                                   │
│  ├── Database design                                                        │
│  └── Integration work                                                       │
│                                                                              │
│  ML ENGINEERS (2)                                                           │
│  ├── LLM prompt engineering                                                 │
│  ├── Model fine-tuning                                                      │
│  └── Knowledge graph                                                        │
│                                                                              │
│  FRONTEND ENGINEERS (2)                                                     │
│  ├── Web application                                                        │
│  └── Visualisation components                                               │
│                                                                              │
│  DEVOPS ENGINEER (1)                                                        │
│  └── Infrastructure, CI/CD, monitoring                                      │
│                                                                              │
│  QA ENGINEER (1)                                                            │
│  └── Test automation, quality assurance                                     │
│                                                                              │
│  DOMAIN EXPERT (0.5 FTE)                                                    │
│  └── Systematic review methodology consultation                             │
│                                                                              │
│  TOTAL: 10-12 FTE                                                           │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 14.2 Communication Cadence

| Meeting | Frequency | Attendees | Purpose |
|---------|-----------|-----------|---------|
| Daily Standup | Daily | All devs | Sync, blockers |
| Sprint Planning | Bi-weekly | All | Plan sprint |
| Sprint Review | Bi-weekly | All + stakeholders | Demo |
| Tech Sync | Weekly | Tech lead + seniors | Architecture |
| Stakeholder Update | Monthly | PO + stakeholders | Progress |

---

## Appendix A: Quick Reference Commands

```bash
# Local Development
docker-compose up -d
cd apps/api && python -m uvicorn main:app --reload
cd apps/web && npm run dev

# Testing
pytest apps/api/tests
npm run test --workspace=apps/web
npm run e2e --workspace=apps/web

# Database Migrations
cd apps/api && alembic upgrade head
cd apps/api && alembic revision --autogenerate -m "description"

# Kubernetes
kubectl apply -k infrastructure/kubernetes/staging
kubectl get pods -n slr-pipeline
kubectl logs -f deployment/slr-api

# Monitoring
kubectl port-forward svc/grafana 3000:3000
kubectl port-forward svc/prometheus 9090:9090
```

---

## Appendix B: Environment Variables

```bash
# .env.example

# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/slr_pipeline

# Redis
REDIS_URL=redis://localhost:6379

# Neo4j
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password

# Object Storage
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin

# AI Providers
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_REGION=us-east-1

# Authentication
AUTH0_DOMAIN=...
AUTH0_CLIENT_ID=...
AUTH0_CLIENT_SECRET=...

# External APIs
UNPAYWALL_EMAIL=your@email.com
EZPROXY_PREFIX=https://ezproxy.library.edu/login?url=

# Feature Flags
ENABLE_KNOWLEDGE_GRAPH=true
ENABLE_MANUSCRIPT_GENERATION=true
```

---

*End of Implementation Blueprint Document - Version 3*
