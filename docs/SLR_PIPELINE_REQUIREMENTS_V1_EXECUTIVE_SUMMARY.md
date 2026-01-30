# Systematic Literature Review Automation Pipeline
## Technical Requirements Document — Executive Summary (Version 1)

**Document Version:** 1.0  
**Date:** January 2026  
**Status:** Draft for Stakeholder Review

---

## 1. Executive Overview

This document outlines the technical requirements for a comprehensive **AI-powered Systematic Literature Review (SLR) Automation Pipeline**. The system aims to dramatically reduce the time, cost, and human effort required to conduct rigorous systematic reviews while maintaining the gold standard of dual-reviewer methodology with human oversight.

### 1.1 Vision Statement

> Transform the systematic review process from a 6-18 month manual endeavour into a 2-4 week AI-augmented workflow, reducing costs by 70-80% while improving consistency, reproducibility, and evidence quality.

### 1.2 Strategic Value Proposition

| Metric | Current State (Manual) | Target State (AI-Augmented) |
|--------|------------------------|----------------------------|
| Total Review Duration | 6-18 months | 2-4 weeks |
| Title/Abstract Screening | 8-12 weeks | 2-3 days |
| Full-Text Review | 4-8 weeks | 1-2 weeks |
| Data Extraction | 4-6 weeks | 3-5 days |
| Risk of Bias Assessment | 2-4 weeks | 2-3 days |
| Statistical Analysis | 2-4 weeks | 1-3 days |
| Manuscript Writing | 4-8 weeks | 1-2 weeks |
| Estimated Cost (per review) | $50,000-200,000 | $10,000-40,000 |

---

## 2. Pipeline Overview

The SLR Automation Pipeline comprises **10 integrated stages**, each supported by AI/ML capabilities:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    SYSTEMATIC REVIEW AUTOMATION PIPELINE                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌────────────┐ │
│  │  1. RESEARCH │───▶│  2. SEARCH   │───▶│  3. DEDUP-   │───▶│ 4. TITLE/  │ │
│  │   QUESTION   │    │   STRATEGY   │    │   LICATION   │    │  ABSTRACT  │ │
│  │  REFINEMENT  │    │  EXECUTION   │    │              │    │  SCREENING │ │
│  └──────────────┘    └──────────────┘    └──────────────┘    └─────┬──────┘ │
│                                                                     │        │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌─────▼──────┐ │
│  │  8. STATIS-  │◀───│  7. RISK OF  │◀───│  6. DATA     │◀───│ 5. FULL    │ │
│  │    TICAL     │    │     BIAS     │    │  EXTRACTION  │    │   TEXT     │ │
│  │   ANALYSIS   │    │  ASSESSMENT  │    │              │    │   REVIEW   │ │
│  └──────┬───────┘    └──────────────┘    └──────────────┘    └────────────┘ │
│         │                                                                    │
│  ┌──────▼───────┐    ┌──────────────┐    ┌──────────────────────────────┐   │
│  │  9. FOREST   │───▶│ 10. MANUSCRIPT│───▶│    KNOWLEDGE GRAPH ENGINE    │   │
│  │   PLOTS &    │    │    WRITING &  │    │   (Cross-cutting component)  │   │
│  │   FIGURES    │    │  REFERENCING  │    └──────────────────────────────┘   │
│  └──────────────┘    └──────────────┘                                        │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Stage-by-Stage Requirements Summary

### Stage 1: Research Question & Hypothesis Generation

**Objective:** AI-assisted formulation and refinement of PICO(S) framework questions.

| Requirement | Priority | AI Capability |
|-------------|----------|---------------|
| PICO extraction from preliminary literature | High | LLM with RAG |
| Hypothesis generation based on evidence gaps | High | LLM with domain knowledge |
| Question refinement through interactive dialogue | Medium | Conversational AI |
| Protocol template generation (PROSPERO format) | High | Template-based generation |

**Key Deliverable:** Structured PICO statement with rationale and search term suggestions.

---

### Stage 2: Search Strategy Development & Execution

**Objective:** Generate comprehensive, reproducible search strategies across multiple databases.

| Requirement | Priority | AI Capability |
|-------------|----------|---------------|
| Boolean query generation from PICO elements | Critical | NLP + domain ontologies |
| MeSH/EMTREE term mapping | Critical | Medical ontology integration |
| Multi-database query translation (PubMed, Embase, Cochrane, etc.) | Critical | Database-specific adapters |
| Search execution automation via APIs | High | API integration layer |
| Grey literature search automation | Medium | Web scraping + NLP |

**Key Deliverable:** Reproducible search strategies with audit trail and citation exports (RIS/BibTeX).

