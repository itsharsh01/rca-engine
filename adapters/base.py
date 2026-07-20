import uuid
import datetime
from abc import ABC, abstractmethod
from pydantic import BaseModel
from typing import List, Dict, Any

class RawSpan(BaseModel):
    span_id: str
    trace_id: str
    parent_span_id: str | None = None
    name: str
    start_time: str
    end_time: str
    attributes: Dict[str, Any] = {}

class RawTrace(BaseModel):
    trace_id: str
    spans: List[RawSpan]

class SourceAdapter(ABC):
    @abstractmethod
    async def fetch_traces(
        self, 
        lookback_hours: int | None = None, 
        start_time: str | None = None, 
        end_time: str | None = None
    ) -> List[RawTrace]:
        """
        Fetch traces from the target platform API.
        """
        pass

def generate_sample_traces(platform_name: str, start_time: str | None = None, end_time: str | None = None, count: int = 3) -> List[RawTrace]:
    """
    Generate realistic RawTrace objects for testing and demo ingestion pipelines.
    """
    now_str = datetime.datetime.now(datetime.timezone.utc).isoformat()
    s_time = start_time or now_str
    e_time = end_time or now_str

    traces = []
    for i in range(count):
        t_id = f"tr_{platform_name[:3]}_{uuid.uuid4().hex[:8]}"
        root_span_id = f"sp_root_{i+1}"
        llm_span_id = f"sp_llm_{i+1}"
        
        spans = [
            RawSpan(
                span_id=root_span_id,
                trace_id=t_id,
                parent_span_id=None,
                name=f"{platform_name}_pipeline_execution",
                start_time=s_time,
                end_time=e_time,
                attributes={
                    "platform": platform_name,
                    "environment": "production",
                    "user_email": f"customer_{i+1}@company.com",
                    "user_query": f"Sample query request #{i+1} for {platform_name}"
                }
            ),
            RawSpan(
                span_id=llm_span_id,
                trace_id=t_id,
                parent_span_id=root_span_id,
                name="llm_completion",
                start_time=s_time,
                end_time=e_time,
                attributes={
                    "model": "gpt-4o",
                    "prompt_tokens": 120 + (i * 15),
                    "completion_tokens": 45 + (i * 8),
                    "latency_ms": 230 + (i * 40),
                    "status": "success"
                }
            )
        ]
        traces.append(RawTrace(trace_id=t_id, spans=spans))
    return traces
