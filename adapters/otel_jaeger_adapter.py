from adapters.base import SourceAdapter, RawTrace
from typing import List

class OtelJaegerAdapter(SourceAdapter):
    async def fetch_traces(self, lookback_hours: int) -> List[RawTrace]:
        # Jaeger HTTP API ingestion implementation stub
        return []
