"""
Risk of Bias Assessment Module

Integrates with the risk-of-bias package (forked from https://github.com/rob-luke/risk-of-bias)
to perform RoB 2.0 assessment on RCT manuscripts.

This module provides a wrapper for the risk_of_bias package to:
1. Run RoB 2.0 framework assessment
2. Extract domain-level judgments
3. Integrate results with RCT extraction pipeline
"""

import sys
import logging
from pathlib import Path
from typing import Dict, Any, Optional

# Add risk-of-bias to path
RISK_OF_BIAS_PATH = Path("/home/ec2-user/rola_sysrev/risk-of-bias")
if str(RISK_OF_BIAS_PATH) not in sys.path:
    sys.path.insert(0, str(RISK_OF_BIAS_PATH))

# Import from risk_of_bias package
# Note: Catches both ImportError and TypeError (for Python 3.9 compatibility with union types)
try:
    from risk_of_bias.frameworks import get_rob2_framework
    from risk_of_bias.run_framework import run_framework
    from risk_of_bias.types._framework_types import Framework
    ROB_AVAILABLE = True
except (ImportError, TypeError) as e:
    logging.warning(f"Risk of Bias package not available: {e}")
    logging.warning("Note: risk-of-bias requires Python 3.10+ for full compatibility")
    ROB_AVAILABLE = False
    # Define placeholder for type hints
    Framework = None

logger = logging.getLogger(__name__)


# ============================================================================
# Configuration
# ============================================================================

# Default model for RoB assessment (OpenAI)
DEFAULT_ROB_MODEL = "gpt-4o"  # or "gpt-4-turbo" for faster processing
DEFAULT_ROB_TEMPERATURE = 0.0


# ============================================================================
# RoB 2.0 Domain Names
# ============================================================================

ROB2_DOMAINS = {
    1: "randomization",
    2: "deviations",
    3: "missing_data",
    4: "measurement",
    5: "selection",
    6: "overall",
}

ROB2_DOMAIN_DESCRIPTIONS = {
    "randomization": "Bias arising from the randomization process",
    "deviations": "Bias due to deviations from intended interventions",
    "missing_data": "Bias due to missing outcome data",
    "measurement": "Bias in measurement of the outcome",
    "selection": "Bias in selection of the reported result",
    "overall": "Overall risk of bias judgment",
}


# ============================================================================
# RoB Assessor Class
# ============================================================================

