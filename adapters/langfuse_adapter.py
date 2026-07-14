from adapters.base import SourceAdapter, RawTrace
from typing import List

class LangfuseAdapter(SourceAdapter):
    async def fetch_traces(self, lookback_hours: int) -> List[RawTrace]:
        # Langfuse REST API paginated ingestion implementation stub
        return []
