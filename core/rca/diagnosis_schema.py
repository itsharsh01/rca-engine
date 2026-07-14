from pydantic import BaseModel
from typing import List, Dict, Any
from core.taxonomy import FaultClass

class RCADiagnosis(BaseModel):
    trace_id: str
    primary_fault: FaultClass
    confidence: float
    reasoning: str
    impacted_spans: List[str]
    remediation_steps: List[str]
