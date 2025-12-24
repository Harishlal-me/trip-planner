"""
Trip Planner ML API Server
Main entry point for the FastAPI application
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from pathlib import Path
import sys

# Import API routers
from api.routes import weather, budget, trip, places, health

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global model instances
ranking_model = None
budget_model = None

# Create FastAPI app
app = FastAPI(
    title="Trip Planner ML API",
    description="AI-powered trip planning with budget prediction and place recommendations",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, tags=["Health"])
app.include_router(weather.router, prefix="/api/weather", tags=["Weather"])
app.include_router(budget.router, prefix="/api/budget", tags=["Budget"])
app.include_router(trip.router, prefix="/api/trip", tags=["Trip Planning"])
app.include_router(places.router, prefix="/api/places", tags=["Places"])

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "🎯 Trip Planner ML API",
        "docs": "http://localhost:8000/docs",
        "version": "1.0.0"
    }

# Startup event
@app.on_event("startup")
async def startup_event():
    global ranking_model, budget_model
    
    logger.info("="*60)
    logger.info("🚀 TRIP PLANNER ML API")
    logger.info("="*60)
    logger.info("✅ FREE APIs: OpenWeather, OSRM, Nominatim, REST Countries")
    logger.info("🤖 ML Models: Loading...")
    
    try:
        from models.recommender.ml_ranking_model import MLRankingModel
        from models.budget_prediction.ml_budget_model import MLBudgetModel
        from pathlib import Path
        
        # Check if model files exist
        trained_models_dir = Path("trained_models")
        
        ranking_files_exist = all([
            (trained_models_dir / "ranking_model.joblib").exists(),
            (trained_models_dir / "ranking_model_scaler.joblib").exists(),
            (trained_models_dir / "ranking_model_features.joblib").exists()
        ])
        
        budget_files_exist = all([
            (trained_models_dir / "budget_model.joblib").exists(),
            (trained_models_dir / "budget_model_scaler.joblib").exists(),
            (trained_models_dir / "budget_model_features.joblib").exists()
        ])
        
        if not ranking_files_exist:
            logger.warning("⚠️  Ranking model files not found")
        else:
            try:
                ranking_model = MLRankingModel()
                ranking_model.load('ranking_model')
                logger.info("✓ Ranking model loaded successfully")
            except Exception as e:
                logger.error(f"✗ Error loading ranking model: {e}")
                logger.info("💡 Try retraining: python -m models.training.trainer")
                ranking_model = None
        
        if not budget_files_exist:
            logger.warning("⚠️  Budget model files not found")
        else:
            try:
                budget_model = MLBudgetModel()
                budget_model.load('budget_model')
                logger.info("✓ Budget model loaded successfully")
            except Exception as e:
                logger.error(f"✗ Error loading budget model: {e}")
                logger.info("💡 Try retraining: python -m models.training.trainer")
                budget_model = None
        
        if ranking_model and budget_model:
            logger.info("🤖 ML Models: Loaded ✓")
        else:
            logger.warning("⚠️  Some models failed to load. API will use fallback predictions.")
    
    except Exception as e:
        logger.error(f"Startup error: {e}")
        logger.warning("⚠️  API starting without ML models (fallback mode)")
    
    logger.info("📍 Server starting at: http://localhost:8000")
    logger.info("📖 API Docs: http://localhost:8000/docs")
    logger.info("="*60)

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("🛑 Server shutting down")

# Error handlers
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Error: {exc}")
    import traceback
    traceback.print_exc()
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": str(exc)}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )