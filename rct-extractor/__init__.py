"""
RCT Extraction Pipeline

A comprehensive AI-driven pipeline for extracting structured data from
randomized controlled trial (RCT) publications for systematic reviews.

Components:
- extractor: Schema-guided data extraction using RAG + Claude LLM
- rob_assessor: Risk of Bias (RoB 2.0) assessment
- pipeline: Main orchestration module
- cli: Command line interface

Usage:
    from rct_extraction_pipeline import run_pipeline
    
    results = run_pipeline(
        input_dir="./pdfs",
        output_dir="./output",
        limit=10,
    )

CLI:
    rct-extract extract ./pdfs --output ./output
    rct-extract assess manuscript.pdf
    rct-extract info
"""

from .schema import EXTRACTION_SCHEMA, RCTExtraction, get_extraction_prompt
from .extractor import RCTExtractor, DocumentProcessor, get_model_info, check_grobid_status
from .rob_assessor import RoBAssessor, assess_rob, get_rob_model_info, ROB_AVAILABLE
from .pipeline import (
    RCTExtractionPipeline,
    PipelineConfig,
    run_pipeline,
)

__version__ = "1.0.0"
__author__ = "Mohamed Elahmedi"

__all__ = [
    # Schema
    "EXTRACTION_SCHEMA",
    "RCTExtraction",
    "get_extraction_prompt",
    
    # Extraction
    "RCTExtractor",
    "DocumentProcessor",
    "get_model_info",
    "check_grobid_status",
    
    # Risk of Bias
    "RoBAssessor",
    "assess_rob",
    "get_rob_model_info",
    "ROB_AVAILABLE",
    
    # Pipeline
    "RCTExtractionPipeline",
    "PipelineConfig",
    "run_pipeline",
]
