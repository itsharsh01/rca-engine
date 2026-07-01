from app.schemas.health import HealthResponse
from app.services.health_service import HealthService


class HealthController:
    def __init__(self, health_service: HealthService | None = None) -> None:
        self._health_service = health_service or HealthService()

    def get_health(self) -> HealthResponse:
        return self._health_service.get_health()
