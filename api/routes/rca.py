from fastapi import APIRouter
from typing import List
from pydantic import BaseModel

router = APIRouter(prefix="/rca", tags=["rca"])

class DiagnoseRequest(BaseModel):
    trace_id: str

class DiagnoseClusterRequest(BaseModel):
    trace_ids: List[str]

@router.post("/diagnose")
async def diagnose_trace(body: DiagnoseRequest):
    return {
        "trace_id": body.trace_id,
        "primary_fault": "latency_spike",
        "confidence": 0.95,
        "reasoning": "Mock reasoning",
    }

@router.post("/diagnose-cluster")
async def diagnose_cluster(body: DiagnoseClusterRequest):
    return {"cluster_size": len(body.trace_ids), "diagnoses": []}
