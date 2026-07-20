from adapters.base import SourceAdapter, RawTrace, generate_sample_traces
from typing import List

class LangfuseAdapter(SourceAdapter):
    async def fetch_traces(
        self, 
        lookback_hours: int | None = None, 
        start_time: str | None = None, 
        end_time: str | None = None
    ) -> List[RawTrace]:
        return generate_sample_traces("langfuse", start_time=start_time, end_time=end_time, count=3)
