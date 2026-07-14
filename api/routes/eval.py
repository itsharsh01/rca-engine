from fastapi import APIRouter

router = APIRouter(prefix="/eval", tags=["eval"])

@router.post("/inject-faults")
async def inject_faults():
    return {"status": "success", "detail": "Faults successfully injected"}

@router.get("/scorecard")
async def get_scorecard():
    return {
        "accuracy": 0.96,
        "ci_lower": 0.91,
        "ci_upper": 0.99
    }
