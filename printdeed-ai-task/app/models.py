from pydantic import BaseModel
from typing import Optional, Dict, List, Any

class FieldData(BaseModel):
    value: Optional[str]
    confidence: float

class ProcessingInstructions(BaseModel):
    workflow: str
    confidence_threshold: float
    hitl_on_failure: bool

class Decision(BaseModel):
    route: Optional[str] = None

class MatchResult(BaseModel):
    matched_code: Optional[str]
    match_confidence: float
    rationale: str
    fallback_used: bool
    source: str

class Envelope(BaseModel):
    envelope_id: str
    extraction: Dict[str, FieldData]
    processing_instructions: ProcessingInstructions
    validation_results: Optional[Dict[str, Any]] = None
    matching_results: Optional[MatchResult] = None
    decision: Decision = Decision()
    audit: List[Dict[str, Any]] = []