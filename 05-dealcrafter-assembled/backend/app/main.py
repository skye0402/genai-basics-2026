"""Main FastAPI application entry point."""
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api import chat, chat_history, audio

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Set specific loggers to appropriate levels
logging.getLogger("app.services.llm_service").setLevel(getattr(logging, settings.log_level.upper(), logging.INFO))
logging.getLogger("uvicorn.access").setLevel(logging.WARNING)  # Reduce noise from access logs

logger = logging.getLogger(__name__)
logger.info(f"Starting Fiori AI Chat Backend (Log Level: {settings.log_level})")


# Create FastAPI app
app = FastAPI(
    title="Fiori AI Chat Backend",
    description="Backend API for AI-powered financial data analysis",
    version="0.1.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat.router, prefix="/api", tags=["chat"])
app.include_router(chat_history.router)
app.include_router(audio.router)


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "ok",
        "service": "Fiori AI Chat Backend",
        "version": "0.1.0",
        "mock_mode": settings.mock_mode
    }


@app.get("/health")
async def health():
    """Detailed health check."""
    return {
        "status": "healthy",
        "mock_mode": settings.mock_mode,
        "cors_origins": settings.cors_origins_list
    }
