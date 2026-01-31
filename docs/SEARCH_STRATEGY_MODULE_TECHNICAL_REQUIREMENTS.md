# Search Strategy Module
## Technical Requirements Document — Build Guide

**Purpose:** Generate professional search strategy documents and PROSPERO registration protocols  
**Target Outputs:**
1. Search Strategy Document (PDF/DOCX) — Montreal Children's Hospital format
2. PROSPERO Protocol — Copy-paste ready for registration

**Build Time:** ~3 weeks for MVP

---

## 1. Target Deliverable Specifications

### Deliverable 1: Search Strategy Document

The module must produce a document with two sections:

### Section A: Search Summary (1 page)
```
┌─────────────────────────────────────────────────────────────────────────────┐
│  [INSTITUTION LOGO/HEADER]                                                  │
│                                                                             │
│                        {REVIEW TITLE}                                       │
│                      ──────────────────                                     │
│                       Systematic Review                                     │
│                                                                             │
│  Assigned To                                                                │
│  ──────────────────────────────────────────────────────────────────────     │
│  {List of reviewers}                                                        │
│                                                                             │
│  About the Search                                                           │
│  ──────────────────────────────────────────────────────────────────────     │
│                                                                             │
│  Search Methodology                                                         │
│  A senior medical librarian searched the following databases from           │
│  inception until {DATE}: {DATABASE LIST}.                                   │
│                                                                             │
│  The search strategy used variations in text words found in the title,      │
│  abstract or keyword fields, and relevant subject headings to retrieve      │
│  articles looking at {TOPIC DESCRIPTION}. See Supplementary material        │
│  for full search strategy.                                                  │
│                                                                             │
│  PRISMA Numbers                                                             │
│  ──────────────────────────────────────────────────────────────────────     │
│  • {N} found before duplicate removal                                       │
│  • {N} after duplicate removal                                              │
│                                                                             │
│  Duplication & Removal of Records                                           │
│  ──────────────────────────────────────────────────────────────────────     │
│  Duplicates were removed using {METHOD}, followed by manual verification.   │
│                                                                             │
│  ┌─────────────────────┬────────────────────┬─────────────────────────┐    │
│  │ Database            │ Before Dedup       │ After Dedup             │    │
│  ├─────────────────────┼────────────────────┼─────────────────────────┤    │
│  │ Medline             │ 3633               │ 3628                    │    │
│  │ Embase              │ 2565               │ 2463                    │    │
│  │ ...                 │ ...                │ ...                     │    │
│  ├─────────────────────┼────────────────────┼─────────────────────────┤    │
│  │ TOTALS              │ {N}                │ {N}                     │    │
│  └─────────────────────┴────────────────────┴─────────────────────────┘    │
│                                                                             │
│  ───────────────────────────────────────────────────────────────────────    │
│  {Page number}        {Author, Credentials}              {Last Updated}    │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Section B: Supplementary Material (N pages)
```
┌─────────────────────────────────────────────────────────────────────────────┐
│  Databases Searched (To use this section as the Supplementary material)     │
│                                                                             │
│  {DATABASE NAME} [{PLATFORM}] ({DATE})                                      │
│  ──────────────────────────────────────────────────────────────────────     │
│  ┌─────┬────────────────────────────────────────────────────────┬─────────┐│
│  │ #   │ Query                                                  │ Results ││
│  ├─────┼────────────────────────────────────────────────────────┼─────────┤│
│  │ S45 │ S44 AND S21                                            │ 41      ││
│  │ S44 │ S43 OR S42 OR S41 OR S40 OR S39 OR S38 OR S37 OR S36   │ 250,627 ││
│  │     │ OR S35 OR S34 OR S33 OR S32 OR S31 OR S29 OR S30 OR    │         ││
│  │     │ S28 OR S27 OR S26 OR S25 OR S24 OR S23 OR S22          │         ││
│  │ S43 │ TI((pectus or chest) N1 (funnel or sunken or           │ 51      ││
│  │     │ excavatum or carinatum)) OR AB((pectus or chest) N1    │         ││
│  │     │ (funnel or sunken or excavatum or carinatum))          │         ││
│  │ ... │ ...                                                    │ ...     ││
│  └─────┴────────────────────────────────────────────────────────┴─────────┘│
│                                                                             │
│  [Repeat for each database]                                                 │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### Deliverable 2: PROSPERO Protocol (Copy-Paste Ready)

Generate a structured document with all PROSPERO registration fields pre-filled. User copies each field directly into the PROSPERO web form.

