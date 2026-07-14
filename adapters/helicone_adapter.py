from adapters.base import SourceAdapter, RawTrace
from typing import List

class HeliconeAdapter(SourceAdapter):
    async def fetch_traces(self, lookback_hours: int) -> List[RawTrace]:
        # Helicone /v1/request/query ingestion implementation stub
        return []
