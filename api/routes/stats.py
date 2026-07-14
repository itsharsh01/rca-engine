from fastapi import APIRouter

router = APIRouter(prefix="/stats", tags=["stats"])

@router.get("/drift")
async def get_drift():
    return {
        "drift_detected": False,
        "mmd_distance": 0.012,
        "p_value": 0.43
    }

@router.get("/changepoints")
async def get_changepoints():
    return {
        "changepoints_indices": [],
        "signals": []
    }
