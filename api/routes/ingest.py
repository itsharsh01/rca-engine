import datetime
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from core.worker.pubsub import PubSubManager
from core.database import get_database

router = APIRouter(prefix="/ingest", tags=["ingest"])
pubsub_manager = PubSubManager()

class IngestRunRequest(BaseModel):
    app_id: str
    platform_name: str
    lookback_hours: int = 5
    diagnosis_id: str | None = None

@router.post("/run")
async def run_ingest(body: IngestRunRequest):
    try:
        now = datetime.datetime.now(datetime.timezone.utc)
        diag_id = body.diagnosis_id or f"diag_{int(now.timestamp())}"
        
        # Split target lookback_hours into 1-hour batches
        messages_sent = []
        for i in range(body.lookback_hours):
            start_time = now - datetime.timedelta(hours=i + 1)
            end_time = now - datetime.timedelta(hours=i)
            
            task_payload = {
                "app_id": body.app_id,
                "platform_name": body.platform_name.lower(),
                "diagnosis_id": diag_id,
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "batch_index": i + 1,
                "total_batches": body.lookback_hours
            }
            
            pubsub_manager.publish_task(task_payload)
            messages_sent.append(task_payload)
            
        return {
            "status": "success", 
            "detail": f"Split ingestion into {body.lookback_hours} batches of 1-hour ranges",
            "batches_triggered": len(messages_sent),
            "diagnosis_id": diag_id
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to publish ingest tasks to queue: {str(e)}"
        )

@router.get("/traces/{diagnosis_id}")
async def get_traces_by_diagnosis(diagnosis_id: str):
    try:
        db = get_database()
        cursor = db.traces.find({"diagnosis_id": diagnosis_id}, {"_id": 0})
        traces = await cursor.to_list(length=100)
        return {
            "status": "success",
            "diagnosis_id": diagnosis_id,
            "count": len(traces),
            "traces": traces
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch traces from MongoDB: {str(e)}"
        )

@router.get("/recent-diagnoses")
async def get_recent_diagnoses():
    try:
        db = get_database()
        pipeline = [
            {
                "$match": {
                    "diagnosis_id": {"$ne": None}
                }
            },
            {
                "$group": {
                    "_id": "$diagnosis_id",
                    "latest_ingested_at": {"$max": "$ingested_at"},
                    "trace_count": {"$sum": 1},
                    "total_spans": {"$sum": {"$size": "$spans"}}
                }
            },
            {
                "$sort": {"latest_ingested_at": -1}
            },
            {
                "$limit": 10
            }
        ]
        results = await db.traces.aggregate(pipeline).to_list(length=10)
        recent = []
        for r in results:
            if r["_id"]:
                recent.append({
                    "diagnosis_id": r["_id"],
                    "latest_ingested_at": r["latest_ingested_at"],
                    "trace_count": r["trace_count"],
                    "total_spans": r["total_spans"]
                })
        return {
            "status": "success",
            "recent_diagnoses": recent
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to aggregate recent diagnoses: {str(e)}"
        )
