from fastapi import APIRouter

router = APIRouter(prefix="/ingest", tags=["ingest"])

@router.post("/run")
async def run_ingest():
    return {"status": "success", "detail": "Ingestion pipeline triggered"}
