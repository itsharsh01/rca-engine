from app.config import settings
from app.schemas.health import HealthResponse


class HealthService:
    def get_health(self) -> HealthResponse:
        return HealthResponse(
            status="ok",
            service="rca-engine",
            version=settings.app_version,
        )
