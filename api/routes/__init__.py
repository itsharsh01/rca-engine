from fastapi import APIRouter
from api.routes.onboarding import router as onboarding_router
from api.routes.ingest import router as ingest_router
from api.routes.rca import router as rca_router
from api.routes.eval import router as eval_router
from api.routes.replay import router as replay_router
from api.routes.stats import router as stats_router

api_router = APIRouter()
api_router.include_router(onboarding_router)
api_router.include_router(ingest_router)
api_router.include_router(rca_router)
api_router.include_router(eval_router)
api_router.include_router(replay_router)
api_router.include_router(stats_router)

__all__ = ["api_router"]
