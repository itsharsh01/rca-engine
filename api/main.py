from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import api_router

def create_app() -> FastAPI:
    app = FastAPI(
        title="Mercury AI Observability Engine",
        description="FastAPI service for LLM trace analytics, drift detection, and root-cause analysis.",
        version="0.1.0",
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