**Output Format:** Markdown/TXT with labeled fields

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    PROSPERO REGISTRATION PROTOCOL                            │
│                    ════════════════════════════════                          │
│                                                                              │
│  Generated: {DATE}                                                           │
│  Review Title: {TITLE}                                                       │
│                                                                              │
│  ═══════════════════════════════════════════════════════════════════════    │
│  INSTRUCTIONS: Copy each field below directly into the corresponding        │
│  PROSPERO form field at https://www.crd.york.ac.uk/prospero/                │
│  ═══════════════════════════════════════════════════════════════════════    │
│                                                                              │
│  ───────────────────────────────────────────────────────────────────────    │
│  1. REVIEW TITLE *                                                          │
│  ───────────────────────────────────────────────────────────────────────    │
│  {Generated title in PROSPERO format}                                       │
│                                                                              │
│  ───────────────────────────────────────────────────────────────────────    │
│  2. ORIGINAL LANGUAGE TITLE                                                 │
│  ───────────────────────────────────────────────────────────────────────    │
│  {Same as above or translated}                                              │
│                                                                              │
│  ───────────────────────────────────────────────────────────────────────    │
│  3. ANTICIPATED OR ACTUAL START DATE *                                      │
│  ───────────────────────────────────────────────────────────────────────    │
│  {DD/MM/YYYY}                                                               │
│                                                                              │
│  ───────────────────────────────────────────────────────────────────────    │
│  4. ANTICIPATED COMPLETION DATE *                                           │
│  ───────────────────────────────────────────────────────────────────────    │
│  {DD/MM/YYYY}                                                               │
│                                                                              │
│  ───────────────────────────────────────────────────────────────────────    │
│  5. STAGE OF REVIEW AT TIME OF REGISTRATION                                 │
│  ───────────────────────────────────────────────────────────────────────    │
│  {Review stage description}                                                 │
│                                                                              │
│  ───────────────────────────────────────────────────────────────────────    │
│  6. NAMED CONTACT *                                                         │
│  ───────────────────────────────────────────────────────────────────────    │
│  {Contact person name}                                                      │
│                                                                              │
│  ───────────────────────────────────────────────────────────────────────    │
│  7. NAMED CONTACT EMAIL *                                                   │
│  ───────────────────────────────────────────────────────────────────────    │
│  {email@institution.edu}                                                    │
│                                                                              │
│  ───────────────────────────────────────────────────────────────────────    │
│  8. NAMED CONTACT ADDRESS                                                   │
│  ───────────────────────────────────────────────────────────────────────    │
│  {Full institutional address}                                               │
│                                                                              │
│  ───────────────────────────────────────────────────────────────────────    │
│  9. NAMED CONTACT ORCID                                                     │
│  ───────────────────────────────────────────────────────────────────────    │
│  {https://orcid.org/0000-0000-0000-0000}                                    │
│                                                                              │
│  ───────────────────────────────────────────────────────────────────────    │
│  10. REVIEW TEAM MEMBERS AND AFFILIATIONS *                                 │
│  ───────────────────────────────────────────────────────────────────────    │
│  {Name 1}, {Department}, {Institution}, {City}, {Country}                   │
│  {Name 2}, {Department}, {Institution}, {City}, {Country}                   │
│  ...                                                                        │
│                                                                              │
│  ───────────────────────────────────────────────────────────────────────    │
│  11. ROLES AND RESPONSIBILITIES                                             │
│  ───────────────────────────────────────────────────────────────────────    │
│  {Name 1}: {Conceived the review, developed search strategy, ...}           │
│  {Name 2}: {Will screen titles/abstracts, extract data, ...}                │
│  {Name 3}: {Will resolve conflicts, perform quality assessment, ...}        │
│                                                                              │
│  ───────────────────────────────────────────────────────────────────────    │
│  12. FUNDING SOURCES/SPONSORS *                                             │
│  ───────────────────────────────────────────────────────────────────────    │
│  {Funding source or "None"}                                                 │
│                                                                              │
│  ───────────────────────────────────────────────────────────────────────    │
│  13. CONFLICTS OF INTEREST *                                                │
│  ───────────────────────────────────────────────────────────────────────    │
│  {Conflict statement or "None known"}                                       │
│                                                                              │
│  ───────────────────────────────────────────────────────────────────────    │
│  14. COLLABORATORS                                                          │
│  ───────────────────────────────────────────────────────────────────────    │
│  {Collaborator names and institutions or "None"}                            │
│                                                                              │
│  ───────────────────────────────────────────────────────────────────────    │
│  15. REVIEW QUESTION *                                                      │
│  ───────────────────────────────────────────────────────────────────────    │
│  {Structured review question with PICO elements clearly stated}             │
│                                                                              │
│  Population: {description}                                                  │
│  Intervention: {description}                                                │
│  Comparator: {description}                                                  │
│  Outcome: {description}                                                     │
│                                                                              │
│  ───────────────────────────────────────────────────────────────────────    │
│  16. SEARCHES *                                                             │
│  ───────────────────────────────────────────────────────────────────────    │
│  The following electronic databases will be searched from inception to      │
│  {date}: {database list}.                                                   │
│                                                                              │
│  The search strategy will combine terms for {population}, {intervention},   │
│  using both controlled vocabulary (MeSH, EMTREE) and free-text terms.       │
│  No language restrictions will be applied.                                  │
│                                                                              │
│  Grey literature will be searched via {sources}.                            │
│  Reference lists of included studies will be hand-searched.                 │
│                                                                              │
│  ───────────────────────────────────────────────────────────────────────    │
│  17. URL TO SEARCH STRATEGY                                                 │
│  ───────────────────────────────────────────────────────────────────────    │
│  {URL or "Will be provided as supplementary material"}                      │
│                                                                              │
│  ───────────────────────────────────────────────────────────────────────    │
│  18. CONDITION OR DOMAIN BEING STUDIED *                                    │
│  ───────────────────────────────────────────────────────────────────────    │
│  {Condition/disease/domain description}                                     │
│                                                                              │
│  ───────────────────────────────────────────────────────────────────────    │
│  19. PARTICIPANTS/POPULATION *                                              │
│  ───────────────────────────────────────────────────────────────────────    │
│  Inclusion criteria:                                                        │
│  - {criterion 1}                                                            │
│  - {criterion 2}                                                            │
│                                                                              │
│  Exclusion criteria:                                                        │
│  - {criterion 1}                                                            │
│  - {criterion 2}                                                            │
│                                                                              │
│  ───────────────────────────────────────────────────────────────────────    │
│  20. INTERVENTION(S), EXPOSURE(S) *                                         │
│  ───────────────────────────────────────────────────────────────────────    │
│  {Detailed intervention description}                                        │
│                                                                              │
│  ───────────────────────────────────────────────────────────────────────    │
│  21. COMPARATOR(S)/CONTROL *                                                │
│  ───────────────────────────────────────────────────────────────────────    │
│  {Comparator description: placebo, standard care, active comparator, etc.}  │
│                                                                              │
│  ───────────────────────────────────────────────────────────────────────    │
│  22. TYPES OF STUDY TO BE INCLUDED *                                        │
│  ───────────────────────────────────────────────────────────────────────    │
│  {e.g., Randomised controlled trials (RCTs) only}                           │
│  {e.g., RCTs and quasi-RCTs}                                                │
│  {e.g., Cohort studies, case-control studies}                               │
│                                                                              │
│  ───────────────────────────────────────────────────────────────────────    │
│  23. CONTEXT                                                                │
│  ───────────────────────────────────────────────────────────────────────    │
│  {Setting, geographic focus, time period, etc.}                             │
│                                                                              │
│  ───────────────────────────────────────────────────────────────────────    │
│  24. MAIN OUTCOME(S) *                                                      │
│  ───────────────────────────────────────────────────────────────────────    │
│  Primary outcome(s):                                                        │
│  1. {Primary outcome with definition and time point}                        │
│                                                                              │
│  ───────────────────────────────────────────────────────────────────────    │
│  25. ADDITIONAL OUTCOME(S)                                                  │
│  ───────────────────────────────────────────────────────────────────────    │
│  Secondary outcomes:                                                        │
│  1. {Secondary outcome 1}                                                   │
│  2. {Secondary outcome 2}                                                   │
│                                                                              │
│  ───────────────────────────────────────────────────────────────────────    │
│  26. DATA EXTRACTION (SELECTION AND CODING) *                               │
│  ───────────────────────────────────────────────────────────────────────    │
│  Two reviewers will independently screen titles and abstracts against       │
│  inclusion criteria. Full texts of potentially eligible studies will be     │
│  retrieved and assessed independently by two reviewers. Disagreements       │
│  will be resolved by discussion or a third reviewer.                        │
│                                                                              │
│  Data will be extracted using a standardised form including:                │
│  - Study characteristics (author, year, country, design)                    │
│  - Population characteristics (sample size, age, sex, condition)            │
│  - Intervention and comparator details                                      │
│  - Outcomes and results                                                     │
│  - Risk of bias domains                                                     │
│                                                                              │
│  ───────────────────────────────────────────────────────────────────────    │
│  27. RISK OF BIAS (QUALITY) ASSESSMENT *                                    │
│  ───────────────────────────────────────────────────────────────────────    │
│  Risk of bias will be assessed using the {Cochrane Risk of Bias 2.0 tool    │
│  for randomised trials / Newcastle-Ottawa Scale for observational studies}. │
│                                                                              │
│  Two reviewers will independently assess each study. Disagreements will     │
│  be resolved by consensus or a third reviewer.                              │
│                                                                              │
│  ───────────────────────────────────────────────────────────────────────    │
│  28. STRATEGY FOR DATA SYNTHESIS *                                          │
│  ───────────────────────────────────────────────────────────────────────    │
│  If sufficient homogeneous data are available, meta-analysis will be        │
│  performed using {random-effects / fixed-effects} models.                   │
│                                                                              │
│  For dichotomous outcomes: {risk ratios / odds ratios} with 95% CIs         │
│  For continuous outcomes: {mean differences / standardised mean differences}│
│                                                                              │
│  Heterogeneity will be assessed using I² statistic:                         │
│  - I² < 50%: low heterogeneity                                              │
│  - I² 50-75%: moderate heterogeneity                                        │
│  - I² > 75%: high heterogeneity                                             │
│                                                                              │
│  If meta-analysis is not appropriate, a narrative synthesis will be         │
│  conducted.                                                                 │
│                                                                              │
│  ───────────────────────────────────────────────────────────────────────    │
│  29. ANALYSIS OF SUBGROUPS OR SUBSETS                                       │
│  ───────────────────────────────────────────────────────────────────────    │
│  Subgroup analyses are planned for:                                         │
│  - {Subgroup 1, e.g., Age groups}                                           │
│  - {Subgroup 2, e.g., Disease severity}                                     │
│  - {Subgroup 3, e.g., Intervention dose/duration}                           │
│                                                                              │
│  Sensitivity analyses:                                                      │
│  - Excluding studies at high risk of bias                                   │
│  - {Other sensitivity analyses}                                             │
│                                                                              │
│  ───────────────────────────────────────────────────────────────────────    │
│  30. TYPE AND METHOD OF REVIEW *                                            │
│  ───────────────────────────────────────────────────────────────────────    │
│  {Intervention / Diagnostic / Prognostic / Qualitative / Other}             │
│                                                                              │
│  ───────────────────────────────────────────────────────────────────────    │
│  31. LANGUAGE                                                               │
│  ───────────────────────────────────────────────────────────────────────    │
│  English                                                                    │
│                                                                              │
│  ───────────────────────────────────────────────────────────────────────    │
│  32. COUNTRY *                                                              │
│  ───────────────────────────────────────────────────────────────────────    │
│  {Country of corresponding author}                                          │
│                                                                              │
│  ───────────────────────────────────────────────────────────────────────    │
│  33. OTHER REGISTRATION DETAILS                                             │
│  ───────────────────────────────────────────────────────────────────────    │
│  {Any other registration, e.g., OSF, Cochrane}                              │
│                                                                              │
│  ───────────────────────────────────────────────────────────────────────    │
│  34. REFERENCE AND/OR URL FOR PUBLISHED PROTOCOL                            │
│  ───────────────────────────────────────────────────────────────────────    │
│  {URL or "Not yet published"}                                               │
│                                                                              │
│  ───────────────────────────────────────────────────────────────────────    │
│  35. DISSEMINATION PLANS                                                    │
│  ───────────────────────────────────────────────────────────────────────    │
│  Results will be submitted for publication in a peer-reviewed journal       │
│  and presented at relevant conferences.                                     │
│                                                                              │
│  ───────────────────────────────────────────────────────────────────────    │
│  36. KEYWORDS *                                                             │
│  ───────────────────────────────────────────────────────────────────────    │
│  {keyword1}; {keyword2}; {keyword3}; {keyword4}; {keyword5}                 │
│                                                                              │
│  ───────────────────────────────────────────────────────────────────────    │
│  37. DETAILS OF ANY EXISTING REVIEW OF THE SAME TOPIC                       │
│  ───────────────────────────────────────────────────────────────────────    │
│  {Description of existing reviews and how this review differs, or "None"}   │
│                                                                              │
│  ───────────────────────────────────────────────────────────────────────    │
│  38. CURRENT REVIEW STATUS *                                                │
│  ───────────────────────────────────────────────────────────────────────    │
│  {Ongoing / Completed but not published / Published}                        │
│                                                                              │
│  ───────────────────────────────────────────────────────────────────────    │
│  39. ANY ADDITIONAL INFORMATION                                             │
│  ───────────────────────────────────────────────────────────────────────    │
│  {Additional notes or "None"}                                               │
│                                                                              │
│  ───────────────────────────────────────────────────────────────────────    │
│  40. DETAILS OF FINAL PUBLICATION                                           │
│  ───────────────────────────────────────────────────────────────────────    │
│  {To be completed after publication}                                        │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘

* = Required field in PROSPERO
```

---

## 2. System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            SEARCH STRATEGY MODULE                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  LAYER 1: PRESENTATION                                                       │
│  ════════════════════                                                        │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐           │
│  │  Web UI (React)  │  │  CLI (Python)    │  │  REST API        │           │
│  │                  │  │                  │  │  (FastAPI)       │           │
│  └────────┬─────────┘  └────────┬─────────┘  └────────┬─────────┘           │
│           └─────────────────────┴─────────────────────┘                      │
│                                  │                                           │
│  LAYER 2: APPLICATION SERVICES                                               │
│  ═════════════════════════════                                               │
│  ┌──────────────────────────────▼──────────────────────────────────┐        │
│  │                    SearchStrategyService                         │        │
│  │  ┌────────────────┐ ┌────────────────┐ ┌────────────────────┐   │        │
│  │  │ PICOParser     │ │ QueryGenerator │ │ DocumentRenderer   │   │        │
│  │  │ PROSPEROGen    │ │                │ │                    │   │        │
│  │  └────────────────┘ └────────────────┘ └────────────────────┘   │        │
│  └──────────────────────────────┬──────────────────────────────────┘        │
│                                 │                                            │
│  LAYER 3: DOMAIN SERVICES                                                    │
│  ════════════════════════                                                    │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────────┐        │
│  │ Ontology    │ │ Database    │ │ Dedup       │ │ LLM Gateway     │        │
│  │ Service     │ │ Executors   │ │ Engine      │ │ (LangChain)     │        │
│  │ (MeSH/     │ │ (PubMed,    │ │             │ │                 │        │
│  │  EMTREE)    │ │  Embase...) │ │             │ │                 │        │
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────────┘        │
│                                 │                                            │
│  LAYER 4: DATA                                                               │
│  ═════════════                                                               │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────────┐        │
│  │ PostgreSQL  │ │ Redis       │ │ File Store  │ │ Vector DB       │        │
│  │ (Projects,  │ │ (Cache,     │ │ (PDFs, RIS) │ │ (Embeddings)    │        │
│  │  Queries)   │ │  Sessions)  │ │             │ │                 │        │
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────────┘        │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Services Specification

### 3.1 PICOParserService

**Purpose:** Extract structured PICO elements from free-text research question

```python
# services/pico_parser.py

from pydantic import BaseModel
from typing import List, Optional

class PICOElements(BaseModel):
    population: str
    population_terms: List[str]
    intervention: str
    intervention_terms: List[str]
    comparator: Optional[str]
    comparator_terms: List[str]
    outcome: str
    outcome_terms: List[str]
    study_types: List[str]  # e.g., ["RCT", "cohort", "case-control"]

class PICOParserService:
    """Extract PICO elements using LLM."""
    
    def __init__(self, llm_client):
        self.llm = llm_client
        
    async def parse(self, research_question: str) -> PICOElements:
        """
        Extract PICO from free-text question.
        
        Example:
          Input: "What is the effectiveness of AI in pediatric surgery?"
          Output: PICOElements(
            population="pediatric surgical patients",
            population_terms=["pediatric", "child*", "infant*", "neonat*"],
            intervention="artificial intelligence",
            intervention_terms=["artificial intelligence", "machine learning", 
                               "deep learning", "neural network*"],
            ...
          )
        """
        pass
```

### 3.2 OntologyService

**Purpose:** Map free-text terms to controlled vocabulary (MeSH, EMTREE)

```python
# services/ontology.py

from dataclasses import dataclass
from typing import List, Dict
from enum import Enum

class OntologyType(Enum):
    MESH = "mesh"
    EMTREE = "emtree"
    
@dataclass
class ControlledTerm:
    term_id: str           # e.g., "D000086382"
    preferred_term: str    # e.g., "Artificial Intelligence"
    entry_terms: List[str] # Synonyms
    tree_numbers: List[str]
    explode: bool = True   # Include narrower terms

class OntologyService:
    """Interface with MeSH and EMTREE APIs."""
    
    def __init__(self):
        self.mesh_api = "https://id.nlm.nih.gov/mesh/lookup/term"
        self.umls_api = "https://uts-ws.nlm.nih.gov/rest"
        
    async def get_mesh_terms(
        self, 
        concept: str,
        include_narrower: bool = True
    ) -> List[ControlledTerm]:
        """
        Look up MeSH terms for a concept.
        
        Example:
          Input: "artificial intelligence"
          Output: [
            ControlledTerm(
              term_id="D000086382",
              preferred_term="Artificial Intelligence",
              entry_terms=["AI", "Machine Intelligence", "Computational Intelligence"],
              tree_numbers=["L01.224.050.375"],
              explode=True
            ),
            ControlledTerm(
              term_id="D000069550",
              preferred_term="Machine Learning",
              ...
            )
          ]
        """
        pass
    
    async def get_synonyms(self, term: str) -> List[str]:
        """Get text word variations for free-text searching."""
        pass
    
    async def translate_mesh_to_emtree(
        self, 
        mesh_terms: List[ControlledTerm]
    ) -> List[ControlledTerm]:
        """Map MeSH terms to EMTREE equivalents."""
        pass
```

### 3.3 QueryGeneratorService

**Purpose:** Generate database-specific Boolean queries from PICO + ontology terms

```python
# services/query_generator.py

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum

class DatabaseType(Enum):
    PUBMED = "pubmed"
    EMBASE = "embase"
    CINAHL = "cinahl"
    COCHRANE = "cochrane"
    WEB_OF_SCIENCE = "wos"
    SCOPUS = "scopus"
    GLOBAL_HEALTH = "global_health"
    PROQUEST = "proquest"
    AFRICA_WIDE = "africa_wide"

@dataclass
class QueryLine:
    line_number: str       # "S1", "S2", etc.
    query: str             # The actual Boolean string
    description: str       # What this line searches for
    result_count: Optional[int] = None

@dataclass
class DatabaseQuery:
    database: DatabaseType
    platform: str          # "Ovid", "EBSCO", "Web of Science"
    search_date: str
    lines: List[QueryLine]
    final_line: str        # e.g., "S45"
    total_results: int

class QueryGeneratorService:
    """Generate Boolean queries for each database."""
    
    # Database-specific field codes
    FIELD_CODES = {
        DatabaseType.PUBMED: {
            "title": "[ti]",
            "abstract": "[ab]",
            "title_abstract": "[tiab]",
            "mesh": "[MeSH Terms]",
            "mesh_noexp": "[MeSH Terms:noexp]",
            "keyword": "[kw]",
            "publication_type": "[pt]",
        },
        DatabaseType.EMBASE: {
            "title": ".ti.",
            "abstract": ".ab.",
            "title_abstract": ".ti,ab.",
            "emtree": "/exp",
            "emtree_noexp": "/de",
            "keyword": ".kw.",
        },
        DatabaseType.CINAHL: {
            "title": "TI",
            "abstract": "AB",
            "title_abstract": "TI OR AB",
            "mesh": "MH",  # CINAHL uses MH for subject headings
            "keyword": "MW",
        },
        # ... other databases
    }
    
    # Proximity operators by database
    PROXIMITY_OPS = {
        DatabaseType.PUBMED: None,  # PubMed doesn't support proximity
        DatabaseType.EMBASE: "ADJ",  # term1 ADJ3 term2
        DatabaseType.CINAHL: "N",    # term1 N3 term2
        DatabaseType.WEB_OF_SCIENCE: "NEAR/", # term1 NEAR/3 term2
    }
    
    async def generate_query(
        self,
        pico: PICOElements,
        database: DatabaseType,
        mesh_terms: List[ControlledTerm],
        emtree_terms: List[ControlledTerm],
    ) -> DatabaseQuery:
        """
        Generate complete search strategy for one database.
        
        Structure:
        - Lines S1-S10: Population terms (MeSH + free text)
        - Lines S11-S20: Intervention terms (MeSH + free text)  
        - Lines S21-S30: Outcome terms (if applicable)
        - Lines S31-S40: Study type filters (if applicable)
        - Line S41+: Combination lines (S10 AND S20 AND S30...)
        """
        pass
    
    def _format_mesh_line(
        self, 
        term: ControlledTerm, 
        database: DatabaseType
    ) -> str:
        """Format a MeSH/EMTREE term for specific database syntax."""
        pass
    
    def _format_text_word_line(
        self,
        terms: List[str],
        database: DatabaseType,
        use_proximity: bool = False
    ) -> str:
        """Format free-text terms with truncation and field codes."""
        pass
```

### 3.4 DatabaseExecutorService

**Purpose:** Execute queries against live databases and retrieve results

```python
# services/database_executor.py

from dataclasses import dataclass
from typing import List, AsyncIterator
import httpx

@dataclass
class Citation:
    id: str
    title: str
    abstract: Optional[str]
    authors: List[str]
    journal: Optional[str]
    year: Optional[int]
    doi: Optional[str]
    pmid: Optional[str]
    source_database: str
    raw_record: Dict

@dataclass
class SearchResult:
    database: DatabaseType
    query_executed: str
    execution_date: str
    total_count: int
    citations: List[Citation]

class PubMedExecutor:
    """Execute searches via NCBI E-utilities API."""
    
    BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key  # Higher rate limit with key
        self.rate_limit = 10 if api_key else 3  # requests per second
        
    async def search(
        self, 
        query: str,
        max_results: int = 10000
    ) -> SearchResult:
        """
        Execute PubMed search and retrieve citations.
        
        1. esearch: Get PMIDs matching query
        2. efetch: Retrieve full records for PMIDs
        """
        pass
    
    async def get_query_translation(self, query: str) -> Dict:
        """Get PubMed's interpretation of the query (useful for debugging)."""
        pass

class EmbaseExecutor:
    """Execute searches via Embase API (requires institutional access)."""
    pass

class DatabaseExecutorService:
    """Facade for all database executors."""
    
    def __init__(self, config: DatabaseConfig):
        self.executors = {
            DatabaseType.PUBMED: PubMedExecutor(config.pubmed_api_key),
            DatabaseType.EMBASE: EmbaseExecutor(config.embase_credentials),
            # ...
        }
    
    async def execute_all(
        self,
        queries: Dict[DatabaseType, DatabaseQuery]
    ) -> Dict[DatabaseType, SearchResult]:
        """Execute searches across all databases concurrently."""
        pass
```

### 3.5 DeduplicationService

**Purpose:** Remove duplicates and track per-database counts

```python
# services/deduplication.py

@dataclass
class DeduplicationStats:
    database: str
    before_count: int
    after_count: int
    duplicates_removed: int

@dataclass
class DeduplicationResult:
    unique_citations: List[Citation]
    stats_by_database: List[DeduplicationStats]
    total_before: int
    total_after: int
    method_description: str

class DeduplicationService:
    """Multi-strategy deduplication with tracking."""
    
    async def deduplicate(
        self,
        citations_by_database: Dict[str, List[Citation]]
    ) -> DeduplicationResult:
        """
        Deduplicate citations while tracking per-database stats.
        
        Strategy order:
        1. Exact DOI match
        2. Exact PMID match
        3. Title + Year exact match (normalized)
        4. Fuzzy title match (Levenshtein > 0.92)
        5. Embedding similarity (optional, for edge cases)
        
        Returns stats formatted for the document table.
        """
        pass
```

### 3.6 DocumentRendererService

**Purpose:** Generate the final PDF/DOCX document

```python
# services/document_renderer.py

from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML  # For PDF generation
from docx import Document    # For DOCX generation

@dataclass
class SearchStrategyDocument:
    title: str
    reviewers: List[str]
    institution: str
    search_date: str
    databases_searched: List[str]
    methodology_narrative: str
    prisma_before: int
    prisma_after: int
    dedup_stats: List[DeduplicationStats]
    database_queries: List[DatabaseQuery]
    author_name: str
    author_credentials: str
    author_email: str
    last_updated: str

class DocumentRendererService:
    """Render search strategy document to PDF/DOCX."""
    
    def __init__(self, template_dir: Path):
        self.env = Environment(loader=FileSystemLoader(template_dir))
        
    def render_pdf(
        self,
        document: SearchStrategyDocument,
        output_path: Path
    ) -> Path:
        """Render to PDF matching the Montreal Children's Hospital format."""
        template = self.env.get_template("search_strategy.html")
        html_content = template.render(doc=document)
        HTML(string=html_content).write_pdf(output_path)
        return output_path
    
    def render_docx(
        self,
        document: SearchStrategyDocument,
        output_path: Path
    ) -> Path:
        """Render to DOCX for editing."""
        pass
```

### 3.7 PROSPEROGeneratorService

**Purpose:** Generate copy-paste ready PROSPERO registration protocol

```python
# services/prospero_generator.py

from dataclasses import dataclass, field
from typing import List, Optional
from datetime import date

@dataclass
class ReviewTeamMember:
    name: str
    department: str
    institution: str
    city: str
    country: str
    email: Optional[str] = None
    orcid: Optional[str] = None
    role: Optional[str] = None  # e.g., "Screening", "Data extraction"

@dataclass
class PROSPEROProtocol:
    """Complete PROSPERO registration data structure."""
    
    # Section 1-4: Basic info
    review_title: str
    original_language_title: Optional[str] = None
    start_date: date = None
    completion_date: date = None
    
    # Section 5: Stage
    stage_of_review: str = "Review ongoing"  # Or "Preliminary searches", "Piloting", etc.
    
    # Section 6-9: Contact
    named_contact: str = ""
    named_contact_email: str = ""
    named_contact_address: str = ""
    named_contact_orcid: Optional[str] = None
    
    # Section 10-14: Team
    team_members: List[ReviewTeamMember] = field(default_factory=list)
    roles_and_responsibilities: str = ""
    funding_sources: str = "None"
    conflicts_of_interest: str = "None known"
    collaborators: str = "None"
    
    # Section 15-17: Question and search
    review_question: str = ""
    pico_population: str = ""
    pico_intervention: str = ""
    pico_comparator: str = ""
    pico_outcome: str = ""
    searches_description: str = ""
    search_strategy_url: str = "Will be provided as supplementary material"
    
    # Section 18-23: Eligibility
    condition_domain: str = ""
    population_inclusion: List[str] = field(default_factory=list)
    population_exclusion: List[str] = field(default_factory=list)
    intervention_description: str = ""
    comparator_description: str = ""
    study_types: List[str] = field(default_factory=list)
    context: str = ""
    
    # Section 24-25: Outcomes
    primary_outcomes: List[str] = field(default_factory=list)
    secondary_outcomes: List[str] = field(default_factory=list)
    
    # Section 26-29: Methods
    data_extraction_method: str = ""
    risk_of_bias_tool: str = "Cochrane Risk of Bias 2.0"
    synthesis_strategy: str = ""
    subgroup_analyses: List[str] = field(default_factory=list)
    sensitivity_analyses: List[str] = field(default_factory=list)
    
    # Section 30-32: Type and location
    review_type: str = "Intervention"  # Intervention, Diagnostic, Prognostic, etc.
    language: str = "English"
    country: str = ""
    
    # Section 33-40: Other
    other_registration: str = "None"
    published_protocol_url: str = "Not yet published"
    dissemination_plans: str = "Results will be submitted for publication in a peer-reviewed journal."
    keywords: List[str] = field(default_factory=list)
    existing_reviews: str = "None identified"
    current_status: str = "Ongoing"
    additional_information: str = "None"

class PROSPEROGeneratorService:
    """Generate PROSPERO registration protocol from review data."""
    
    def __init__(self, llm_client):
        self.llm = llm_client
    
    async def generate_protocol(
        self,
        pico: PICOElements,
        team_members: List[ReviewTeamMember],
        databases: List[str],
        search_date: str,
        review_title: Optional[str] = None,
        additional_context: Optional[str] = None
    ) -> PROSPEROProtocol:
        """
        Generate complete PROSPERO protocol from PICO and team info.
        
        Uses LLM to generate:
        - Review title (if not provided)
        - Formatted review question
        - Inclusion/exclusion criteria
        - Data extraction description
        - Synthesis strategy
        - Keywords
        """
        pass
    
    async def _generate_title(self, pico: PICOElements) -> str:
        """Generate PROSPERO-appropriate title."""
        # Format: "{Intervention} for {population/condition}: a systematic review"
        pass
    
    async def _generate_eligibility_criteria(
        self, 
        pico: PICOElements
    ) -> tuple[List[str], List[str]]:
        """Generate inclusion and exclusion criteria."""
        pass
    
    async def _generate_synthesis_strategy(
        self,
        pico: PICOElements,
        study_types: List[str]
    ) -> str:
        """Generate data synthesis description."""
        pass
    
    def render_protocol(
        self,
        protocol: PROSPEROProtocol,
        output_path: Path,
        format: str = "markdown"  # "markdown", "txt", "docx"
    ) -> Path:
        """
        Render protocol to copy-paste format.
        
        Each field is clearly labeled with the PROSPERO field number
        and name, making it easy to copy directly into the web form.
        """
        pass
    
    def _format_team_members(self, members: List[ReviewTeamMember]) -> str:
        """Format team members for PROSPERO field 10."""
        lines = []
        for m in members:
            line = f"{m.name}, {m.department}, {m.institution}, {m.city}, {m.country}"
            lines.append(line)
        return "\n".join(lines)
    
    def _format_roles(self, members: List[ReviewTeamMember]) -> str:
        """Format roles for PROSPERO field 11."""
        lines = []
        for m in members:
            if m.role:
                lines.append(f"{m.name}: {m.role}")
        return "\n".join(lines)
```

**PROSPERO Generation Prompt:**

```python
# prompts/prospero_generation.py

PROSPERO_TITLE_PROMPT = """
Generate a systematic review title suitable for PROSPERO registration.

PICO Elements:
- Population: {population}
- Intervention: {intervention}
- Comparator: {comparator}
- Outcome: {outcome}

The title should follow this format:
"[Intervention] for [condition/population]: a systematic review [and meta-analysis]"

Examples:
- "Cognitive behavioral therapy for anxiety disorders in children: a systematic review and meta-analysis"
- "Artificial intelligence in pediatric surgery: a systematic review"

Return only the title, no explanation.
"""

PROSPERO_ELIGIBILITY_PROMPT = """
Generate inclusion and exclusion criteria for a systematic review PROSPERO registration.

PICO Elements:
- Population: {population}
- Intervention: {intervention}
- Comparator: {comparator}
- Outcome: {outcome}
- Study types: {study_types}

Generate clear, specific criteria in this JSON format:
{{
    "inclusion": [
        "criterion 1",
        "criterion 2",
        ...
    ],
    "exclusion": [
        "criterion 1",
        "criterion 2",
        ...
    ]
}}

Inclusion criteria should cover:
- Population characteristics
- Intervention specifics
- Study design requirements
- Publication requirements (if any)

Exclusion criteria should cover:
- Populations not of interest
- Study types to exclude
- Other exclusion reasons
"""

PROSPERO_SYNTHESIS_PROMPT = """
Generate a data synthesis strategy description for PROSPERO registration.

Details:
- Study types: {study_types}
- Primary outcome type: {outcome_type} (binary/continuous/time-to-event)
- Expected heterogeneity: {heterogeneity_expectation}

Write a paragraph describing:
1. Whether meta-analysis will be conducted
2. Statistical model (random/fixed effects)
3. Effect measures to use
4. Heterogeneity assessment approach
5. What happens if meta-analysis is not possible

Use formal academic language suitable for PROSPERO.
"""
```

---

## 4. LLM Integration

### 4.1 LLM Configuration

```python
# config/llm_config.py

from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic

LLM_CONFIG = {
    "pico_extraction": {
        "model": "gpt-4o",
        "temperature": 0.0,
        "max_tokens": 2000,
        "description": "Extract structured PICO from research question"
    },
    "synonym_generation": {
        "model": "gpt-4o-mini",
        "temperature": 0.3,
        "max_tokens": 1000,
        "description": "Generate search term synonyms and variations"
    },
    "methodology_narrative": {
        "model": "gpt-4o",
        "temperature": 0.2,
        "max_tokens": 500,
        "description": "Generate methodology paragraph for document"
    }
}

def get_llm(task: str):
    config = LLM_CONFIG[task]
    return ChatOpenAI(
        model=config["model"],
        temperature=config["temperature"],
        max_tokens=config["max_tokens"]
    )
```

### 4.2 Prompts

```python
# prompts/pico_extraction.py

PICO_EXTRACTION_PROMPT = """
You are an expert medical librarian extracting PICO elements from a research question.

Research Question: {question}

Extract the following elements. For each element, provide:
1. A clear description
2. A list of search terms including:
   - The main concept
   - Synonyms
   - Related terms
   - Variant spellings
   - Truncation suggestions (use * for truncation)

Return JSON in this exact format:
{{
  "population": {{
    "description": "...",
    "terms": ["term1", "term2*", "term3"]
  }},
  "intervention": {{
    "description": "...",
    "terms": ["...", "..."]
  }},
  "comparator": {{
    "description": "..." or null if not applicable,
    "terms": ["...", "..."]
  }},
  "outcome": {{
    "description": "...",
    "terms": ["...", "..."]
  }},
  "study_types": ["RCT", "cohort", "systematic review", ...]
}}

Be comprehensive. Include:
- American and British spellings (e.g., tumor/tumour)
- Acronyms and full forms (e.g., AI, artificial intelligence)
- Lay terms and medical terms (e.g., heart attack, myocardial infarction)
- Truncation for word variants (e.g., surg* for surgery, surgical, surgeon)
"""

METHODOLOGY_NARRATIVE_PROMPT = """
Generate a methodology paragraph for a systematic review search strategy document.

Details:
- Databases searched: {databases}
- Search date: {search_date}
- Topic: {topic}
- Used subject headings (MeSH/EMTREE) and text words
- No language restrictions (unless specified)

Write in past tense, third person, formal academic style.
Example style: "A senior medical librarian searched the following databases from inception until {date}: {database_list}. The search strategy used variations in text words found in the title, abstract or keyword fields, and relevant subject headings to retrieve articles looking at {topic}."

Keep it to 2-3 sentences. Be specific to this review.
"""
```

---

## 5. API Specification

### 5.1 REST Endpoints

```yaml
openapi: 3.0.3
info:
  title: Search Strategy Module API
  version: 1.0.0

paths:
  /api/v1/search-strategy/parse-pico:
    post:
      summary: Extract PICO from research question
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                research_question:
                  type: string
                  example: "What is the effectiveness of AI in pediatric surgery?"
      responses:
        '200':
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/PICOElements'

  /api/v1/search-strategy/generate-queries:
    post:
      summary: Generate database-specific queries from PICO
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                pico:
                  $ref: '#/components/schemas/PICOElements'
                databases:
                  type: array
                  items:
                    type: string
                    enum: [pubmed, embase, cinahl, cochrane, wos, scopus]
      responses:
        '200':
          content:
            application/json:
              schema:
                type: object
                additionalProperties:
                  $ref: '#/components/schemas/DatabaseQuery'

  /api/v1/search-strategy/execute:
    post:
      summary: Execute searches across databases
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                queries:
                  type: object
                max_results_per_db:
                  type: integer
                  default: 10000
      responses:
        '202':
          description: Search execution started
          content:
            application/json:
              schema:
                type: object
                properties:
                  job_id:
                    type: string

  /api/v1/search-strategy/generate-document:
    post:
      summary: Generate final search strategy document
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                project_id:
                  type: string
                format:
                  type: string
                  enum: [pdf, docx]
                template:
                  type: string
                  default: "standard"
      responses:
        '200':
          content:
            application/pdf:
              schema:
                type: string
                format: binary

  /api/v1/search-strategy/generate-prospero:
    post:
      summary: Generate PROSPERO registration protocol
      requestBody:
        content:
          application/json:
            schema:
              type: object
              required: [project_id, team_members]
              properties:
                project_id:
                  type: string
                team_members:
                  type: array
                  items:
                    type: object
                    properties:
                      name:
                        type: string
                      department:
                        type: string
                      institution:
                        type: string
                      city:
                        type: string
                      country:
                        type: string
                      email:
                        type: string
                      orcid:
                        type: string
                      role:
                        type: string
                start_date:
                  type: string
                  format: date
                completion_date:
                  type: string
                  format: date
                funding:
                  type: string
                  default: "None"
                conflicts:
                  type: string
                  default: "None known"
                format:
                  type: string
                  enum: [markdown, txt, docx]
                  default: markdown
      responses:
        '200':
          description: PROSPERO protocol document
          content:
            text/markdown:
              schema:
                type: string
            application/vnd.openxmlformats-officedocument.wordprocessingml.document:
              schema:
                type: string
                format: binary
```

---

## 6. Data Models

### 6.1 Database Schema

```sql
-- PostgreSQL schema

CREATE TABLE search_projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(500) NOT NULL,
    research_question TEXT NOT NULL,
    pico_elements JSONB,
    reviewers JSONB,  -- Array of {name, email, role}
    institution VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE search_queries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES search_projects(id),
    database VARCHAR(50) NOT NULL,
    platform VARCHAR(50),
    search_date DATE NOT NULL,
    query_lines JSONB NOT NULL,  -- Array of {line_number, query, result_count}
    total_results INTEGER,
    executed_at TIMESTAMP
);

