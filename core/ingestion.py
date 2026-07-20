import datetime
from core.pii_redactor import PIIRedactor
from adapters.base import RawTrace
from core.database import get_database

class IngestPipeline:
    def __init__(self):
        self.redactor = PIIRedactor()

    async def ingest(self, trace: RawTrace, diagnosis_id: str | None = None) -> None:
        """
        Pull trace, redact PII, and upsert to MongoDB traces collection.
        """
        db = get_database()
        
        # Convert spans into dict format for MongoDB
        spans_data = []
        for span in trace.spans:
            span_dict = span.model_dump()
            # Redact PII in attributes if any
            if "attributes" in span_dict and span_dict["attributes"]:
                span_dict["attributes"] = self.redactor.redact_dict(span_dict["attributes"])
            spans_data.append(span_dict)

        trace_doc = {
            "trace_id": trace.trace_id,
            "diagnosis_id": diagnosis_id,
            "spans": spans_data,
            "ingested_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
        }

        await db.traces.update_one(
            {"trace_id": trace.trace_id},
            {"$set": trace_doc},
            upsert=True
        )
