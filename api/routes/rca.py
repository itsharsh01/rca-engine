from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from core.analytics.rca_engine import RCAEngine
from core.agent.diagnostic_agent import LLMDiagnosticAgent

router = APIRouter(prefix="/rca", tags=["rca"])
rca_engine = RCAEngine()
diagnostic_agent = LLMDiagnosticAgent()

class RCAAnaLyzeRequest(BaseModel):
    target_diagnosis_id: str
    baseline_diagnosis_id: str | None = None

@router.post("/analyze")
async def analyze_diagnosis(body: RCAAnaLyzeRequest):
    try:
        metrics = await rca_engine.analyze_diagnosis(
            target_diagnosis_id=body.target_diagnosis_id,
            baseline_diagnosis_id=body.baseline_diagnosis_id
        )
        diagnosis = await diagnostic_agent.diagnose(metrics)
        
        return {
            "status": "success",
            "metrics": metrics,
            "diagnosis": diagnosis
        }
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to perform RCA analysis: {str(e)}"
        )
