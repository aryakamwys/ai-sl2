from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.logger import logger
from app.routes import ai, data, pollution

# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="AI-powered recommendation system using RAG and Google Sheets",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(ai.router, prefix="/api/ai", tags=["AI"])
app.include_router(data.router, prefix="/api/data", tags=["Data"])
app.include_router(pollution.router, prefix="/api/pollution", tags=["Pollution Analysis"])


@app.get("/")
async def root():
    """Health check endpoint"""
    logger.info("Health check endpoint called")
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.VERSION,
    }


@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "ok",
        "environment": settings.ENVIRONMENT,
        "services": {
            "gemini": bool(settings.GEMINI_API_KEY),
            "perplexity": bool(settings.PERPLEXITY_API_KEY),
            "google_sheets": bool(settings.GOOGLE_SHEETS_CREDENTIALS),
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )

