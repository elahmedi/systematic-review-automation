"""
RCT Data Extraction Module

Uses LangChain with Anthropic Claude for schema-guided data extraction from RCT PDFs.
Implements RAG (Retrieval-Augmented Generation) with ChromaDB for efficient document processing.

Supports two document processing modes:
1. GROBID-based: Section-aware parsing for scientific papers (recommended)
2. Fallback: RecursiveCharacterTextSplitter for generic PDF processing
"""

import os
import json
import logging
import requests
import xml.etree.ElementTree as ET
import base64
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any, Tuple
from dataclasses import dataclass, field

# PyMuPDF for image extraction
try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False
    fitz = None

from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_aws import BedrockEmbeddings, ChatBedrock
from langchain_chroma import Chroma
from langchain_core.documents import Document

from .schema import EXTRACTION_SCHEMA, RCTExtraction, DemographicsGroup

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================================================
# Configuration
# ============================================================================

# Default chunking parameters
DEFAULT_CHUNK_SIZE = 2000          # Characters per chunk
DEFAULT_CHUNK_OVERLAP = 400        # Overlap between chunks for context continuity
DEFAULT_TOP_K = 8                  # Number of relevant chunks to retrieve

# Token limits
MAX_CONTEXT_TOKENS = 200000        # Claude 3.5 Sonnet v2 context window (200k on Bedrock)

# AWS Bedrock Configuration
BEDROCK_REGION = "us-east-1"       # AWS region for Bedrock

# Embedding Model (Amazon Titan Embeddings V2)
EMBEDDING_MODEL = "amazon.titan-embed-text-v2:0"
EMBEDDING_DIMENSIONS = 1024        # Titan V2 outputs 1024 dimensions

# LLM Configuration (Claude Opus 4.5 via Bedrock - US inference profile)
DEFAULT_MODEL = "us.anthropic.claude-opus-4-5-20251101-v1:0"
DEFAULT_TEMPERATURE = 0.0          # Deterministic for extraction tasks

# GROBID Configuration
DEFAULT_GROBID_URL = "http://localhost:8070"  # Default GROBID server URL
GROBID_TIMEOUT = 120  # Seconds

# GROBID Docker Configuration
GROBID_DOCKER_IMAGE_CRF = "grobid/grobid:0.8.2.1-crf"      # Lightweight CRF model (~1GB)
GROBID_DOCKER_IMAGE_FULL = "grobid/grobid:0.8.2.1-full"    # Full DL model with GPU support (~17GB)
GROBID_CONTAINER_NAME = "grobid"
GROBID_PORT = 8070


# ============================================================================
# GROBID TEI-XML Namespace
# ============================================================================

TEI_NS = {"tei": "http://www.tei-c.org/ns/1.0"}


# ============================================================================
# GROBID Docker Manager
# ============================================================================

