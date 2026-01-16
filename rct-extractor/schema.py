"""
RCT Extraction Schema

Defines the data extraction fields for systematic review of randomized controlled trials.
Each field includes type, extraction method, and description for LLM guidance.
"""

from enum import Enum
from typing import Any, Optional, List
from pydantic import BaseModel, Field


# ============================================================================
# Enumeration Types for Classification Fields
# ============================================================================

class FundingType(str, Enum):
    INDUSTRY = "Industry"
    PUBLIC = "Public"
    MIXED = "Mixed"
    UNIVERSITY = "University"
    UNCLEAR = "Unclear"


class StudyType(str, Enum):
    SINGLECENTER = "singlecenter"
    MULTICENTER = "multicenter"


class GeographicalLocation(str, Enum):
    ARAB = "Arab"
    REGIONAL = "regional"
    INTERNATIONAL = "international"


class PilotRCT(str, Enum):
    DONE = "done"
    NOT_DONE = "notdone"


class TherapeuticArea(str, Enum):
    CANCER = "Cancer"
    DIABETES = "Diabetes"
    ORTHOPEDIC = "Orthopedic"
    PHYSIOLOGY = "Physiology"
    PSYCHIATRY = "Psychiatry"
    CARDIOLOGY = "Cardiology"
    NEUROLOGY = "Neurology"
    UROLOGY = "Urology"
    OBGYN = "OBGYN"
    GASTROINTESTINAL = "Gastrointestinal"
    DERMATOLOGY = "Dermatology"
    OPHTHALMOLOGY = "Ophthalmology"
    AUTOIMMUNE = "Autoimmune"
    OTHER = "Other"


class TargetGroup(str, Enum):
    PEDIATRIC = "Pediatric"
    ADULT = "Adult"
    PREGNANT = "Pregnant"
    UNSPECIFIED = "Unspecified"


class RandomizationUnit(str, Enum):
    INDIVIDUAL = "individual"
    SITE = "site"
    CLUSTER = "cluster"
    OTHER = "Other"


class StratificationStatus(str, Enum):
    YES = "Yes"
    NO = "No"
    UNSPECIFIED = "Unspecified"


class BlockingStatus(str, Enum):
    BLOCKING = "Blocking"
    NO_BLOCKING = "NoBlocking"
    UNSPECIFIED = "Unspecified"


class ConcealmentStatus(str, Enum):
    CONCEALED = "Concealed"
    NOT_CONCEALED = "NotConcealed"
    UNSPECIFIED = "Unspecified"


class InterventionDomain(str, Enum):
    HEALTHCARE_INTERVENTION = "HealthcareIntervention"
    PUBLIC_HEALTH = "PublicHealth"
    HEALTH_SYSTEMS_POLICY = "HealthSystemsAndPolicy"
    NUTRITION_DIET = "NutritionAndDiet"
    LIFESTYLE_BEHAVIORAL = "LifestyleAndBehavioral"
    HEALTH_EDUCATION = "HealthEducationAndAwareness"
    TRADITIONAL_COMPLEMENTARY = "TraditionalAndComplementaryMedicine"
    OTHER = "Other"


class StatisticalOutcomeType(str, Enum):
    BINARY = "BinaryOrDichotomous"
    CONTINUOUS = "Continuous"
    CATEGORICAL = "Categorical"
    ORDINAL = "Ordinal"
    OTHER = "Other"


class OutcomeStructure(str, Enum):
    SINGLE = "SingleOutcome"
    COMPOSITE = "CompositeOutcome"


class ITTPPSignificance(str, Enum):
    YES = "Yes"
    NO = "No"
    NOT_APPLICABLE = "NotApplicable"


class PresentationMode(str, Enum):
    RELATIVE = "RelativeEffect"
    ABSOLUTE = "AbsoluteEffect"
    OTHER = "Other"


class MissingnessHandling(str, Enum):
    NOT_DISCUSSED = "MechanismNotDiscussed"
    COMPLETE_CASE = "completeCaseAnalysis"
    OTHER = "Other"


class RiskOfBiasLevel(str, Enum):
    LOW = "LowRiskOfBias"
    MODERATE = "ModerateRiskOfBias"
    HIGH = "HighRiskOfBias"
    NOT_MENTIONED = "NotMentionedRiskOfBias"


# ============================================================================
# Schema Definition with Field Descriptions
# ============================================================================

