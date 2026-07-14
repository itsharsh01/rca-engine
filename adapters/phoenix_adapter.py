from adapters.base import SourceAdapter, RawTrace
from typing import List

class PhoenixAdapter(SourceAdapter):
    async def fetch_traces(self, lookback_hours: int) -> List[RawTrace]:
        # Arize Phoenix /v1/spans ingestion implementation stub
        return []