class GrobidDockerManager:
    """
    Manages GROBID Docker container lifecycle with automatic GPU detection.
    
    Uses the full DL model when GPU is available, falls back to lightweight CRF model otherwise.
    """
    
    def __init__(
        self,
        container_name: str = GROBID_CONTAINER_NAME,
        port: int = GROBID_PORT,
        image_crf: str = GROBID_DOCKER_IMAGE_CRF,
        image_full: str = GROBID_DOCKER_IMAGE_FULL,
    ):
        self.container_name = container_name
        self.port = port
        self.image_crf = image_crf
        self.image_full = image_full
        self._has_gpu = None
        self._has_docker = None
    
    @staticmethod
    def check_gpu_available() -> bool:
        """Check if NVIDIA GPU is available for Docker"""
        import subprocess
        try:
            result = subprocess.run(
                ["nvidia-smi"],
                capture_output=True,
                timeout=10
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    @staticmethod
    def check_docker_available() -> bool:
        """Check if Docker is installed and running"""
        import subprocess
        try:
            result = subprocess.run(
                ["docker", "info"],
                capture_output=True,
                timeout=10
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    @property
    def has_gpu(self) -> bool:
        """Cached GPU availability check"""
        if self._has_gpu is None:
            self._has_gpu = self.check_gpu_available()
        return self._has_gpu
    
    @property
    def has_docker(self) -> bool:
        """Cached Docker availability check"""
        if self._has_docker is None:
            self._has_docker = self.check_docker_available()
        return self._has_docker
    
    @property
    def selected_image(self) -> str:
        """Select appropriate Docker image based on GPU availability"""
        if self.has_gpu:
            logger.info(f"GPU detected, using full GROBID image: {self.image_full}")
            return self.image_full
        else:
            logger.info(f"No GPU detected, using CRF GROBID image: {self.image_crf}")
            return self.image_crf
    
    def get_container_status(self) -> Optional[str]:
        """
        Get GROBID container status.
        
        Returns:
            'running', 'stopped', or None if container doesn't exist
        """
        import subprocess
        try:
            result = subprocess.run(
                ["docker", "inspect", "-f", "{{.State.Status}}", self.container_name],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                return result.stdout.strip()
            return None
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return None
    
    def start_container(self, force_restart: bool = False) -> bool:
        """
        Start the GROBID Docker container.
        
        Args:
            force_restart: If True, removes existing container and starts fresh
            
        Returns:
            True if container started successfully
        """
        import subprocess
        import time
        
        if not self.has_docker:
            logger.error("Docker is not available")
            return False
        
        status = self.get_container_status()
        
        # Container is already running
        if status == "running" and not force_restart:
            logger.info(f"GROBID container '{self.container_name}' is already running")
            return True
        
        # Remove existing container if needed
        if status is not None:
            if force_restart or status != "running":
                logger.info(f"Removing existing GROBID container (status: {status})")
                subprocess.run(
                    ["docker", "rm", "-f", self.container_name],
                    capture_output=True,
                    timeout=30
                )
        
        # Build docker run command
        image = self.selected_image
        cmd = [
            "docker", "run", "-d",
            "--name", self.container_name,
            "-p", f"{self.port}:{self.port}",
        ]
        
        # Add GPU support if available and using full image
        if self.has_gpu and image == self.image_full:
            cmd.extend(["--gpus", "all"])
        
        cmd.append(image)
        
        logger.info(f"Starting GROBID container: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            if result.returncode != 0:
                logger.error(f"Failed to start GROBID: {result.stderr}")
                return False
            
            # Wait for GROBID to be ready
            logger.info("Waiting for GROBID to initialize...")
            for i in range(30):  # Wait up to 30 seconds
                time.sleep(1)
                try:
                    response = requests.get(
                        f"http://localhost:{self.port}/api/isalive",
                        timeout=5
                    )
                    if response.status_code == 200:
                        logger.info("GROBID is ready!")
                        return True
                except requests.exceptions.RequestException:
                    pass
            
            logger.warning("GROBID started but may not be fully ready")
            return True
            
        except subprocess.TimeoutExpired:
            logger.error("Timeout starting GROBID container")
            return False
    
    def stop_container(self) -> bool:
        """Stop the GROBID Docker container"""
        import subprocess
        
        if not self.has_docker:
            return False
        
        try:
            result = subprocess.run(
                ["docker", "stop", self.container_name],
                capture_output=True,
                timeout=30
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def get_info(self) -> Dict[str, Any]:
        """Get information about GROBID Docker setup"""
        return {
            "docker_available": self.has_docker,
            "gpu_available": self.has_gpu,
            "selected_image": self.selected_image if self.has_docker else None,
            "container_name": self.container_name,
            "container_status": self.get_container_status(),
            "port": self.port,
            "grobid_url": f"http://localhost:{self.port}",
        }


# Global GROBID Docker manager instance
grobid_docker = GrobidDockerManager()


# ============================================================================
# Section Mapping for RCT Papers (IMRaD structure)
# ============================================================================

# Map section titles to canonical section types for RCT papers
SECTION_TYPE_MAPPING = {
    # Abstract
    "abstract": "abstract",
    "summary": "abstract",
    
    # Introduction
    "introduction": "introduction",
    "background": "introduction",
    "rationale": "introduction",
    
    # Methods
    "methods": "methods",
    "methodology": "methods",
    "materials and methods": "methods",
    "patients and methods": "methods",
    "study design": "methods",
    "study population": "methods",
    "participants": "methods",
    "randomization": "methods",
    "randomisation": "methods",
    "blinding": "methods",
    "masking": "methods",
    "interventions": "methods",
    "intervention": "methods",
    "outcomes": "methods",
    "outcome measures": "methods",
    "statistical analysis": "methods",
    "statistical methods": "methods",
    "sample size": "methods",
    "ethics": "methods",
    "ethical considerations": "methods",
    
    # Results
    "results": "results",
    "findings": "results",
    "patient characteristics": "results",
    "baseline characteristics": "results",
    "primary outcome": "results",
    "secondary outcomes": "results",
    "adverse events": "results",
    "safety": "results",
    
    # Discussion
    "discussion": "discussion",
    "interpretation": "discussion",
    "limitations": "discussion",
    "strengths and limitations": "discussion",
    
    # Conclusion
    "conclusion": "conclusion",
    "conclusions": "conclusion",
    
    # Other sections
    "acknowledgments": "acknowledgments",
    "acknowledgements": "acknowledgments",
    "funding": "funding",
    "conflicts of interest": "conflicts",
    "competing interests": "conflicts",
    "disclosures": "conflicts",
    "references": "references",
    "supplementary": "supplementary",
    "appendix": "supplementary",
}

# Fields and their most relevant sections for targeted retrieval
FIELD_SECTION_RELEVANCE = {
    "title": ["header", "abstract"],
    "journalName": ["header"],
    "yearOfPublication": ["header"],
    "funding": ["funding", "acknowledgments", "methods"],
    "fundingType": ["funding", "acknowledgments"],
    "trialRegistration": ["methods", "abstract", "header"],
    "registrationPlatform": ["methods", "abstract"],
    "registrationNumber": ["methods", "abstract"],
    "randomization": ["methods"],
    "blinding": ["methods"],
    "stratification": ["methods"],
    "blocking": ["methods"],
    "concealment": ["methods"],
    "totalParticipants": ["methods", "results"],
    "primaryOutcome": ["methods", "results"],
    "statisticalPower": ["methods"],
    "powerCalculation": ["methods"],
    "totalRandomized": ["results", "methods"],
    "demographics": ["results"],
}


# ============================================================================
# Data Classes for Structured Sections
# ============================================================================

@dataclass
class PaperSection:
    """Represents a section extracted from a research paper"""
    title: str
    content: str
    section_type: str  # Canonical type (e.g., "methods", "results")
    section_number: Optional[str] = None
    parent_section: Optional[str] = None
    page_numbers: List[int] = field(default_factory=list)
    
    def to_document(self, paper_title: str = "", filename: str = "") -> Document:
        """Convert to LangChain Document with metadata"""
        metadata = {
            "section_title": self.title,
            "section_type": self.section_type,
            "section_number": self.section_number or "",
            "parent_section": self.parent_section or "",
            "paper_title": paper_title,
            "filename": filename,
            "source": "grobid",
        }
        if self.page_numbers:
            metadata["pages"] = self.page_numbers
        
        return Document(page_content=self.content, metadata=metadata)


@dataclass  
class ParsedPaper:
    """Complete parsed paper with all sections and metadata"""
    title: str
    authors: List[str]
    abstract: str
    sections: List[PaperSection]
    references: List[Dict[str, str]]
    filename: str = ""
    # Additional metadata from GROBID header
    journal_name: str = ""
    journal_abbrev: str = ""
    publisher: str = ""
    year_of_publication: Optional[int] = None
    publication_date: str = ""
    doi: str = ""
    volume: str = ""
    issue: str = ""
    pages: str = ""
    keywords: List[str] = field(default_factory=list)
    author_affiliations: List[Dict[str, str]] = field(default_factory=list)
    corresponding_author: str = ""
    corresponding_author_email: str = ""
    corresponding_author_country: str = ""
    # Figures and tables
    figures: List[Dict[str, str]] = field(default_factory=list)
    tables: List[Dict[str, Any]] = field(default_factory=list)
    
    def get_sections_by_type(self, section_type: str) -> List[PaperSection]:
        """Get all sections of a given type"""
        return [s for s in self.sections if s.section_type == section_type]
    
    def get_header_content(self) -> str:
        """Generate a formatted header section with all metadata"""
        lines = ["=== PAPER METADATA ==="]
        lines.append(f"Title: {self.title}")
        lines.append(f"Journal: {self.journal_name}")
        if self.journal_abbrev:
            lines.append(f"Journal Abbreviation: {self.journal_abbrev}")
        if self.publisher:
            lines.append(f"Publisher: {self.publisher}")
        if self.year_of_publication:
            lines.append(f"Year of Publication: {self.year_of_publication}")
        if self.publication_date:
            lines.append(f"Publication Date: {self.publication_date}")
        if self.doi:
            lines.append(f"DOI: {self.doi}")
        if self.volume:
            lines.append(f"Volume: {self.volume}")
        if self.issue:
            lines.append(f"Issue: {self.issue}")
        if self.pages:
            lines.append(f"Pages: {self.pages}")
        
        lines.append(f"\nAuthors ({len(self.authors)} total):")
        for i, author in enumerate(self.authors, 1):
            lines.append(f"  {i}. {author}")
        
        if self.corresponding_author:
            lines.append(f"\nCorresponding Author: {self.corresponding_author}")
        if self.corresponding_author_email:
            lines.append(f"Corresponding Author Email: {self.corresponding_author_email}")
        if self.corresponding_author_country:
            lines.append(f"Corresponding Author Country: {self.corresponding_author_country}")
        
        if self.author_affiliations:
            lines.append("\nAuthor Affiliations:")
            for aff in self.author_affiliations:
                aff_str = aff.get('institution', '')
                if aff.get('country'):
                    aff_str += f", {aff['country']}"
                lines.append(f"  - {aff_str}")
        
        if self.keywords:
            lines.append(f"\nKeywords: {', '.join(self.keywords)}")
        
        return "\n".join(lines)
    
    def to_documents(self) -> List[Document]:
        """Convert all sections to LangChain Documents"""
        docs = []
        
        # Add header metadata as a document (CRITICAL for extraction!)
        header_content = self.get_header_content()
        docs.append(Document(
            page_content=header_content,
            metadata={
                "section_title": "Paper Header/Metadata",
                "section_type": "header",
                "paper_title": self.title,
                "filename": self.filename,
                "source": "grobid",
            }
        ))
        
        # Add abstract as a document
        if self.abstract:
            docs.append(Document(
                page_content=self.abstract,
                metadata={
                    "section_title": "Abstract",
                    "section_type": "abstract",
                    "paper_title": self.title,
                    "filename": self.filename,
                    "source": "grobid",
                }
            ))
        
        # Add all sections
        for section in self.sections:
            docs.append(section.to_document(self.title, self.filename))
        
        # Add tables as documents (CRITICAL for results extraction!)
        for table in self.tables:
            table_content = self._format_table_content(table)
            docs.append(Document(
                page_content=table_content,
                metadata={
                    "section_title": table.get("label", "Table"),
                    "section_type": "table",
                    "paper_title": self.title,
                    "filename": self.filename,
                    "source": "grobid",
                }
            ))
        
        # Add figures as documents
        for figure in self.figures:
            fig_content = f"Figure {figure.get('label', '')}: {figure.get('caption', '')}"
            if fig_content.strip():
                docs.append(Document(
                    page_content=fig_content,
                    metadata={
                        "section_title": figure.get("label", "Figure"),
                        "section_type": "figure",
                        "paper_title": self.title,
                        "filename": self.filename,
                        "source": "grobid",
                    }
                ))
        
        return docs
    
    def _format_table_content(self, table: Dict[str, Any]) -> str:
        """Format table data as readable text for LLM"""
        lines = []
        
        # Table header
        label = table.get("label", "Table")
        caption = table.get("caption", "")
        lines.append(f"=== {label}: {caption} ===")
        
        # Table description if present
        desc = table.get("description", "")
        if desc:
            lines.append(f"Description: {desc}")
        
        # Table data
        rows = table.get("rows", [])
        if rows:
            lines.append("\nTable Data:")
            # Try to format as aligned table
            if rows:
                # Get max width for each column
                col_widths = []
                for row in rows:
                    for i, cell in enumerate(row):
                        cell_str = str(cell) if cell else ""
                        if i >= len(col_widths):
                            col_widths.append(len(cell_str))
                        else:
                            col_widths[i] = max(col_widths[i], len(cell_str))
                
                # Format rows
                for i, row in enumerate(rows):
                    row_str = " | ".join(
                        str(cell if cell else "").ljust(col_widths[j] if j < len(col_widths) else 0)
                        for j, cell in enumerate(row)
                    )
                    lines.append(row_str)
                    # Add separator after header row
                    if i == 0:
                        lines.append("-" * len(row_str))
        
        return "\n".join(lines)


# ============================================================================
# GROBID Client
# ============================================================================

class GrobidClient:
    """Client for interacting with GROBID server"""
    
    def __init__(self, grobid_url: str = DEFAULT_GROBID_URL, timeout: int = GROBID_TIMEOUT):
        self.grobid_url = grobid_url.rstrip("/")
        self.timeout = timeout
        self._available = None
    
    def is_available(self) -> bool:
        """Check if GROBID server is available"""
        if self._available is not None:
            return self._available
        
        try:
            response = requests.get(
                f"{self.grobid_url}/api/isalive",
                timeout=5
            )
            self._available = response.status_code == 200
        except Exception as e:
            logger.warning(f"GROBID server not available at {self.grobid_url}: {e}")
            self._available = False
        
        return self._available
    
    def process_fulltext(self, pdf_path: Path) -> Optional[str]:
        """
        Process a PDF and return TEI-XML fulltext
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            TEI-XML string or None if failed
        """
        if not self.is_available():
            return None
        
        try:
            with open(pdf_path, 'rb') as f:
                response = requests.post(
                    f"{self.grobid_url}/api/processFulltextDocument",
                    files={"input": (pdf_path.name, f, "application/pdf")},
                    data={
                        "consolidateHeader": "1",
                        "consolidateCitations": "0",
                        "includeRawCitations": "0",
                        "includeRawAffiliations": "0",
                        "teiCoordinates": "figure",  # Request coordinates for figures
                        "segmentSentences": "0",
                    },
                    timeout=self.timeout
                )
            
            if response.status_code == 200:
                return response.text
            else:
                logger.error(f"GROBID returned status {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"GROBID processing failed: {e}")
            return None


# ============================================================================
# GROBID TEI-XML Parser
# ============================================================================

class GrobidParser:
    """Parser for GROBID TEI-XML output"""
    
    @staticmethod
    def _get_text(element: Optional[ET.Element]) -> str:
        """Extract all text from an element, including nested elements"""
        if element is None:
            return ""
        return "".join(element.itertext()).strip()
    
    @staticmethod
    def _normalize_section_title(title: str) -> str:
        """Normalize section title for matching"""
        return title.lower().strip().rstrip(".:)")
    
    @staticmethod
    def _get_section_type(title: str) -> str:
        """Map section title to canonical section type"""
        normalized = GrobidParser._normalize_section_title(title)
        
        # Direct match
        if normalized in SECTION_TYPE_MAPPING:
            return SECTION_TYPE_MAPPING[normalized]
        
        # Partial match (e.g., "2.1 Statistical Analysis" -> "methods")
        for key, value in SECTION_TYPE_MAPPING.items():
            if key in normalized:
                return value
        
        return "other"
    
    def parse(self, tei_xml: str, filename: str = "") -> ParsedPaper:
        """
        Parse GROBID TEI-XML into structured paper with full metadata
        
        Args:
            tei_xml: TEI-XML string from GROBID
            filename: Original filename for metadata
            
        Returns:
            ParsedPaper object with extracted sections and metadata
        """
        root = ET.fromstring(tei_xml)
        
        # Extract title
        title_elem = root.find(".//tei:titleStmt/tei:title", TEI_NS)
        title = self._get_text(title_elem) if title_elem is not None else ""
        
        # Extract authors and their affiliations
        authors = []
        author_affiliations = []
        corresponding_author = ""
        corresponding_author_email = ""
        corresponding_author_country = ""
        
        for author in root.findall(".//tei:sourceDesc//tei:author", TEI_NS):
            forename = author.find(".//tei:forename", TEI_NS)
            surname = author.find(".//tei:surname", TEI_NS)
            if surname is not None:
                name = self._get_text(surname)
                if forename is not None:
                    name = f"{self._get_text(forename)} {name}"
                authors.append(name)
                
                # Check if this is corresponding author
                if author.get("role") == "corresp":
                    corresponding_author = name
                    # Get email
                    email_elem = author.find(".//tei:email", TEI_NS)
                    if email_elem is not None:
                        corresponding_author_email = self._get_text(email_elem)
                    
                    # Get affiliation and country
                    affiliation = author.find(".//tei:affiliation", TEI_NS)
                    if affiliation is not None:
                        country = self._extract_country_from_affiliation(affiliation)
                        if country:
                            corresponding_author_country = country
            
            # Extract affiliation for all authors
            affiliation = author.find(".//tei:affiliation", TEI_NS)
            if affiliation is not None:
                aff_info = self._parse_affiliation(affiliation)
                if aff_info and aff_info not in author_affiliations:
                    author_affiliations.append(aff_info)
        
        # Extract journal information from monogr
        monogr = root.find(".//tei:sourceDesc//tei:monogr", TEI_NS)
        journal_name = ""
        journal_abbrev = ""
        publisher = ""
        volume = ""
        issue = ""
        pages = ""
        
        if monogr is not None:
            # Journal title
            journal_title = monogr.find("tei:title[@level='j'][@type='main']", TEI_NS)
            if journal_title is not None:
                journal_name = self._get_text(journal_title)
            
            # Journal abbreviation
            journal_abbr = monogr.find("tei:title[@level='j'][@type='abbrev']", TEI_NS)
            if journal_abbr is not None:
                journal_abbrev = self._get_text(journal_abbr)
            
            # Publisher
            pub_elem = monogr.find(".//tei:publisher", TEI_NS)
            if pub_elem is not None:
                publisher = self._get_text(pub_elem)
            
            # Volume, issue, pages
            imprint = monogr.find("tei:imprint", TEI_NS)
            if imprint is not None:
                vol_elem = imprint.find("tei:biblScope[@unit='volume']", TEI_NS)
                if vol_elem is not None:
                    volume = self._get_text(vol_elem)
                
                issue_elem = imprint.find("tei:biblScope[@unit='issue']", TEI_NS)
                if issue_elem is not None:
                    issue = self._get_text(issue_elem)
                
                page_elem = imprint.find("tei:biblScope[@unit='page']", TEI_NS)
                if page_elem is not None:
                    page_from = page_elem.get("from", "")
                    page_to = page_elem.get("to", "")
                    if page_from and page_to:
                        pages = f"{page_from}-{page_to}"
                    elif page_from:
                        pages = page_from
        
        # Extract publication date
        year_of_publication = None
        publication_date = ""
        date_elem = root.find(".//tei:publicationStmt/tei:date[@type='published']", TEI_NS)
        if date_elem is not None:
            when = date_elem.get("when", "")
            publication_date = when
            if when:
                try:
                    year_of_publication = int(when.split("-")[0])
                except (ValueError, IndexError):
                    pass
        
        # Extract DOI
        doi = ""
        doi_elem = root.find(".//tei:idno[@type='DOI']", TEI_NS)
        if doi_elem is not None:
            doi = self._get_text(doi_elem)
        
        # Extract keywords
        keywords = []
        for term in root.findall(".//tei:profileDesc//tei:keywords//tei:term", TEI_NS):
            kw = self._get_text(term)
            if kw:
                keywords.append(kw)
        
        # Extract abstract
        abstract_elem = root.find(".//tei:profileDesc/tei:abstract", TEI_NS)
        abstract = self._get_text(abstract_elem) if abstract_elem is not None else ""
        
        # Extract body sections
        sections = []
        body = root.find(".//tei:body", TEI_NS)
        
        if body is not None:
            for div in body.findall(".//tei:div", TEI_NS):
                section = self._parse_div(div)
                if section and section.content.strip():
                    sections.append(section)
        
        # Extract figures and tables from body
        figures = []
        tables = []
        
        for figure in root.findall(".//tei:body//tei:figure", TEI_NS):
            fig_type = figure.get("type", "")
            
            if fig_type == "table":
                # Parse table
                table_data = self._parse_table(figure)
                if table_data:
                    tables.append(table_data)
            else:
                # Parse figure
                fig_data = self._parse_figure(figure)
                if fig_data:
                    figures.append(fig_data)
        
        # Also check for figures/tables outside body (some GROBID outputs)
        for figure in root.findall(".//tei:figure", TEI_NS):
            if body is not None and figure in body.iter():
                continue  # Already processed
            
            fig_type = figure.get("type", "")
            if fig_type == "table":
                table_data = self._parse_table(figure)
                if table_data and table_data not in tables:
                    tables.append(table_data)
            else:
                fig_data = self._parse_figure(figure)
                if fig_data and fig_data not in figures:
                    figures.append(fig_data)
        
        # Extract references (basic)
        references = []
        for ref in root.findall(".//tei:listBibl/tei:biblStruct", TEI_NS):
            ref_title = ref.find(".//tei:title", TEI_NS)
            if ref_title is not None:
                references.append({"title": self._get_text(ref_title)})
        
        return ParsedPaper(
            title=title,
            authors=authors,
            abstract=abstract,
            sections=sections,
            references=references,
            filename=filename,
            journal_name=journal_name,
            journal_abbrev=journal_abbrev,
            publisher=publisher,
            year_of_publication=year_of_publication,
            publication_date=publication_date,
            doi=doi,
            volume=volume,
            issue=issue,
            pages=pages,
            keywords=keywords,
            author_affiliations=author_affiliations,
            corresponding_author=corresponding_author,
            corresponding_author_email=corresponding_author_email,
            corresponding_author_country=corresponding_author_country,
            figures=figures,
            tables=tables,
        )
    
    def _parse_affiliation(self, affiliation: ET.Element) -> Optional[Dict[str, str]]:
        """Parse an affiliation element into a dictionary"""
        result = {}
        
        # Institution
        inst = affiliation.find(".//tei:orgName[@type='institution']", TEI_NS)
        if inst is not None:
            result["institution"] = self._get_text(inst)
        
        # Department/Laboratory
        dept = affiliation.find(".//tei:orgName[@type='department']", TEI_NS)
        if dept is not None:
            result["department"] = self._get_text(dept)
        
        lab = affiliation.find(".//tei:orgName[@type='laboratory']", TEI_NS)
        if lab is not None:
            result["laboratory"] = self._get_text(lab)
        
        # Country from address
        country = self._extract_country_from_affiliation(affiliation)
        if country:
            result["country"] = country
        
        return result if result else None
    
    def _extract_country_from_affiliation(self, affiliation: ET.Element) -> str:
        """Extract country from affiliation address"""
        # Try explicit country element
        country_elem = affiliation.find(".//tei:address/tei:country", TEI_NS)
        if country_elem is not None:
            return self._get_text(country_elem)
        
        # Try to parse from addrLine (common pattern: "City, Country" or "..., Country")
        addr_line = affiliation.find(".//tei:address/tei:addrLine", TEI_NS)
        if addr_line is not None:
            addr_text = self._get_text(addr_line)
            # Common countries in medical research
            countries = [
                "Qatar", "UAE", "United Arab Emirates", "Saudi Arabia", "KSA",
                "Egypt", "Jordan", "Lebanon", "Iraq", "Kuwait", "Bahrain", "Oman",
                "Pakistan", "India", "Iran", "Turkey", "USA", "United States",
                "UK", "United Kingdom", "Germany", "France", "Italy", "Spain",
                "China", "Japan", "South Korea", "Australia", "Canada", "Brazil",
                "Dubai", "Abu Dhabi",  # Cities often used as country indicators
            ]
            for country in countries:
                if country.lower() in addr_text.lower():
                    # Map city names to countries
                    if country in ["Dubai", "Abu Dhabi"]:
                        return "UAE"
                    return country
        
        return ""
    
    def _parse_figure(self, figure: ET.Element) -> Optional[Dict[str, Any]]:
        """Parse a figure element including coordinates for image extraction"""
        head = figure.find("tei:head", TEI_NS)
        label = figure.get("{http://www.w3.org/XML/1998/namespace}id", "")
        fig_label = self._get_text(head) if head is not None else ""
        
        # Get figure label from <label> element if present
        label_elem = figure.find("tei:label", TEI_NS)
        if label_elem is not None:
            fig_label = f"Figure {self._get_text(label_elem)}"
        
        # Get caption from figDesc
        fig_desc = figure.find("tei:figDesc", TEI_NS)
        caption = self._get_text(fig_desc) if fig_desc is not None else ""
        
        coords = None
        coords_source = None
        
        # Try to get coordinates from graphic element first (bitmap images)
        graphic = figure.find("tei:graphic", TEI_NS)
        if graphic is not None:
            coords_str = graphic.get("coords", "")
            if coords_str:
                # Format: "page,x,y,width,height"
                try:
                    parts = coords_str.split(",")
                    if len(parts) >= 5:
                        coords = {
                            "page": int(float(parts[0])),
                            "x": float(parts[1]),
                            "y": float(parts[2]),
                            "width": float(parts[3]),
                            "height": float(parts[4]),
                        }
                        coords_source = "graphic"
                except (ValueError, IndexError):
                    pass
        
        # Fallback: get coords from figure element itself (caption location for vector figures)
        if coords is None:
            fig_coords_str = figure.get("coords", "")
            if fig_coords_str:
                # Can have multiple coord sets separated by semicolons, take the first
                first_coords = fig_coords_str.split(";")[0]
                try:
                    parts = first_coords.split(",")
                    if len(parts) >= 5:
                        coords = {
                            "page": int(float(parts[0])),
                            "x": float(parts[1]),
                            "y": float(parts[2]),
                            "width": float(parts[3]),
                            "height": float(parts[4]),
                            "is_caption_coords": True,  # Flag that these are caption coords, not image
                        }
                        coords_source = "caption"
                except (ValueError, IndexError):
                    pass
        
        if not fig_label and not caption:
            return None
        
        # Filter out non-figure elements (GROBID sometimes misdetects)
        # Real figures should have "Figure" in the label
        is_real_figure = (
            "figure" in fig_label.lower() or
            "fig" in fig_label.lower() or
            (caption and "figure" in caption.lower()[:20])
        )
        
        if not is_real_figure:
            return None
        
        return {
            "id": label,
            "label": fig_label,
            "caption": caption,
            "coords": coords,
            "coords_source": coords_source,
            "image_base64": None,  # Will be populated later
        }
    
    def _parse_table(self, figure: ET.Element) -> Optional[Dict[str, Any]]:
        """Parse a table element (tables are in <figure type='table'>)"""
        # Get table label/title
        head = figure.find("tei:head", TEI_NS)
        table_label = self._get_text(head) if head is not None else ""
        
        # Get label number
        label_elem = figure.find("tei:label", TEI_NS)
        if label_elem is not None:
            label_num = self._get_text(label_elem)
            if not table_label.startswith("Table"):
                table_label = f"Table {label_num}: {table_label}"
        
        # Get description from figDesc
        fig_desc = figure.find("tei:figDesc", TEI_NS)
        description = self._get_text(fig_desc) if fig_desc is not None else ""
        
        # Parse the actual table data
        table_elem = figure.find("tei:table", TEI_NS)
        rows = []
        
        if table_elem is not None:
            for row in table_elem.findall("tei:row", TEI_NS):
                row_data = []
                for cell in row.findall("tei:cell", TEI_NS):
                    cell_text = self._get_text(cell)
                    row_data.append(cell_text)
                if row_data:
                    rows.append(row_data)
        
        if not table_label and not rows:
            return None
        
        return {
            "label": table_label,
            "caption": table_label,
            "description": description,
            "rows": rows,
        }
    
    def _parse_div(self, div: ET.Element, parent_title: str = None) -> Optional[PaperSection]:
        """Parse a div element into a PaperSection"""
        # Get section header
        head = div.find("tei:head", TEI_NS)
        section_title = self._get_text(head) if head is not None else ""
        section_number = head.get("n") if head is not None else None
        
        # Get section content (all paragraphs)
        content_parts = []
        for p in div.findall("tei:p", TEI_NS):
            p_text = self._get_text(p)
            if p_text:
                content_parts.append(p_text)
        
        # Also get any direct text in div
        if div.text and div.text.strip():
            content_parts.insert(0, div.text.strip())
        
        content = "\n\n".join(content_parts)
        
        if not content and not section_title:
            return None
        
        section_type = self._get_section_type(section_title) if section_title else "other"
        
        return PaperSection(
            title=section_title,
            content=content,
            section_type=section_type,
            section_number=section_number,
            parent_section=parent_title,
        )


# ============================================================================
# Document Processor with GROBID Support
# ============================================================================

class DocumentProcessor:
    """
    Handles PDF loading, chunking, and vector storage.
    
    Supports two modes:
    1. GROBID mode: Section-aware parsing (recommended for scientific papers)
    2. Fallback mode: Generic RecursiveCharacterTextSplitter
    """
    
    def __init__(
        self,
        chunk_size: int = DEFAULT_CHUNK_SIZE,
        chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
        embedding_model: str = EMBEDDING_MODEL,
        grobid_url: str = DEFAULT_GROBID_URL,
        use_grobid: bool = True,
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.use_grobid = use_grobid
        
        # Initialize GROBID client
        self.grobid_client = GrobidClient(grobid_url) if use_grobid else None
        self.grobid_parser = GrobidParser() if use_grobid else None
        
        # Initialize fallback text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""],
        )
        
        # Initialize embeddings (AWS Bedrock Titan V2)
        self.embeddings = BedrockEmbeddings(
            model_id=embedding_model,
            region_name=BEDROCK_REGION,
        )
        
        # Check GROBID availability
        self._grobid_available = None
        if use_grobid:
            self._grobid_available = self.grobid_client.is_available()
            if self._grobid_available:
                logger.info(f"GROBID available at {grobid_url}")
            else:
                logger.warning(f"GROBID not available, will use fallback splitter")
        
        logger.info(
            f"DocumentProcessor initialized: chunk_size={chunk_size}, "
            f"overlap={chunk_overlap}, grobid={'enabled' if self._grobid_available else 'disabled'}"
        )
    
    @property
    def grobid_available(self) -> bool:
        """Check if GROBID is available"""
        return self._grobid_available or False
    
    def load_pdf(self, pdf_path: Path) -> Tuple[List[Document], Optional[ParsedPaper]]:
        """
        Load and parse a PDF document.
        
        Returns:
            Tuple of (documents, parsed_paper) where parsed_paper is None if using fallback
        """
        parsed_paper = None
        
        # Try GROBID first
        if self.grobid_available:
            tei_xml = self.grobid_client.process_fulltext(pdf_path)
            if tei_xml:
                parsed_paper = self.grobid_parser.parse(tei_xml, pdf_path.name)
                
                # Extract figure images if PyMuPDF is available
                if PYMUPDF_AVAILABLE and parsed_paper.figures:
                    self._extract_figure_images(pdf_path, parsed_paper)
                
                documents = parsed_paper.to_documents()
                logger.info(
                    f"GROBID parsed '{pdf_path.name}': {len(parsed_paper.sections)} sections, "
                    f"title='{parsed_paper.title[:50]}...'"
                )
                return documents, parsed_paper
        
        # Fallback to PyPDF
        logger.info(f"Using fallback PDF loader for: {pdf_path.name}")
        loader = PyPDFLoader(str(pdf_path))
        documents = loader.load()
        logger.info(f"Loaded PDF with {len(documents)} pages: {pdf_path.name}")
        return documents, None
    
    def _extract_figure_images(self, pdf_path: Path, parsed_paper: ParsedPaper) -> None:
        """
        Extract figure images from PDF using GROBID coordinates.
        
        Handles two cases:
        1. Bitmap images: Uses graphic element coords directly
        2. Vector figures: Expands from caption coords to capture the figure region
        
        Updates the figure dictionaries in parsed_paper with base64-encoded images.
        """
        if not PYMUPDF_AVAILABLE:
            logger.warning("PyMuPDF not available, skipping figure image extraction")
            return
        
        try:
            doc = fitz.open(str(pdf_path))
            
            for figure in parsed_paper.figures:
                coords = figure.get("coords")
                if not coords:
                    continue
                
                page_num = coords["page"] - 1  # GROBID uses 1-indexed pages
                if page_num < 0 or page_num >= len(doc):
                    continue
                
                page = doc[page_num]
                page_width = page.rect.width
                page_height = page.rect.height
                
                # Get base coordinates
                x = coords["x"]
                y = coords["y"]
                width = coords["width"]
                height = coords["height"]
                
                # Check if these are caption coordinates (vector figures)
                if coords.get("is_caption_coords"):
                    # Caption coords are typically small (just text height ~6-10 pts)
                    # The actual figure is usually ABOVE the caption
                    # Expand to capture the figure region
                    
                    # Standard figure region: expand upward and to full column width
                    margin = 20  # Safety margin
                    
                    # Figure is likely above caption, expand upward significantly
                    # Use caption y position as bottom boundary
                    fig_bottom = y + height + 10
                    fig_top = max(50, y - 400)  # Capture ~400pts above caption (typical figure height)
                    
                    # Expand width to reasonable column width
                    fig_left = max(margin, x - 50)
                    fig_right = min(page_width - margin, x + width + 200)
                    
                    # For full-page figures, might need wider capture
                    if "flow" in figure.get("caption", "").lower() or "consort" in figure.get("caption", "").lower():
                        # CONSORT/flow diagrams are typically larger
                        fig_left = margin
                        fig_right = page_width - margin
                        fig_top = max(50, y - 500)
                    
                    clip_rect = fitz.Rect(fig_left, fig_top, fig_right, fig_bottom)
                    logger.debug(f"Vector figure '{figure.get('label')}': expanding from caption coords to {clip_rect}")
                else:
                    # Bitmap image: use coords directly
                    clip_rect = fitz.Rect(x, y, x + width, y + height)
                
                # Ensure clip rect is valid and within page bounds
                clip_rect = clip_rect & page.rect  # Intersect with page
                if clip_rect.is_empty or clip_rect.width < 10 or clip_rect.height < 10:
                    logger.debug(f"Skipping {figure.get('label')}: invalid clip region")
                    continue
                
                # Render the clipped region at higher resolution for clarity
                zoom = 2.0  # 2x zoom for better quality
                mat = fitz.Matrix(zoom, zoom)
                
                try:
                    # Get pixmap of the clipped region
                    pix = page.get_pixmap(matrix=mat, clip=clip_rect)
                    
                    # Convert to PNG bytes
                    img_bytes = pix.tobytes("png")
                    
                    # Encode as base64
                    figure["image_base64"] = base64.b64encode(img_bytes).decode("utf-8")
                    figure["image_format"] = "png"
                    figure["extracted_region"] = {
                        "x": clip_rect.x0,
                        "y": clip_rect.y0,
                        "width": clip_rect.width,
                        "height": clip_rect.height,
                    }
                    logger.debug(f"Extracted image for {figure.get('label', 'figure')}")
                    
                except Exception as e:
                    logger.warning(f"Failed to extract image for {figure.get('label', 'figure')}: {e}")
            
            doc.close()
            
            # Count extracted images
            extracted = sum(1 for f in parsed_paper.figures if f.get("image_base64"))
            logger.info(f"Extracted {extracted}/{len(parsed_paper.figures)} figure images from PDF")
            
        except Exception as e:
            logger.error(f"Failed to extract figure images: {e}")
    
    def chunk_documents(
        self, 
        documents: List[Document], 
        parsed_paper: Optional[ParsedPaper] = None
    ) -> List[Document]:
        """
        Split documents into chunks.
        
        If parsed_paper is provided (GROBID mode), chunks are section-aware.
        Otherwise, uses generic text splitting.
        """
        if parsed_paper is not None:
            # GROBID mode: chunk each section separately to preserve section boundaries
            chunks = []
            for doc in documents:
                section_type = doc.metadata.get("section_type", "other")
                
                # For short sections, keep as-is
                if len(doc.page_content) <= self.chunk_size:
                    chunks.append(doc)
                else:
                    # Split long sections but preserve metadata
                    section_chunks = self.text_splitter.split_documents([doc])
                    for i, chunk in enumerate(section_chunks):
                        chunk.metadata["chunk_index"] = i
                        chunk.metadata["total_chunks"] = len(section_chunks)
                    chunks.extend(section_chunks)
            
            logger.info(f"Created {len(chunks)} section-aware chunks")
            return chunks
        else:
            # Fallback mode: generic splitting
            chunks = self.text_splitter.split_documents(documents)
            logger.info(f"Split into {len(chunks)} chunks (fallback mode)")
            return chunks
    
    def create_vectorstore(
        self, 
        chunks: List[Document], 
        collection_name: str = "rct_chunks"
    ) -> Chroma:
        """Create ChromaDB vector store from chunks"""
        vectorstore = Chroma.from_documents(
            documents=chunks,
            embedding=self.embeddings,
            collection_name=collection_name,
        )
        logger.info(f"Created vector store with {len(chunks)} vectors")
        return vectorstore


# ============================================================================
# Extraction Prompt Templates
# ============================================================================

EXTRACTION_SYSTEM_PROMPT = """You are an expert systematic review data extractor specializing in randomized controlled trials (RCTs).

Your task is to extract structured data from RCT publications with MAXIMUM ACCURACY.

## CRITICAL EXTRACTION RULES:

### For TITLE field:
- Extract the EXACT publication title as it appears at the top of the paper
- The title is NOT the study objective or aim
- The title is NOT the first sentence of the abstract
- Look for the title in the header/beginning of the document

### For CLASSIFICATION/ENUM fields:
- Read the field description AND the option descriptions carefully
- Choose the option that BEST matches what is stated in the paper
- If multiple options could apply, choose the most specific one
- Only use "Unspecified" or "Other" when truly no other option fits

### For BOOLEAN fields:
- true = explicitly stated or clearly implied in the text
- false = explicitly stated as not done/not used
- null = not mentioned at all in the manuscript

### For NUMERIC fields:
- Extract EXACT numbers as reported
- Do NOT round or estimate
- Include units when relevant

### For STRING fields:
- Extract verbatim when possible
- Be comprehensive - include all relevant details

## WHERE TO FIND INFORMATION:
- **Title, Journal, Year**: Header/first page
- **Randomization, Blinding, Sample Size**: Methods section
- **Demographics, Participant Numbers**: Results section, often in Table 1
- **Funding, Registration**: Methods, Acknowledgments, Footnotes, or end of paper
- **Primary Outcome**: Methods (definition) and Results (values)

## OUTPUT:
- Return ONLY valid JSON
- Use null for missing information (not "Not found" or empty string)
- Ensure all enum values match EXACTLY the allowed options"""

EXTRACTION_USER_PROMPT = """# RCT Data Extraction Task

## Paper Title (from document header):
{paper_title}

## Manuscript Content:
{context}

---

## FIELD DEFINITIONS AND EXTRACTION RULES:

{schema}

---

## DEMOGRAPHICS EXTRACTION:
For each treatment arm/group in the study, extract:
- groupName: Name of the group (e.g., "Intervention", "Control", "Drug A", "Placebo")
- meanAge: Mean age in years (number or null)
- sdAge: Standard deviation of age (number or null)  
- medianAge: Median age if reported instead of mean (number or null)
- iqrAge: Interquartile range as string (e.g., "45-62") or null
- femaleProportion: Proportion female as decimal 0-1 (e.g., 0.45 for 45%) or null
- nParticipants: Number of participants in this group (integer or null)

Extract demographics for EACH group separately. If only overall demographics reported, use groupName: "Overall".

---

## YOUR TASK:
Extract ALL fields according to their definitions above. Return ONLY a valid JSON object.

For enum fields, use EXACTLY the option values shown (case-sensitive).
Use null for any field where information is not found in the manuscript.

```json
{{
  "title": "...",
  "journalName": "...",
  ...all other fields...,
  "demographics": [{{...}}, {{...}}]
}}
```"""


# ============================================================================
# RCT Extractor
# ============================================================================

class RCTExtractor:
    """
    Main extraction class using RAG with Claude.
    
    Supports section-aware retrieval when GROBID is available.
    """
    
    def __init__(
        self,
        model: str = DEFAULT_MODEL,
        temperature: float = DEFAULT_TEMPERATURE,
        top_k: int = DEFAULT_TOP_K,
        chunk_size: int = DEFAULT_CHUNK_SIZE,
        chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
        grobid_url: str = DEFAULT_GROBID_URL,
        use_grobid: bool = True,
    ):
        self.model = model
        self.temperature = temperature
        self.top_k = top_k
        
        # Initialize document processor with GROBID support
        self.doc_processor = DocumentProcessor(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            grobid_url=grobid_url,
            use_grobid=use_grobid,
        )
        
        # Initialize LLM (Claude via AWS Bedrock)
        self.llm = ChatBedrock(
            model_id=model,
            region_name=BEDROCK_REGION,
            model_kwargs={
                "temperature": temperature,
                "max_tokens": 8192,
            },
        )
        
        # Build schema string for prompt
        self.schema_string = self._build_schema_string()
        
        logger.info(
            f"RCTExtractor initialized: model={model}, temp={temperature}, "
            f"top_k={top_k}, grobid={'available' if self.doc_processor.grobid_available else 'unavailable'}"
        )
    
    def _build_schema_string(self) -> str:
        """Build a comprehensive formatted schema string for the extraction prompt"""
        schema_parts = []
        
        for field_name, field_info in EXTRACTION_SCHEMA.items():
            desc = field_info['description']
            field_type = field_info['type']
            method = field_info.get('method', 'extract')
            
            # Build detailed field description
            field_str = f"### {field_name}\n"
            field_str += f"- **Type**: {field_type}\n"
            field_str += f"- **Method**: {method}\n"
            field_str += f"- **Description**: {desc}\n"
            
            # Include enum options with their descriptions if available
            if 'enum' in field_info:
                field_str += f"- **Options**:\n"
                enum_descs = field_info.get('enumDescriptions', {})
                for option in field_info['enum']:
                    if option in enum_descs:
                        field_str += f"  - `{option}`: {enum_descs[option]}\n"
                    else:
                        field_str += f"  - `{option}`\n"
            
            schema_parts.append(field_str)
        
        return "\n".join(schema_parts)
    
    def _get_section_aware_queries(self, grobid_mode: bool) -> List[Dict[str, Any]]:
        """
        Get retrieval queries, optionally with section filters for GROBID mode.
        
        Returns list of dicts with 'query' and optional 'section_filter' keys.
        """
        if grobid_mode:
            # Section-aware queries for better precision
            return [
                {"query": "title authors journal publication", "section_filter": ["abstract", "header"]},
                {"query": "randomization method allocation sequence generation", "section_filter": ["methods"]},
                {"query": "blinding masking double-blind open-label", "section_filter": ["methods"]},
                {"query": "sample size power calculation statistical analysis", "section_filter": ["methods"]},
                {"query": "intervention treatment drug dose regimen", "section_filter": ["methods"]},
                {"query": "comparator placebo control group standard of care", "section_filter": ["methods"]},
                {"query": "primary outcome endpoint measure", "section_filter": ["methods", "results"]},
                {"query": "participants enrolled randomized baseline characteristics", "section_filter": ["results"]},
                {"query": "demographics age sex gender", "section_filter": ["results"]},
                {"query": "funding sponsor grant financial support", "section_filter": ["funding", "acknowledgments", "methods"]},
                {"query": "trial registration clinical trial number NCT ISRCTN", "section_filter": ["methods", "abstract"]},
                {"query": "intention to treat per protocol analysis", "section_filter": ["methods", "results"]},
            ]
        else:
            # Generic queries (no section awareness)
            return [
                {"query": "study title, journal, publication year, authors"},
                {"query": "randomization method, allocation concealment, blinding"},
                {"query": "sample size, power calculation, statistical analysis"},
                {"query": "intervention, treatment, drug, comparator, placebo"},
                {"query": "primary outcome, results, effect size"},
                {"query": "funding, trial registration, clinical trial number"},
                {"query": "inclusion exclusion criteria, participants, demographics"},
                {"query": "methods, study design, endpoints"},
            ]
    
    def _retrieve_with_section_filter(
        self,
        retriever,
        query: str,
        section_filter: Optional[List[str]],
        chunks: List[Document],
        k: int,
    ) -> List[Document]:
        """
        Retrieve documents, optionally filtering by section type.
        
        If section_filter is provided, first tries to retrieve from matching sections,
        then falls back to all sections if not enough results.
        """
        if not section_filter:
            return retriever.invoke(query)
        
        # First, get all relevant chunks
        all_results = retriever.invoke(query)
        
        # Filter by section type
        filtered = [
            doc for doc in all_results
            if doc.metadata.get("section_type") in section_filter
        ]
        
        # If we got enough filtered results, use them
        if len(filtered) >= k // 2:
            return filtered[:k]
        
        # Otherwise, supplement with non-filtered results
        seen = set(id(doc) for doc in filtered)
        for doc in all_results:
            if id(doc) not in seen:
                filtered.append(doc)
                if len(filtered) >= k:
                    break
        
        return filtered
    
    def extract_from_pdf(self, pdf_path: Path) -> Dict[str, Any]:
        """
        Extract RCT data from a PDF file using RAG.
        
        Uses GROBID for section-aware parsing if available.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Dictionary containing extracted data
        """
        logger.info(f"Starting extraction for: {pdf_path.name}")
        
        # Load and process document
        documents, parsed_paper = self.doc_processor.load_pdf(pdf_path)
        chunks = self.doc_processor.chunk_documents(documents, parsed_paper)
        
        # Create vector store
        vectorstore = self.doc_processor.create_vectorstore(chunks)
        retriever = vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": self.top_k},
        )
        
        # Determine if we're in GROBID mode
        grobid_mode = parsed_paper is not None
        
        # Get queries (section-aware if GROBID mode)
        queries = self._get_section_aware_queries(grobid_mode)
        
        # Collect all relevant chunks
        all_chunks = []
        seen_content = set()
        
        for query_info in queries:
            query = query_info["query"] if isinstance(query_info, dict) else query_info
            section_filter = query_info.get("section_filter") if isinstance(query_info, dict) else None
            
            retrieved = self._retrieve_with_section_filter(
                retriever, query, section_filter, chunks, self.top_k
            )
            
            for doc in retrieved:
                content_hash = hash(doc.page_content[:200])
                if content_hash not in seen_content:
                    seen_content.add(content_hash)
                    
                    # Add section context to chunk if available
                    if grobid_mode:
                        section_info = f"[Section: {doc.metadata.get('section_title', 'Unknown')}]\n"
                        all_chunks.append(section_info + doc.page_content)
                    else:
                        all_chunks.append(doc.page_content)
        
        # Combine context
        context = "\n\n---\n\n".join(all_chunks)
        
        logger.info(
            f"Retrieved {len(all_chunks)} unique chunks for extraction "
            f"({'section-aware' if grobid_mode else 'generic'} mode)"
        )
        
        # Get paper title from GROBID if available
        paper_title = parsed_paper.title if parsed_paper else "Not available - extract from manuscript"
        
        # Build extraction prompt
        prompt = EXTRACTION_USER_PROMPT.format(
            paper_title=paper_title,
            context=context,
            schema=self.schema_string,
        )
        
        # Build message content - include images if available
        user_content = []
        
        # Add figure images if available (for multimodal extraction)
        if parsed_paper and parsed_paper.figures:
            figures_with_images = [f for f in parsed_paper.figures if f.get("image_base64")]
            if figures_with_images:
                logger.info(f"Including {len(figures_with_images)} figure images in prompt")
                for fig in figures_with_images:
                    # Add image
                    user_content.append({
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/png",
                            "data": fig["image_base64"],
                        }
                    })
                    # Add caption as context
                    user_content.append({
                        "type": "text",
                        "text": f"[{fig.get('label', 'Figure')}: {fig.get('caption', '')}]"
                    })
        
        # Add the main prompt text
        user_content.append({
            "type": "text",
            "text": prompt
        })
        
        # Call LLM for extraction
        messages = [
            {"role": "system", "content": EXTRACTION_SYSTEM_PROMPT},
            {"role": "user", "content": user_content},
        ]
        
        response = self.llm.invoke(messages)
        
        # Parse JSON response
        try:
            response_text = response.content
            
            # Find JSON block
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                json_str = response_text[json_start:json_end].strip()
            elif "```" in response_text:
                json_start = response_text.find("```") + 3
                json_end = response_text.find("```", json_start)
                json_str = response_text[json_start:json_end].strip()
            else:
                json_str = response_text.strip()
            
            extracted_data = json.loads(json_str)
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.debug(f"Response was: {response.content}")
            extracted_data = {"error": str(e), "raw_response": response.content}
        
        # Add metadata
        extracted_data["filename"] = pdf_path.name
        extracted_data["extracted_at"] = datetime.utcnow().isoformat()
        extracted_data["model"] = self.model
        extracted_data["extraction_mode"] = "grobid" if grobid_mode else "fallback"
        
        # Add paper metadata if available from GROBID
        if parsed_paper:
            extracted_data["_grobid_title"] = parsed_paper.title
            extracted_data["_grobid_journal"] = parsed_paper.journal_name
            extracted_data["_grobid_year"] = parsed_paper.year_of_publication
            extracted_data["_grobid_doi"] = parsed_paper.doi
            extracted_data["_grobid_authors"] = parsed_paper.authors
            extracted_data["_grobid_corresponding_author"] = parsed_paper.corresponding_author
            extracted_data["_grobid_corresponding_country"] = parsed_paper.corresponding_author_country
            extracted_data["_grobid_sections"] = [s.section_type for s in parsed_paper.sections]
            extracted_data["_grobid_tables_count"] = len(parsed_paper.tables)
            extracted_data["_grobid_figures_count"] = len(parsed_paper.figures)
            # Include table summaries
            if parsed_paper.tables:
                extracted_data["_grobid_tables"] = [
                    {"label": t.get("label"), "rows": len(t.get("rows", []))}
                    for t in parsed_paper.tables
                ]
        
        # Cleanup vector store
        vectorstore.delete_collection()
        
        logger.info(f"Extraction complete for: {pdf_path.name}")
        
        return extracted_data
    
    def extract_batch(
        self,
        pdf_dir: Path,
        output_path: Optional[Path] = None,
        limit: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        Extract data from multiple PDFs in a directory
        
        Args:
            pdf_dir: Directory containing PDF files
            output_path: Optional path to save results as JSON
            limit: Optional limit on number of files to process
            
        Returns:
            List of extraction results
        """
        pdf_files = list(pdf_dir.glob("*.pdf"))
        
        if limit:
            pdf_files = pdf_files[:limit]
        
        logger.info(f"Processing {len(pdf_files)} PDF files from {pdf_dir}")
        
        results = []
        for i, pdf_path in enumerate(pdf_files, 1):
            logger.info(f"Processing {i}/{len(pdf_files)}: {pdf_path.name}")
            
            try:
                result = self.extract_from_pdf(pdf_path)
                results.append(result)
            except Exception as e:
                logger.error(f"Failed to process {pdf_path.name}: {e}")
                results.append({
                    "filename": pdf_path.name,
                    "error": str(e),
                    "extracted_at": datetime.utcnow().isoformat(),
                })
        
        if output_path:
            with open(output_path, 'w') as f:
                json.dump(results, f, indent=2)
            logger.info(f"Results saved to {output_path}")
        
        return results


# ============================================================================
# Utility Functions
# ============================================================================

def get_model_info() -> Dict[str, Any]:
    """Return information about the models and configuration used"""
    return {
        "extraction_llm": {
            "provider": "AWS Bedrock",
            "model": DEFAULT_MODEL,
            "context_window": MAX_CONTEXT_TOKENS,
            "temperature": DEFAULT_TEMPERATURE,
            "region": BEDROCK_REGION,
        },
        "embedding_model": {
            "provider": "AWS Bedrock",
            "model": EMBEDDING_MODEL,
            "dimensions": EMBEDDING_DIMENSIONS,
            "region": BEDROCK_REGION,
        },
        "vector_database": {
            "name": "ChromaDB",
            "type": "In-memory (ephemeral)",
            "similarity_metric": "Cosine similarity",
        },
        "document_processing": {
            "primary": "GROBID (section-aware parsing)",
            "fallback": "RecursiveCharacterTextSplitter",
            "grobid_url": DEFAULT_GROBID_URL,
            "docker_image_crf": GROBID_DOCKER_IMAGE_CRF,
            "docker_image_full": GROBID_DOCKER_IMAGE_FULL,
            "gpu_available": grobid_docker.has_gpu,
            "selected_image": grobid_docker.selected_image if grobid_docker.has_docker else "N/A",
        },
        "chunking": {
            "strategy": "Section-aware (GROBID) or RecursiveCharacterTextSplitter (fallback)",
            "chunk_size": DEFAULT_CHUNK_SIZE,
            "chunk_overlap": DEFAULT_CHUNK_OVERLAP,
            "tokenizer": "tiktoken (cl100k_base)",
        },
        "retrieval": {
            "strategy": "Section-filtered multi-query similarity search",
            "top_k": DEFAULT_TOP_K,
            "queries_per_document": 12,
        },
    }


def check_grobid_status(grobid_url: str = DEFAULT_GROBID_URL) -> Dict[str, Any]:
    """Check GROBID server status"""
    client = GrobidClient(grobid_url)
    available = client.is_available()
    
    # Include Docker container info
    docker_info = grobid_docker.get_info()
    
    return {
        "url": grobid_url,
        "available": available,
        "message": "GROBID server is running" if available else "GROBID server not available",
        "docker": docker_info,
    }


def ensure_grobid_running(auto_start: bool = True) -> bool:
    """
    Ensure GROBID is running, optionally starting the Docker container.
    
    Args:
        auto_start: If True, automatically start GROBID Docker container if not running
        
    Returns:
        True if GROBID is available
    """
    # First check if GROBID is already running
    client = GrobidClient()
    if client.is_available():
        logger.info("GROBID is already running")
        return True
    
    if not auto_start:
        logger.warning("GROBID is not running and auto_start is disabled")
        return False
    
    # Try to start via Docker
    if not grobid_docker.has_docker:
        logger.error("Docker is not available - cannot auto-start GROBID")
        return False
    
    logger.info("GROBID not running, attempting to start Docker container...")
    if grobid_docker.start_container():
        # Verify it's working
        client._available = None  # Reset cache
        return client.is_available()
    
    return False


def get_grobid_docker_manager() -> GrobidDockerManager:
    """Get the global GROBID Docker manager instance"""
    return grobid_docker