# This dictionary defines all extraction fields with their metadata
# The 'description' field is used as guidance for the LLM during extraction

EXTRACTION_SCHEMA = {
    # -------------------------------------------------------------------------
    # Publication Metadata
    # -------------------------------------------------------------------------
    "title": {
        "type": "string",
        "method": "extract",
        "description": "The exact title of the research paper as it appears in the publication"
    },
    "journalName": {
        "type": "string",
        "method": "extract",
        "description": "Name of the journal where the paper was published"
    },
    "yearOfPublication": {
        "type": "integer",
        "method": "extract",
        "description": "Year the paper was published"
    },
    "funding": {
        "type": "boolean",
        "method": "generate",
        "description": "Whether the study received funding (true/false)"
    },
    "fundingType": {
        "type": "enum",
        "method": "classify",
        "description": "Type of funding received",
        "enum": ["Industry", "Public", "Mixed", "University", "Unclear"],
        "enumDescriptions": {
            "Industry": "Pharmaceutical or medical device company funding",
            "Public": "Government or public research grants",
            "Mixed": "Combination of industry and public funding",
            "University": "University or academic institution internal funding",
            "Unclear": "Funding source not clearly stated or ambiguous"
        }
    },
    
    # -------------------------------------------------------------------------
    # Trial Registration
    # -------------------------------------------------------------------------
    "trialRegistration": {
        "type": "boolean",
        "method": "generate",
        "description": "Whether the trial was registered in a registry (true/false)"
    },
    "registrationPlatform": {
        "type": "string",
        "method": "extract",
        "description": "Platform where trial was registered (e.g., ClinicalTrials.gov, EU-CTR, ISRCTN, PACTR, ANZCTR)"
    },
    "registrationNumber": {
        "type": "string",
        "method": "extract",
        "description": "Trial registration number or identifier (e.g., NCT12345678)"
    },
    
    # -------------------------------------------------------------------------
    # Geographic Information
    # -------------------------------------------------------------------------
    "arabCountries": {
        "type": "string",
        "method": "extract",
        "description": "List of Arab countries involved in the study (comma-separated if multiple)"
    },
    "typeOfStudy": {
        "type": "enum",
        "method": "classify",
        "description": "Single-center or multi-center study design",
        "enum": ["singlecenter", "multicenter"],
        "enumDescriptions": {
            "singlecenter": "The study was conducted in one site. If no mention of multiple sites, assume single center.",
            "multicenter": "More than one center or site participated in data collection"
        }
    },
    "geographicalLocation": {
        "type": "enum",
        "method": "classify",
        "description": "Geographical scope of the study",
        "enum": ["Arab", "regional", "international"],
        "enumDescriptions": {
            "Arab": "Study conducted only in Arab countries",
            "regional": "Arab countries and neighboring regions",
            "international": "International multi-country study"
        }
    },
    "correspondingAuthorCountry": {
        "type": "string",
        "method": "extract",
        "description": "Country of the corresponding author's affiliation"
    },
    
    # -------------------------------------------------------------------------
    # Author Information
    # -------------------------------------------------------------------------
    "totalAuthors": {
        "type": "integer",
        "method": "generate",
        "description": "Total number of authors listed on the paper"
    },
    "recruitingSites": {
        "type": "integer",
        "method": "extract",
        "description": "Number of recruiting sites involved in the study"
    },
    
    # -------------------------------------------------------------------------
    # Study Design
    # -------------------------------------------------------------------------
    "pilotRCT": {
        "type": "enum",
        "method": "classify",
        "description": "Whether a pilot RCT was conducted prior to this study",
        "enum": ["done", "notdone"],
        "enumDescriptions": {
            "done": "A pilot study was performed before the present study",
            "notdone": "No pilot preceded the present study or not mentioned"
        }
    },
    "therapeuticArea": {
        "type": "enum",
        "method": "classify",
        "description": "Primary disease or therapeutic area addressed in the study",
        "enum": ["Cancer", "Diabetes", "Orthopedic", "Physiology", "Psychiatry", 
                 "Cardiology", "Neurology", "Urology", "OBGYN", "Gastrointestinal",
                 "Dermatology", "Ophthalmology", "Autoimmune", "Other"]
    },
    "targetGroup": {
        "type": "enum",
        "method": "classify",
        "description": "Target patient population",
        "enum": ["Pediatric", "Adult", "Pregnant", "Unspecified"]
    },
    
    # -------------------------------------------------------------------------
    # Participant Information
    # -------------------------------------------------------------------------
    "totalParticipants": {
        "type": "integer",
        "method": "extract",
        "description": "Total number of participants enrolled in the study"
    },
    "methodSampleSource": {
        "type": "string",
        "method": "extract",
        "description": "Sample source or participant recruitment method (e.g., hospital, outpatient clinic)"
    },
    
    # -------------------------------------------------------------------------
    # Randomization Methods
    # -------------------------------------------------------------------------
    "methodRandomization": {
        "type": "boolean",
        "method": "extract",
        "description": "Whether randomization was performed (true/false)"
    },
    "methodRandomizationRatio": {
        "type": "string",
        "method": "extract",
        "description": "Ratio of randomization (e.g., 1:1, 2:1, 1:1:1)"
    },
    "methodRandomizationUnit": {
        "type": "enum",
        "method": "classify",
        "description": "Unit of randomization",
        "enum": ["individual", "site", "cluster", "Other"],
        "enumDescriptions": {
            "individual": "Randomization at patient/participant level",
            "site": "Randomization at study site level",
            "cluster": "Cluster randomization",
            "Other": "Other randomization unit"
        }
    },
    "methodStratification": {
        "type": "enum",
        "method": "classify",
        "description": "Whether stratified randomization was used",
        "enum": ["Yes", "No", "Unspecified"]
    },
    "methodBlocking": {
        "type": "enum",
        "method": "classify",
        "description": "Whether block randomization was used",
        "enum": ["Blocking", "NoBlocking", "Unspecified"]
    },
    "methodConcealment": {
        "type": "enum",
        "method": "classify",
        "description": "Whether allocation concealment was used",
        "enum": ["Concealed", "NotConcealed", "Unspecified"]
    },
    "methodBlinding": {
        "type": "string",
        "method": "extract",
        "description": "Blinding method used (e.g., double-blind, single-blind, open-label)"
    },
    
    # -------------------------------------------------------------------------
    # Intervention Details
    # -------------------------------------------------------------------------
    "methodDomain": {
        "type": "enum",
        "method": "classify",
        "description": "Intervention domain category",
        "enum": ["HealthcareIntervention", "PublicHealth", "HealthSystemsAndPolicy",
                 "NutritionAndDiet", "LifestyleAndBehavioral", "HealthEducationAndAwareness",
                 "TraditionalAndComplementaryMedicine", "Other"]
    },
    "typeOfIntervention": {
        "type": "string",
        "method": "extract",
        "description": "Type of intervention: Pharmacological, Non-pharmacological, or both"
    },
    "interventionName": {
        "type": "string",
        "method": "extract",
        "description": "Name of the primary intervention or treatment"
    },
    "pharmacologicalInterventions": {
        "type": "string",
        "method": "extract",
        "description": "Specific drugs or medications used (if pharmacological)"
    },
    "nonPharmacologicalInterventions": {
        "type": "string",
        "method": "extract",
        "description": "Specific non-pharmacological interventions used"
    },
    
    # -------------------------------------------------------------------------
    # Comparator Details
    # -------------------------------------------------------------------------
    "typeOfComparator": {
        "type": "string",
        "method": "extract",
        "description": "Type of comparator: Placebo, Standard of care, Active comparator, or Other"
    },
    "placebo": {
        "type": "boolean",
        "method": "extract",
        "description": "Whether placebo was used as comparator"
    },
    "standardOfCare": {
        "type": "boolean",
        "method": "extract",
        "description": "Whether standard of care was used as comparator"
    },
    "activeComparator": {
        "type": "string",
        "method": "extract",
        "description": "Active comparator used (if applicable)"
    },
    
    # -------------------------------------------------------------------------
    # Outcome Measures
    # -------------------------------------------------------------------------
    "primaryOutcome": {
        "type": "string",
        "method": "extract",
        "description": "Primary outcome measure of the study"
    },
    "statisticalTypeOfPrimaryOutcome": {
        "type": "enum",
        "method": "classify",
        "description": "Statistical type of primary outcome",
        "enum": ["BinaryOrDichotomous", "Continuous", "Categorical", "Ordinal", "Other"]
    },
    "outcomeType": {
        "type": "enum",
        "method": "classify",
        "description": "Outcome structure type",
        "enum": ["SingleOutcome", "CompositeOutcome"]
    },
    
    # -------------------------------------------------------------------------
    # Statistical Analysis
    # -------------------------------------------------------------------------
    "powerCalculation": {
        "type": "boolean",
        "method": "extract",
        "description": "Whether power calculation was performed"
    },
    "assumptions": {
        "type": "boolean",
        "method": "extract",
        "description": "Whether assumptions for power calculation were stated a priori"
    },
    "justification": {
        "type": "boolean",
        "method": "extract",
        "description": "Whether justification for sample size was provided"
    },
    "statisticalPower": {
        "type": "string",
        "method": "extract",
        "description": "Statistical power indicated (e.g., 80%, 90%)"
    },
    "interimAnalyses": {
        "type": "boolean",
        "method": "extract",
        "description": "Whether interim analyses were performed"
    },
    "adaptiveSampleSize": {
        "type": "boolean",
        "method": "extract",
        "description": "Whether adaptive sample size design was used"
    },
    
    # -------------------------------------------------------------------------
    # Analysis Methods
    # -------------------------------------------------------------------------
    "ittPrimaryMethod": {
        "type": "boolean",
        "method": "extract",
        "description": "Whether intention-to-treat (ITT) analysis was the primary method"
    },
    "ppPrimaryMethod": {
        "type": "boolean",
        "method": "extract",
        "description": "Whether per-protocol (PP) analysis was the primary method"
    },
    "bothIttPpSignificant": {
        "type": "enum",
        "method": "classify",
        "description": "Whether both ITT and PP analyses were statistically significant",
        "enum": ["Yes", "No", "NotApplicable"]
    },
    
    # -------------------------------------------------------------------------
    # Results Presentation
    # -------------------------------------------------------------------------
    "primaryModeOfPresentation": {
        "type": "enum",
        "method": "classify",
        "description": "Primary mode of presenting results",
        "enum": ["RelativeEffect", "AbsoluteEffect", "Other"]
    },
    "primaryOutcomeMetric": {
        "type": "string",
        "method": "extract",
        "description": "Metric used: Relative risk, Odds ratio, Hazard ratio, Risk difference, Mean difference, or Other"
    },
    "adjustedEstimate": {
        "type": "boolean",
        "method": "generate",
        "description": "Whether primary outcome was an adjusted estimate of effect"
    },
    "reportedPValue": {
        "type": "boolean",
        "method": "generate",
        "description": "Whether p-value was reported for primary outcome"
    },
    
    # -------------------------------------------------------------------------
    # Patient Flow
    # -------------------------------------------------------------------------
    "totalRandomized": {
        "type": "integer",
        "method": "extract",
        "description": "Total number of patients who were randomized"
    },
    "totalCompletedFollowup": {
        "type": "integer",
        "method": "extract",
        "description": "Number of patients who completed follow-up"
    },
    "lossFollowUp": {
        "type": "number",
        "method": "generate",
        "description": "Loss to follow-up percentage (calculated or extracted)"
    },
    "handlingMissingness": {
        "type": "enum",
        "method": "classify",
        "description": "Method for handling missing data",
        "enum": ["MechanismNotDiscussed", "completeCaseAnalysis", "Other"]
    },
    
    # -------------------------------------------------------------------------
    # Early Stopping
    # -------------------------------------------------------------------------
    "earlyStoppingEfficacy": {
        "type": "boolean",
        "method": "generate",
        "description": "Whether there was early stopping for efficacy"
    },
    "earlyStoppingFutility": {
        "type": "boolean",
        "method": "generate",
        "description": "Whether there was early stopping for futility"
    },
    
    # -------------------------------------------------------------------------
    # Control Group Metrics
    # -------------------------------------------------------------------------
    "controlGroupEventRate": {
        "type": "string",
        "method": "extract",
        "description": "Event rate in the control group (as percentage or fraction)"
    },
}


