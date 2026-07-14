from core.taxonomy import FaultClass
from sqlalchemy.ext.asyncio import AsyncSession

async def label_trace_ground_truth(trace_id: str, fault: FaultClass, session: AsyncSession) -> None:
    """
    Write ground-truth FaultClass labels to DB for validation runs.
    """
    pass
