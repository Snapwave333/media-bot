from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import os
from pathlib import Path

from app.config import get_settings
from app.database import init_db
from app.routers import auth, videos, payments

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    # Startup
    print("Starting AI Music Video SaaS...")

    # Create necessary directories
    for dir_path in [settings.upload_dir, settings.output_dir, settings.temp_dir]:
        Path(dir_path).mkdir(parents=True, exist_ok=True)

    # Initialize database
    await init_db()
    print("Database initialized")

    yield

    # Shutdown
    print("Shutting down...")


app = FastAPI(
    title=settings.app_name,
    description="""
    AI-Powered Music Video Generation Platform

    Transform your music into stunning visual experiences with AI:
    - Upload your MP3 and lyrics
    - AI analyzes beat, tempo, mood, and structure
    - Generates unique visuals tailored to your music
    - Automatically edits and syncs to the beat
    - Download your professional music video

    Perfect for independent musicians who want professional-quality videos without the $5,000 budget.
    """,
    version=settings.api_version,
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/v1")
app.include_router(videos.router, prefix="/api/v1")
app.include_router(payments.router, prefix="/api/v1")


# Exception handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "message": str(exc) if settings.debug else "An unexpected error occurred"
        }
    )


# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.api_version
    }


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": settings.app_name,
        "version": settings.api_version,
        "description": "AI-Powered Music Video Generation Platform",
        "docs": "/docs",
        "pricing": {
            "single_video": "$50",
            "subscription": "Contact for pricing"
        },
        "features": [
            "Beat and tempo detection using librosa",
            "AI-powered mood analysis",
            "Automatic visual generation",
            "Beat-synced video editing",
            "Multiple style presets",
            "High-quality output (1080p/4K)"
        ]
    }


# Mount static files for outputs (in production, use CDN)
if os.path.exists(settings.output_dir):
    app.mount("/outputs", StaticFiles(directory=settings.output_dir), name="outputs")