---

### Stage 3: Deduplication

**Objective:** Intelligent identification and removal of duplicate citations.

| Requirement | Priority | AI Capability |
|-------------|----------|---------------|
| Exact match deduplication (DOI, PMID) | Critical | Rule-based matching |
| Fuzzy matching for near-duplicates | Critical | Embedding similarity + ML |
| Cross-database duplicate detection | High | Entity resolution algorithms |
| Manual review queue for uncertain cases | Medium | Human-in-the-loop UI |

**Key Deliverable:** Deduplicated citation library with transparent merge decisions.

---

### Stage 4: Title & Abstract Screening (Co-Scanning)

**Objective:** AI-augmented dual-screening with human oversight.

| Requirement | Priority | AI Capability |
|-------------|----------|---------------|
| Binary include/exclude classification | Critical | Fine-tuned classifier |
| Confidence scoring for prioritisation | High | Probabilistic output |
| Active learning from human decisions | High | Online learning loop |
| Inter-rater agreement calculation | High | Statistical module |
| Conflict resolution workflow | Critical | Human arbitration UI |

**Key Deliverable:** Screened citations with inclusion rationale and agreement metrics.

---

### Stage 5: Full-Text Review & PDF Retrieval

**Objective:** Automated PDF acquisition and full-text eligibility assessment.

| Requirement | Priority | AI Capability |
|-------------|----------|---------------|
| DOI-based PDF retrieval (Unpaywall, EZProxy) | Critical | Multi-source retriever |
| Full-text eligibility screening | Critical | LLM document analysis |
| Exclusion reason documentation | High | Structured extraction |
| PRISMA flow diagram generation | High | Automated visualisation |

**Key Deliverable:** Full-text corpus with eligibility decisions and exclusion rationale.

---

### Stage 6: Structured Data Extraction

**Objective:** Extract 80+ standardised fields from included studies.

| Requirement | Priority | AI Capability |
|-------------|----------|---------------|
| Schema-guided extraction (PICO, methods, outcomes) | Critical | RAG + structured output |
| Table/figure data extraction | High | Vision-language models |
| Demographics extraction by treatment arm | High | Multi-modal extraction |
| Extraction validation against human | Medium | Quality assurance module |

**Key Deliverable:** Structured JSON/CSV dataset ready for meta-analysis.

---

### Stage 7: Risk of Bias Assessment

**Objective:** AI-powered RoB 2 assessment with evidence-based reasoning.

| Requirement | Priority | AI Capability |
|-------------|----------|---------------|
| Domain-by-domain RoB 2 assessment | Critical | Framework-guided LLM |
| Evidence extraction with citations | Critical | RAG with source tracking |
| Multi-assessor comparison (AI vs human) | High | Agreement statistics |
| RobVis-compatible export | High | Standard format export |

**Key Deliverable:** RoB 2 assessments with reasoning, evidence, and traffic-light visualisations.

---

### Stage 8: Statistical Analysis & Meta-Analysis

**Objective:** Automated statistical synthesis with publication-quality outputs.

| Requirement | Priority | AI Capability |
|-------------|----------|---------------|
| Effect size calculation (OR, RR, MD, SMD) | Critical | Statistical engine |
| Heterogeneity assessment (I², τ²) | Critical | Meta-analysis algorithms |
| Fixed/random effects models | Critical | Statistical modelling |
| Subgroup and sensitivity analyses | High | Automated analysis variants |
| Publication bias assessment | High | Funnel plots, Egger's test |

**Key Deliverable:** Meta-analysis results with forest plots, heterogeneity statistics, and sensitivity analyses.

---

### Stage 9: Forest Plots, Tables & Figures

**Objective:** Generate publication-ready visualisations.

| Requirement | Priority | AI Capability |
|-------------|----------|---------------|
| Forest plot generation | Critical | Visualisation engine |
| GRADE summary of findings tables | High | Automated table generation |
| PRISMA flow diagram | Critical | Diagram generator |
| Risk of bias traffic-light plots | High | RobVis integration |
| Funnel plots and L'Abbé plots | Medium | Statistical visualisation |

**Key Deliverable:** Vector graphics (SVG/PDF) ready for journal submission.

---

### Stage 10: Manuscript Writing & Referencing

**Objective:** AI-assisted manuscript generation with proper citations.

| Requirement | Priority | AI Capability |
|-------------|----------|---------------|
| Section-by-section draft generation | High | LLM with templates |
| PRISMA checklist compliance | Critical | Checklist validation |
| Automatic citation insertion | Critical | Reference management |
| Citation style formatting (APA, Vancouver, etc.) | High | Format converters |
| Plagiarism and AI-content detection avoidance | High | Original text generation |

