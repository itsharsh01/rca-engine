from fastapi import APIRouter

from app.controllers.health_controller import HealthController
from app.schemas.health import HealthResponse

router = APIRouter()
controller = HealthController()


@router.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    return controller.get_health()
