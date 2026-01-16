"""
RCT Extraction Pipeline

Main orchestration module that combines:
1. PDF document processing with chunking and embeddings
2. Schema-guided data extraction using Claude LLM
3. Risk of Bias assessment using RoB 2.0 framework
4. Result aggregation and export

This pipeline processes RCT manuscripts to extract structured data fields
and assess risk of bias, producing comprehensive output for systematic reviews.
"""

import os
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed

import pandas as pd
from tqdm import tqdm

from .extractor import RCTExtractor, get_model_info
from .rob_assessor import RoBAssessor, get_rob_model_info, ROB_AVAILABLE

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# Pipeline Configuration
# ============================================================================

class PipelineConfig:
    """Configuration for the extraction pipeline"""
    
    def __init__(
        self,
        # Extraction settings
        extraction_model: str = "claude-3-5-sonnet-20241022",
        extraction_temperature: float = 0.0,
        chunk_size: int = 2000,
        chunk_overlap: int = 400,
        top_k: int = 8,
        
        # GROBID settings (for section-aware parsing)
        grobid_url: str = "http://localhost:8070",
        use_grobid: bool = True,
        
        # RoB settings
        rob_model: str = "gpt-4o",
        rob_temperature: float = 0.0,
        run_rob_assessment: bool = True,
        
        # Processing settings
        max_workers: int = 1,  # Sequential by default for API rate limits
        continue_on_error: bool = True,
        save_intermediate: bool = True,
        
        # Output settings
        output_format: str = "both",  # "csv", "json", or "both"
    ):
        self.extraction_model = extraction_model
        self.extraction_temperature = extraction_temperature
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.top_k = top_k
        
        self.grobid_url = grobid_url
        self.use_grobid = use_grobid
        
        self.rob_model = rob_model
        self.rob_temperature = rob_temperature
        self.run_rob_assessment = run_rob_assessment
        
        self.max_workers = max_workers
        self.continue_on_error = continue_on_error
        self.save_intermediate = save_intermediate
        
        self.output_format = output_format


# ============================================================================
# Main Pipeline Class
# ============================================================================

