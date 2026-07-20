import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import api_router
from core.worker.pubsub import PubSubManager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Start the background Pub/Sub subscription worker
    pubsub_manager = PubSubManager()
    loop = asyncio.get_running_loop()
    subscriber_future = pubsub_manager.start_subscriber(loop)
    
    yield
    
    # Shutdown: Clean up background subscriber task
    if subscriber_future:
        try:
            subscriber_future.cancel()
        except Exception:
            pass

def create_app() -> FastAPI:
    app = FastAPI(
        title="Mercury AI Observability Engine",
        description="FastAPI service for LLM trace analytics, drift detection, and root-cause analysis.",
        version="0.1.0",
        lifespan=lifespan,
    )
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    app.include_router(api_router, prefix="/api/v1")
    
    @app.get("/health")
    def health_check():
        return {"status": "healthy", "service": "mercury-ai-rca-engine"}
        
    return app

app = create_app()