CREATE TABLE search_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES search_projects(id),
    database VARCHAR(50) NOT NULL,
    citation_data JSONB NOT NULL,
    is_duplicate BOOLEAN DEFAULT FALSE,
    duplicate_of UUID REFERENCES search_results(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE deduplication_runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES search_projects(id),
    method_description TEXT,
    stats_by_database JSONB,  -- Array of {database, before, after}
    total_before INTEGER,
    total_after INTEGER,
    executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE prospero_protocols (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES search_projects(id),
    protocol_data JSONB NOT NULL,  -- Full PROSPEROProtocol structure
    prospero_id VARCHAR(50),       -- Assigned after registration (e.g., CRD42024000001)
    status VARCHAR(50) DEFAULT 'draft',  -- draft, submitted, registered
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE team_members (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES search_projects(id),
    name VARCHAR(200) NOT NULL,
    department VARCHAR(200),
    institution VARCHAR(300),
    city VARCHAR(100),
    country VARCHAR(100),
    email VARCHAR(200),
    orcid VARCHAR(50),
    role TEXT,  -- Description of responsibilities
    is_contact BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_search_results_project ON search_results(project_id);
CREATE INDEX idx_search_results_duplicate ON search_results(is_duplicate);
CREATE INDEX idx_prospero_protocols_project ON prospero_protocols(project_id);
CREATE INDEX idx_team_members_project ON team_members(project_id);
```

---

## 7. Functional Requirements

| ID | Requirement | Priority | Acceptance Criteria |
|----|-------------|----------|---------------------|
| FR-01 | Extract PICO from free-text research question | Critical | Returns structured PICO with ≥10 terms per element |
| FR-02 | Map concepts to MeSH terms | Critical | Returns relevant MeSH descriptors with tree numbers |
| FR-03 | Map concepts to EMTREE terms | High | Returns EMTREE equivalents for Embase searching |
| FR-04 | Generate PubMed query syntax | Critical | Valid query executable via E-utilities |
| FR-05 | Generate Embase/Ovid query syntax | Critical | Valid query with .ti,ab. and /exp syntax |
| FR-06 | Generate CINAHL/EBSCO query syntax | High | Valid query with TI, AB, MH syntax |
| FR-07 | Generate Cochrane query syntax | High | Valid query for Cochrane Library |
| FR-08 | Execute PubMed search via API | Critical | Returns citations with PMID, title, abstract |
| FR-09 | Export search results to RIS | Critical | Valid RIS file importable to EndNote/Zotero |
| FR-10 | Deduplicate citations | Critical | Removes duplicates with ≥99% accuracy |
| FR-11 | Track per-database counts | Critical | Accurate before/after counts per database |
| FR-12 | Generate summary PDF | Critical | Matches Montreal Children's Hospital format |
| FR-13 | Generate supplementary PDF | Critical | Line-by-line queries with result counts |
| FR-14 | Generate DOCX for editing | High | Editable document with same content |
| **FR-15** | **Generate PROSPERO protocol** | **Critical** | **All 40 PROSPERO fields populated** |
| FR-16 | Generate PROSPERO-formatted title | Critical | Follows "[Intervention] for [condition]" format |
| FR-17 | Generate inclusion/exclusion criteria | Critical | Specific, measurable criteria from PICO |
| FR-18 | Generate synthesis strategy text | High | Appropriate for study types selected |
| FR-19 | Format team members for PROSPERO | Critical | Name, dept, institution, city, country format |
| FR-20 | Output PROSPERO as Markdown | Critical | Copy-paste ready with field labels |
| FR-21 | Output PROSPERO as DOCX | High | Editable with same structure |
| FR-22 | Validate required PROSPERO fields | High | Warns if required fields (*) are empty |

---

## 8. Non-Functional Requirements

| ID | Requirement | Target | Measurement |
|----|-------------|--------|-------------|
| NFR-01 | PICO extraction latency | < 5 seconds | API response time |
| NFR-02 | Query generation latency | < 10 seconds for all databases | API response time |
| NFR-03 | Search execution throughput | 10,000 citations/database | Within rate limits |
| NFR-04 | Deduplication performance | 50,000 citations in < 2 minutes | Processing time |
| NFR-05 | Document generation time | < 30 seconds | PDF render time |
| NFR-06 | System availability | 99.5% uptime | Monthly SLA |
| NFR-07 | API rate limiting | 100 requests/minute/user | Prevent abuse |
| NFR-08 | Audit logging | All operations logged | Compliance |
| NFR-09 | Data retention | 2 years | Project data |

---

## 9. Technology Stack

### 9.1 Complete Stack

```yaml
infrastructure:
  container: Docker 24+
  orchestration: Docker Compose (dev) / Kubernetes (prod)
  
backend:
  language: Python 3.12+
  framework: FastAPI 0.109+
  async: asyncio + httpx
  validation: Pydantic 2.0+
  orm: SQLAlchemy 2.0+
  migrations: Alembic
  
llm_integration:
  framework: LangChain 0.1+
  providers:
    - OpenAI (GPT-4o, GPT-4o-mini)
    - Anthropic (Claude 3.5 Sonnet) - optional
  embeddings: text-embedding-3-small (for dedup)
  
databases:
  primary: PostgreSQL 16+
  cache: Redis 7+
  vector: ChromaDB (embedded) or Qdrant
  
document_generation:
  templating: Jinja2
  pdf: WeasyPrint or ReportLab
  docx: python-docx
  
external_apis:
  pubmed: NCBI E-utilities
  mesh: NLM MeSH API
  umls: UMLS REST API (requires license)
  unpaywall: Unpaywall API (for PDF retrieval later)
  
testing:
  unit: pytest
  api: pytest + httpx
  e2e: Playwright (for web UI)
  
observability:
  logging: structlog
  metrics: Prometheus
  tracing: OpenTelemetry (optional)
```

---

## 10. Build Instructions

### 10.1 Prerequisites

```bash
# System requirements
- Ubuntu 22.04+ or macOS 13+
- Python 3.12+
- Docker 24+
- Docker Compose 2.0+
- Node.js 20+ (for web UI)

# API Keys needed
- OPENAI_API_KEY (required)
- NCBI_API_KEY (optional, higher rate limits)
- UMLS_API_KEY (optional, for advanced ontology features)
```

### 10.2 Step-by-Step Setup

```bash
# 1. Clone and setup
git clone <repository>
cd search-strategy-module

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -e ".[dev]"

# 4. Copy environment template
cp .env.example .env
# Edit .env with your API keys

# 5. Start infrastructure
docker-compose up -d postgres redis

# 6. Run database migrations
alembic upgrade head

# 7. Start API server (development)
uvicorn app.main:app --reload --port 8000

# 8. Run tests
pytest tests/ -v

# 9. Test the search strategy pipeline
python -m app.cli generate-search \
  --question "What is the effectiveness of AI in pediatric surgery?" \
  --databases pubmed,embase,cinahl \
  --output ./output/search_strategy.pdf

# 10. Test PROSPERO protocol generation
python -m app.cli generate-prospero \
  --question "What is the effectiveness of AI in pediatric surgery?" \
  --contact "Dr. Jane Smith" \
  --email "jane.smith@university.edu" \
  --institution "University Hospital" \
  --output ./output/prospero_protocol.md
```

### 10.3 Docker Compose Setup

```yaml
# docker-compose.yml
version: '3.8'

services:
  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: search_strategy
      POSTGRES_USER: app
      POSTGRES_PASSWORD: devpassword
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://app:devpassword@postgres:5432/search_strategy
      REDIS_URL: redis://redis:6379
      OPENAI_API_KEY: ${OPENAI_API_KEY}
    depends_on:
      - postgres
      - redis
    volumes:
      - ./app:/app/app  # Hot reload

volumes:
  pgdata:
```

### 10.4 Project Structure

```
search-strategy-module/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app
│   ├── config.py               # Settings
│   ├── cli.py                  # CLI interface
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes.py           # API endpoints
│   │   └── dependencies.py
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── pico_parser.py
│   │   ├── ontology.py
│   │   ├── query_generator.py
│   │   ├── database_executor.py
│   │   ├── deduplication.py
│   │   ├── document_renderer.py
│   │   └── prospero_generator.py
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── database.py         # SQLAlchemy models
│   │   └── schemas.py          # Pydantic schemas
│   │
│   ├── prompts/
│   │   ├── pico_extraction.txt
│   │   ├── methodology.txt
│   │   ├── prospero_title.txt
│   │   ├── prospero_eligibility.txt
│   │   └── prospero_synthesis.txt
│   │
│   └── templates/
│       ├── search_strategy.html
│       ├── search_strategy.css
│       ├── prospero_protocol.md
│       └── prospero_protocol.docx
│
├── tests/
│   ├── __init__.py
│   ├── test_pico_parser.py
│   ├── test_query_generator.py
│   ├── test_deduplication.py
│   └── fixtures/
│       └── sample_citations.json
│
├── alembic/
│   ├── versions/
│   └── env.py
│
├── docker-compose.yml
├── Dockerfile
├── pyproject.toml
├── .env.example
└── README.md
```

---

## 11. Testing Plan

### 11.1 Unit Tests

```python
# tests/test_query_generator.py

import pytest
from app.services.query_generator import QueryGeneratorService, DatabaseType

class TestPubMedQueryGeneration:
    
    def test_mesh_term_formatting(self):
        """MeSH terms should use correct PubMed syntax."""
        service = QueryGeneratorService()
        result = service._format_mesh_line(
            term=ControlledTerm(
                term_id="D000086382",
                preferred_term="Artificial Intelligence",
                explode=True
            ),
            database=DatabaseType.PUBMED
        )
        assert result == '"Artificial Intelligence"[MeSH Terms]'
    
    def test_text_word_with_truncation(self):
        """Text words should include truncation and field codes."""
        service = QueryGeneratorService()
        result = service._format_text_word_line(
            terms=["surg*", "operat*"],
            database=DatabaseType.PUBMED
        )
        assert "[tiab]" in result
        assert "surg*" in result
        assert " OR " in result

class TestEmbaseQueryGeneration:
    
    def test_emtree_term_formatting(self):
        """EMTREE terms should use Ovid syntax."""
        service = QueryGeneratorService()
        result = service._format_mesh_line(
            term=ControlledTerm(
                preferred_term="artificial intelligence",
                explode=True
            ),
            database=DatabaseType.EMBASE
        )
        assert "artificial intelligence/exp" in result.lower()
```

### 11.2 Integration Tests

```python
# tests/test_integration.py

@pytest.mark.integration
async def test_full_pipeline():
    """Test complete flow from question to document."""
    
    # 1. Parse PICO
    pico_service = PICOParserService(get_llm("pico_extraction"))
    pico = await pico_service.parse(
        "What is the effectiveness of AI in pediatric surgery?"
    )
    assert pico.population is not None
    assert pico.intervention is not None
    
    # 2. Generate queries
    query_service = QueryGeneratorService()
    queries = await query_service.generate_query(
        pico=pico,
        database=DatabaseType.PUBMED,
        mesh_terms=[]  # Would come from ontology service
    )
    assert len(queries.lines) > 0
    
    # 3. Execute (mock or real)
    # ...
    
    # 4. Generate document
    renderer = DocumentRendererService(Path("./templates"))
    doc_path = renderer.render_pdf(document, Path("./test_output.pdf"))
    assert doc_path.exists()
```

---

## 12. Validation Checklist

Before demo, verify:

**Search Strategy Document:**
- [ ] PICO extraction returns sensible terms for test questions
- [ ] Generated PubMed query is valid (test in PubMed Advanced Search)
- [ ] Generated Embase query is valid (test in Ovid)
- [ ] Search execution returns expected citation counts
- [ ] Deduplication correctly identifies duplicates
- [ ] PDF output matches Montreal Children's Hospital format exactly
- [ ] Per-database counts table is accurate
- [ ] Supplementary material shows all query lines with results
- [ ] Document renders without errors

**PROSPERO Protocol:**
- [ ] All 40 PROSPERO fields are generated
- [ ] Required fields (*) are populated and flagged if empty
- [ ] Title follows PROSPERO format guidelines
- [ ] Review question includes explicit PICO elements
- [ ] Inclusion/exclusion criteria are specific and measurable
- [ ] Team members formatted correctly (Name, Dept, Institution, City, Country)
- [ ] Searches section lists all databases with date range
- [ ] Data synthesis strategy matches study types
- [ ] Markdown output is copy-paste ready into PROSPERO web form
- [ ] DOCX output maintains field structure for editing

**API Endpoints:**
- [ ] `/parse-pico` responds correctly
- [ ] `/generate-queries` responds correctly
- [ ] `/execute` responds correctly
- [ ] `/generate-document` responds correctly
- [ ] `/generate-prospero` responds correctly

---

## 13. Sample Output Verification

Test with this question: **"What is the effectiveness of AI in pediatric surgery?"**

Expected PubMed query structure:
```
#1  "Artificial Intelligence"[MeSH Terms]
#2  "Machine Learning"[MeSH Terms]  
#3  "Deep Learning"[MeSH Terms]
#4  "Neural Networks, Computer"[MeSH Terms]
#5  (artificial intelligence[tiab] OR machine learning[tiab] OR deep learning[tiab] OR neural network*[tiab])
#6  #1 OR #2 OR #3 OR #4 OR #5
#7  "Pediatrics"[MeSH Terms]
#8  "Child"[MeSH Terms]
#9  "Infant"[MeSH Terms]
#10 (pediatric*[tiab] OR paediatric*[tiab] OR child*[tiab] OR infant*[tiab])
#11 #7 OR #8 OR #9 OR #10
#12 "Surgical Procedures, Operative"[MeSH Terms]
#13 (surg*[tiab] OR operat*[tiab])
#14 #12 OR #13
#15 #6 AND #11 AND #14
```

---

*End of Technical Requirements Document*
