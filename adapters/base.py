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
    async def fetch_traces(self, lookback_hours: int) -> List[RawTrace]:
        """
        Fetch traces from the target platform API.
        """
        pass
