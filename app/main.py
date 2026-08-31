"""FastAPI Main Application Entry Point."""
import os
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.core.config import settings
from app.core.logging import setup_logging, get_logger
from app.api.routes import health_router, chat_router
from app.database.session import Base, engine

# Initialize structured logging
setup_logging("DEBUG" if settings.DEBUG else "INFO")
logger = get_logger("app.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context for startup and shutdown procedures."""
    logger.info(
        f"Starting {settings.APP_NAME} (Environment: {settings.APP_ENV}, Framework: {settings.AGENT_FRAMEWORK})",
        extra={"event": "agent_started"}
    )
    # Ensure database tables exist
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database schemas verified.")
    except Exception as e:
        logger.warning(f"Could not connect to database on startup: {e}")

    yield

    logger.info("Shutting down Retail Customer Support Assistant...")


def create_app() -> FastAPI:
    """Creates and configures the FastAPI application."""
    app = FastAPI(
        title=settings.APP_NAME,
        description="Multi-Agent Customer Support Assistant for Retail with LangGraph, LangChain, Google ADK, and MCP.",
        version="0.1.0",
        lifespan=lifespan
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register API Routers
    app.include_router(health_router)
    app.include_router(chat_router)

    # Mount React + Vite Frontend
    dist_dir = Path(__file__).parent.parent / "frontend" / "dist"
    if dist_dir.exists():
        if (dist_dir / "assets").exists():
            app.mount("/assets", StaticFiles(directory=str(dist_dir / "assets")), name="assets")

        @app.get("/")
        async def serve_react_root():
            return FileResponse(str(dist_dir / "index.html"))

    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
