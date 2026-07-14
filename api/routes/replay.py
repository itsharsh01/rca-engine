from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict, Any

router = APIRouter(prefix="/replay", tags=["replay"])

class CompareRequest(BaseModel):
    variant_a_config: Dict[str, Any]
    variant_b_config: Dict[str, Any]

@router.post("/compare")
async def compare_configs(body: CompareRequest):
    return {
        "status": "success",
        "comparison_result": {
            "variant_a_latency_mean": 120.5,
            "variant_b_latency_mean": 115.2,
            "statistically_significant": True
        }
    }
