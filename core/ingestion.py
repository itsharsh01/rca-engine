from core.pii_redactor import PIIRedactor
from adapters.base import RawTrace

class IngestPipeline:
    def __init__(self):
        self.redactor = PIIRedactor()

    async def ingest(self, trace: RawTrace) -> None:
        """
        Pull trace, redact it, and upsert to database.
        """
        # Ingestion pipeline stub
        pass