class RCTExtractionPipeline:
    """
    Complete RCT Extraction Pipeline
    
    Orchestrates the full extraction workflow:
    1. Load PDFs from directory
    2. Extract structured data using RAG + Claude
    3. Assess risk of bias using RoB 2.0
    4. Aggregate and export results
    """
    
    def __init__(self, config: Optional[PipelineConfig] = None):
        """
        Initialize the pipeline
        
        Args:
            config: Pipeline configuration (uses defaults if None)
        """
        self.config = config or PipelineConfig()
        
        # Initialize extractor with GROBID support
        self.extractor = RCTExtractor(
            model=self.config.extraction_model,
            temperature=self.config.extraction_temperature,
            top_k=self.config.top_k,
            chunk_size=self.config.chunk_size,
            chunk_overlap=self.config.chunk_overlap,
            grobid_url=self.config.grobid_url,
            use_grobid=self.config.use_grobid,
        )
        
        # Initialize RoB assessor if enabled
        self.rob_assessor = None
        if self.config.run_rob_assessment and ROB_AVAILABLE:
            self.rob_assessor = RoBAssessor(
                model=self.config.rob_model,
                temperature=self.config.rob_temperature,
            )
        elif self.config.run_rob_assessment and not ROB_AVAILABLE:
            logger.warning("RoB assessment requested but package not available")
        
        logger.info("RCT Extraction Pipeline initialized")
    
    def process_single(
        self,
        pdf_path: Path,
        output_dir: Optional[Path] = None,
    ) -> Dict[str, Any]:
        """
        Process a single PDF file
        
        Args:
            pdf_path: Path to the PDF file
            output_dir: Optional directory to save intermediate results
            
        Returns:
            Dictionary containing extraction and RoB assessment results
        """
        logger.info(f"Processing: {pdf_path.name}")
        
        result = {
            "filename": pdf_path.name,
            "processed_at": datetime.utcnow().isoformat(),
            "status": "success",
        }
        
        # Step 1: Extract structured data
        try:
            extraction_result = self.extractor.extract_from_pdf(pdf_path)
            result["extraction"] = extraction_result
            logger.info(f"Extraction complete for {pdf_path.name}")
        except Exception as e:
            logger.error(f"Extraction failed for {pdf_path.name}: {e}")
            result["extraction"] = {"error": str(e)}
            result["status"] = "extraction_failed"
        
        # Step 2: Risk of Bias assessment
        if self.rob_assessor and result["status"] == "success":
            try:
                rob_result = self.rob_assessor.assess(pdf_path)
                result["risk_of_bias"] = rob_result
                
                # Add summary to extraction
                rob_summary = self.rob_assessor.get_summary(rob_result)
                if "extraction" in result and isinstance(result["extraction"], dict):
                    result["extraction"].update(rob_summary)
                
                logger.info(f"RoB assessment complete for {pdf_path.name}")
            except Exception as e:
                logger.error(f"RoB assessment failed for {pdf_path.name}: {e}")
                result["risk_of_bias"] = {"error": str(e)}
                result["status"] = "rob_failed"
        
        # Save intermediate result if configured
        if output_dir and self.config.save_intermediate:
            output_file = output_dir / f"{pdf_path.stem}_result.json"
            with open(output_file, 'w') as f:
                json.dump(result, f, indent=2, default=str)
        
        return result
    
    def process_batch(
        self,
        input_dir: Path,
        output_dir: Path,
        limit: Optional[int] = None,
        pattern: str = "*.pdf",
    ) -> List[Dict[str, Any]]:
        """
        Process a batch of PDF files
        
        Args:
            input_dir: Directory containing PDF files
            output_dir: Directory for output files
            limit: Optional limit on number of files to process
            pattern: Glob pattern for PDF files
            
        Returns:
            List of processing results
        """
        # Create output directory
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Find PDF files
        pdf_files = list(input_dir.glob(pattern))
        if limit:
            pdf_files = pdf_files[:limit]
        
        logger.info(f"Found {len(pdf_files)} PDF files to process")
        
        # Process files
        results = []
        
        if self.config.max_workers > 1:
            # Parallel processing
            with ThreadPoolExecutor(max_workers=self.config.max_workers) as executor:
                futures = {
                    executor.submit(self.process_single, pdf, output_dir): pdf
                    for pdf in pdf_files
                }
                
                for future in tqdm(as_completed(futures), total=len(pdf_files), desc="Processing"):
                    pdf = futures[future]
                    try:
                        result = future.result()
                        results.append(result)
                    except Exception as e:
                        logger.error(f"Failed to process {pdf.name}: {e}")
                        if not self.config.continue_on_error:
                            raise
        else:
            # Sequential processing
            for pdf_path in tqdm(pdf_files, desc="Processing"):
                try:
                    result = self.process_single(pdf_path, output_dir)
                    results.append(result)
                except Exception as e:
                    logger.error(f"Failed to process {pdf_path.name}: {e}")
                    if not self.config.continue_on_error:
                        raise
                    results.append({
                        "filename": pdf_path.name,
                        "status": "failed",
                        "error": str(e),
                    })
        
        # Export results
        self._export_results(results, output_dir)
        
        return results
    
    def _export_results(self, results: List[Dict[str, Any]], output_dir: Path):
        """Export results to file(s)"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Export JSON
        if self.config.output_format in ("json", "both"):
            json_path = output_dir / f"rct_extraction_{timestamp}.json"
            with open(json_path, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            logger.info(f"Results saved to {json_path}")
        
        # Export CSV
        if self.config.output_format in ("csv", "both"):
            # Flatten extraction results for CSV
            rows = []
            for result in results:
                row = {"filename": result.get("filename")}
                
                # Add extraction fields
                extraction = result.get("extraction", {})
                if isinstance(extraction, dict) and "error" not in extraction:
                    row.update(extraction)
                
                # Add RoB fields
                rob = result.get("risk_of_bias", {})
                if isinstance(rob, dict) and "error" not in rob:
                    for domain, data in rob.get("domains", {}).items():
                        row[f"rob_{domain}"] = data.get("judgment")
                
                row["status"] = result.get("status")
                rows.append(row)
            
            df = pd.DataFrame(rows)
            csv_path = output_dir / f"rct_extraction_{timestamp}.csv"
            df.to_csv(csv_path, index=False)
            logger.info(f"Results saved to {csv_path}")
    
    def get_pipeline_info(self) -> Dict[str, Any]:
        """Get complete information about the pipeline configuration"""
        info = {
            "pipeline_version": "1.0.0",
            "timestamp": datetime.utcnow().isoformat(),
            "configuration": {
                "extraction_model": self.config.extraction_model,
                "extraction_temperature": self.config.extraction_temperature,
                "chunk_size": self.config.chunk_size,
                "chunk_overlap": self.config.chunk_overlap,
                "top_k": self.config.top_k,
                "rob_enabled": self.config.run_rob_assessment,
                "rob_model": self.config.rob_model if self.config.run_rob_assessment else None,
            },
            "extraction_info": get_model_info(),
        }
        
        if self.config.run_rob_assessment and ROB_AVAILABLE:
            info["rob_info"] = get_rob_model_info()
        
        return info


# ============================================================================
# Convenience Functions
# ============================================================================

def run_pipeline(
    input_dir: str,
    output_dir: str,
    limit: Optional[int] = None,
    run_rob: bool = True,
    extraction_model: str = "claude-3-5-sonnet-20241022",
    rob_model: str = "gpt-4o",
) -> List[Dict[str, Any]]:
    """
    Convenience function to run the complete pipeline
    
    Args:
        input_dir: Directory containing PDF files
        output_dir: Directory for output files
        limit: Optional limit on files to process
        run_rob: Whether to run Risk of Bias assessment
        extraction_model: Model for data extraction
        rob_model: Model for RoB assessment
        
    Returns:
        List of processing results
    """
    config = PipelineConfig(
        extraction_model=extraction_model,
        rob_model=rob_model,
        run_rob_assessment=run_rob,
    )
    
    pipeline = RCTExtractionPipeline(config)
    
    return pipeline.process_batch(
        input_dir=Path(input_dir),
        output_dir=Path(output_dir),
        limit=limit,
    )


# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="RCT Extraction Pipeline")
    parser.add_argument("input_dir", help="Directory containing PDF files")
    parser.add_argument("output_dir", help="Directory for output files")
    parser.add_argument("--limit", type=int, help="Limit number of files")
    parser.add_argument("--no-rob", action="store_true", help="Skip RoB assessment")
    parser.add_argument("--extraction-model", default="claude-3-5-sonnet-20241022")
    parser.add_argument("--rob-model", default="gpt-4o")
    
    args = parser.parse_args()
    
    results = run_pipeline(
        input_dir=args.input_dir,
        output_dir=args.output_dir,
        limit=args.limit,
        run_rob=not args.no_rob,
        extraction_model=args.extraction_model,
        rob_model=args.rob_model,
    )
    
    print(f"\nProcessed {len(results)} files")
    success = sum(1 for r in results if r.get("status") == "success")
    print(f"Successful: {success}/{len(results)}")