class RoBAssessor:
    """
    Risk of Bias Assessor using the RoB 2.0 framework
    
    This class wraps the risk_of_bias package to assess RCT manuscripts
    according to the Cochrane RoB 2.0 guidelines.
    """
    
    def __init__(
        self,
        model: str = DEFAULT_ROB_MODEL,
        temperature: float = DEFAULT_ROB_TEMPERATURE,
        verbose: bool = False,
    ):
        """
        Initialize the RoB Assessor
        
        Args:
            model: OpenAI model to use for assessment
            temperature: Sampling temperature (0.0 for deterministic)
            verbose: Whether to print detailed progress
        """
        if not ROB_AVAILABLE:
            raise ImportError(
                "Risk of Bias package not available. "
                "Please ensure /home/ec2-user/rola_sysrev/risk-of-bias is properly installed."
            )
        
        self.model = model
        self.temperature = temperature
        self.verbose = verbose
        
        logger.info(f"RoBAssessor initialized: model={model}, temp={temperature}")
    
    def assess(
        self,
        manuscript_path: Path,
        guidance_document: Optional[Path] = None,
    ) -> Dict[str, Any]:
        """
        Perform RoB 2.0 assessment on a manuscript
        
        Args:
            manuscript_path: Path to the PDF manuscript
            guidance_document: Optional path to RoB guidance document
            
        Returns:
            Dictionary containing domain-level assessments and overall judgment
        """
        if not manuscript_path.exists():
            raise FileNotFoundError(f"Manuscript not found: {manuscript_path}")
        
        logger.info(f"Starting RoB assessment for: {manuscript_path.name}")
        
        # Get fresh RoB 2.0 framework
        framework = get_rob2_framework()
        
        # Run assessment
        completed_framework = run_framework(
            manuscript=manuscript_path,
            framework=framework,
            model=self.model,
            guidance_document=guidance_document,
            verbose=self.verbose,
            temperature=self.temperature,
        )
        
        # Extract results
        results = self._extract_results(completed_framework)
        results["manuscript"] = manuscript_path.name
        results["model"] = self.model
        
        logger.info(f"RoB assessment complete. Overall: {results.get('overall', 'Unknown')}")
        
        return results
    
    def _extract_results(self, framework: "Framework") -> Dict[str, Any]:
        """Extract assessment results from completed framework"""
        results = {
            "domains": {},
            "questions": {},
        }
        
        for domain in framework.domains:
            domain_key = ROB2_DOMAINS.get(domain.index, f"domain_{domain.index}")
            
            # Get domain judgment
            if hasattr(domain, 'judgement_function') and domain.judgement_function:
                judgment = domain.judgement_function(domain)
            else:
                judgment = None
            
            results["domains"][domain_key] = {
                "name": domain.name,
                "judgment": judgment,
                "questions": [],
            }
            
            # Extract question-level responses
            for question in domain.questions:
                if question.response:
                    q_result = {
                        "index": question.index,
                        "question": question.question,
                        "response": str(question.response.response),
                        "reasoning": question.response.reasoning,
                        "evidence": question.response.evidence,
                    }
                    results["domains"][domain_key]["questions"].append(q_result)
                    
                    # Also store in flat questions dict
                    q_key = f"q{int(question.index * 10)}"
                    results["questions"][q_key] = q_result
        
        # Extract overall judgment
        if "overall" in results["domains"]:
            results["overall"] = results["domains"]["overall"].get("judgment")
        
        return results
    
    def get_summary(self, results: Dict[str, Any]) -> Dict[str, str]:
        """
        Get a summary of domain-level judgments
        
        Args:
            results: Full assessment results from assess()
            
        Returns:
            Dictionary mapping domain names to judgments
        """
        summary = {}
        
        for domain_key, domain_data in results.get("domains", {}).items():
            judgment = domain_data.get("judgment")
            if judgment:
                summary[f"rob_{domain_key}"] = judgment
        
        return summary


# ============================================================================
# Standalone Assessment Function
# ============================================================================

def assess_rob(
    manuscript_path: Path,
    model: str = DEFAULT_ROB_MODEL,
    temperature: float = DEFAULT_ROB_TEMPERATURE,
    verbose: bool = False,
    guidance_document: Optional[Path] = None,
) -> Dict[str, Any]:
    """
    Convenience function for one-off RoB assessment
    
    Args:
        manuscript_path: Path to PDF manuscript
        model: OpenAI model to use
        temperature: Sampling temperature
        verbose: Print detailed progress
        guidance_document: Optional RoB guidance PDF
        
    Returns:
        Assessment results dictionary
    """
    assessor = RoBAssessor(
        model=model,
        temperature=temperature,
        verbose=verbose,
    )
    return assessor.assess(manuscript_path, guidance_document)


# ============================================================================
# Model Information
# ============================================================================

def get_rob_model_info() -> Dict[str, Any]:
    """Return information about the RoB assessment configuration"""
    return {
        "framework": {
            "name": "RoB 2.0 (Risk of Bias 2)",
            "reference": "Sterne et al. BMJ 2019;366:l4898",
            "domains": list(ROB2_DOMAIN_DESCRIPTIONS.items()),
        },
        "llm": {
            "provider": "OpenAI",
            "default_model": DEFAULT_ROB_MODEL,
            "temperature": DEFAULT_ROB_TEMPERATURE,
        },
        "package": {
            "source": "https://github.com/rob-luke/risk-of-bias",
            "local_path": str(RISK_OF_BIAS_PATH),
        },
    }