**Key Deliverable:** Complete manuscript draft with embedded references and PRISMA compliance report.

---

## 4. Knowledge Graph Engine (Cross-Cutting)

**Objective:** Build and maintain a queryable knowledge graph from extracted evidence.

| Requirement | Priority | AI Capability |
|-------------|----------|---------------|
| Entity extraction (interventions, outcomes, populations) | High | Named entity recognition |
| Relationship mapping (causes, treats, associated with) | High | Relation extraction |
| Ontology alignment (MeSH, SNOMED-CT, HPO) | Medium | Ontology linking |
| Graph database storage (Neo4j/RDF) | High | Graph persistence |
| Natural language querying | Medium | Graph-to-text interface |
| Living review updates | Medium | Incremental graph updates |

**Key Deliverable:** Queryable knowledge graph enabling evidence synthesis, gap analysis, and living reviews.

---

## 5. Integration Architecture

```
┌────────────────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE LAYER                                │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   Web App   │  │   CLI Tool  │  │   API/SDK   │  │  Notebooks  │        │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘        │
└─────────┴────────────────┴────────────────┴────────────────┴───────────────┘
                                    │
┌───────────────────────────────────▼────────────────────────────────────────┐
│                        ORCHESTRATION LAYER                                  │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                      Workflow Engine (Temporal/Airflow)              │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└────────────────────────────────────────────────────────────────────────────┘
                                    │
┌───────────────────────────────────▼────────────────────────────────────────┐
│                          AI/ML SERVICES LAYER                               │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────────┐  │
│  │ LLM APIs │ │ Embedding│ │ Document │ │ Vision   │ │  Custom Models   │  │
│  │(GPT/Claude)│ │ Models  │ │ Parsers  │ │ Models   │ │  (fine-tuned)    │  │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────────────┘  │
└────────────────────────────────────────────────────────────────────────────┘
                                    │
┌───────────────────────────────────▼────────────────────────────────────────┐
│                           DATA LAYER                                        │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────────┐  │
│  │ Document │ │  Vector  │ │Relational│ │  Graph   │ │   File Storage   │  │
│  │  Store   │ │   DB     │ │    DB    │ │    DB    │ │   (PDF, RIS)     │  │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────────────┘  │
└────────────────────────────────────────────────────────────────────────────┘
```

---

## 6. Existing Components (Current Repository)

The following modules are already implemented and will be integrated:

| Module | Status | Coverage |
|--------|--------|----------|
| **PDF Retriever** | ✅ Implemented | Stage 5 (PDF acquisition) |
| **RCT Extractor** | ✅ Implemented | Stage 6 (Data extraction) |
| **Risk of Bias** | ✅ Implemented | Stage 7 (RoB 2 assessment) |
| **Covidence Downloader** | ✅ Implemented | Stage 5 (PDF acquisition) |

---

## 7. Success Metrics

| KPI | Target |
|-----|--------|
| Screening sensitivity | ≥95% (vs human gold standard) |
| Extraction accuracy | ≥90% field-level agreement |
| RoB agreement with experts | κ ≥ 0.7 (substantial agreement) |
| Time reduction | ≥70% vs manual process |
| Cost reduction | ≥60% vs outsourced review |
| User satisfaction | ≥4.5/5.0 rating |

---

## 8. Risk Considerations

| Risk | Mitigation |
|------|------------|
| AI hallucination in extraction | RAG with source verification; human validation |
| Regulatory/compliance concerns | Audit trails; explainable AI; human oversight |
| Model bias affecting review outcomes | Diverse training data; multi-model consensus |
| API cost overruns | Token budgeting; caching; efficient prompting |
| Dependency on external AI providers | Multi-provider architecture; local model options |

---

## 9. Recommended Next Steps

1. **Phase 1 (Months 1-3):** Integrate existing modules into unified pipeline
2. **Phase 2 (Months 4-6):** Develop screening and search strategy modules
3. **Phase 3 (Months 7-9):** Build statistical analysis and visualisation engine
4. **Phase 4 (Months 10-12):** Implement manuscript generation and knowledge graph
5. **Phase 5 (Ongoing):** Validation studies, user testing, and continuous improvement

---

## 10. Conclusion

This SLR Automation Pipeline represents a significant advancement in evidence synthesis methodology. By leveraging state-of-the-art AI capabilities while maintaining rigorous human oversight, the system will enable researchers to conduct more systematic reviews, of higher quality, in less time, and at lower cost.

**The future of evidence synthesis is human-AI collaboration.**

---

*Document prepared for stakeholder review. Technical specifications available in Version 2. Implementation details available in Version 3.*