# ============================================================================
# Pydantic Models for Extraction Output
# ============================================================================

class DemographicsGroup(BaseModel):
    """Demographics for a single treatment arm/group"""
    group_name: str = Field(description="Name of the treatment group")
    mean_age: Optional[float] = Field(None, description="Mean age of participants")
    sd_age: Optional[float] = Field(None, description="Standard deviation of age")
    median_age: Optional[float] = Field(None, description="Median age if reported")
    iqr_age: Optional[str] = Field(None, description="Interquartile range for age")
    female_proportion: Optional[float] = Field(None, description="Proportion of female participants (0-1)")
    n_participants: Optional[int] = Field(None, description="Number of participants in this group")


class RCTExtraction(BaseModel):
    """Complete RCT extraction result"""
    # Metadata
    filename: str
    extracted_at: str
    
    # Publication info
    title: Optional[str] = None
    journal_name: Optional[str] = None
    year_of_publication: Optional[int] = None
    
    # Funding
    funding: Optional[bool] = None
    funding_type: Optional[str] = None
    funder: Optional[str] = None
    
    # Registration
    trial_registration: Optional[bool] = None
    registration_platform: Optional[str] = None
    registration_number: Optional[str] = None
    
    # Geographic
    arab_countries: Optional[str] = None
    type_of_study: Optional[str] = None
    geographical_location: Optional[str] = None
    corresponding_author_country: Optional[str] = None
    
    # Authors & Sites
    total_authors: Optional[int] = None
    recruiting_sites: Optional[int] = None
    
    # Study Design
    pilot_rct: Optional[str] = None
    therapeutic_area: Optional[str] = None
    target_group: Optional[str] = None
    
    # Participants
    total_participants: Optional[int] = None
    sample_source: Optional[str] = None
    
    # Randomization
    randomization: Optional[bool] = None
    randomization_ratio: Optional[str] = None
    randomization_unit: Optional[str] = None
    stratification: Optional[str] = None
    blocking: Optional[str] = None
    concealment: Optional[str] = None
    blinding: Optional[str] = None
    
    # Intervention
    domain: Optional[str] = None
    type_of_intervention: Optional[str] = None
    intervention_name: Optional[str] = None
    pharmacological_interventions: Optional[str] = None
    non_pharmacological_interventions: Optional[str] = None
    
    # Comparator
    type_of_comparator: Optional[str] = None
    placebo: Optional[bool] = None
    standard_of_care: Optional[bool] = None
    active_comparator: Optional[str] = None
    
    # Outcomes
    primary_outcome: Optional[str] = None
    statistical_type_primary_outcome: Optional[str] = None
    outcome_type: Optional[str] = None
    
    # Statistics
    power_calculation: Optional[bool] = None
    statistical_power: Optional[str] = None
    assumptions: Optional[bool] = None
    justification: Optional[bool] = None
    interim_analyses: Optional[bool] = None
    adaptive_sample_size: Optional[bool] = None
    
    # Analysis
    itt_primary: Optional[bool] = None
    pp_primary: Optional[bool] = None
    both_itt_pp_significant: Optional[str] = None
    
    # Presentation
    primary_mode_presentation: Optional[str] = None
    primary_outcome_metric: Optional[str] = None
    adjusted_estimate: Optional[bool] = None
    reported_pvalue: Optional[bool] = None
    
    # Patient Flow
    total_randomized: Optional[int] = None
    total_completed_followup: Optional[int] = None
    loss_followup: Optional[float] = None
    handling_missingness: Optional[str] = None
    
    # Early Stopping
    early_stopping_efficacy: Optional[bool] = None
    early_stopping_futility: Optional[bool] = None
    
    # Control
    control_group_event_rate: Optional[str] = None
    
    # Demographics by group
    demographics: Optional[List[DemographicsGroup]] = None
    
    # Risk of Bias (from ROB2)
    rob_randomization: Optional[str] = None
    rob_deviations: Optional[str] = None
    rob_missing_data: Optional[str] = None
    rob_measurement: Optional[str] = None
    rob_selection: Optional[str] = None
    rob_overall: Optional[str] = None


def get_extraction_prompt() -> str:
    """Generate a structured extraction prompt from the schema"""
    prompt_parts = [
        "Extract the following information from this RCT manuscript.",
        "For each field, provide the value as specified. Use 'null' or 'Not found' if information is not available.",
        "",
        "FIELDS TO EXTRACT:",
        ""
    ]
    
    for field_name, field_info in EXTRACTION_SCHEMA.items():
        field_type = field_info['type']
        method = field_info['method']
        description = field_info['description']
        
        prompt_parts.append(f"**{field_name}** ({field_type}, {method}):")
        prompt_parts.append(f"  {description}")
        
        if 'enum' in field_info:
            prompt_parts.append(f"  Options: {', '.join(field_info['enum'])}")
        
        prompt_parts.append("")
    
    return "\n".join(prompt_parts)
