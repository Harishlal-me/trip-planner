"""
Health check endpoint - api/routes/health.py
"""

from fastapi import APIRouter
from datetime import datetime
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/health")
async def health_check():
    """Check API health status"""
    return {
        "status": "✅ Healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "Trip Planner ML API",
        "version": "1.0.0"
    }

@router.get("/health/models")
async def models_health():
    """Check if ML models are loaded"""
    try:
        from models.recommender.ml_ranking_model import MLRankingModel
        from models.budget_prediction.ml_budget_model import MLBudgetModel
        from pathlib import Path
        
        models_dir = Path("trained_models")
        
        # Check ranking model files
        ranking_files = [
            models_dir / "ranking_model.joblib",
            models_dir / "ranking_model_scaler.joblib",
            models_dir / "ranking_model_features.joblib"
        ]
        
        ranking_ok = all(f.exists() for f in ranking_files)
        
        # Check budget model files
        budget_files = [
            models_dir / "budget_model.joblib",
            models_dir / "budget_model_scaler.joblib",
            models_dir / "budget_model_features.joblib"
        ]
        
        budget_ok = all(f.exists() for f in budget_files)
        
        if ranking_ok and budget_ok:
            try:
                ranking_model = MLRankingModel()
                ranking_model.load('ranking_model')
                
                budget_model = MLBudgetModel()
                budget_model.load('budget_model')
                
                return {
                    "status": "✅ All models loaded and ready",
                    "ranking_model": "✓ Ready",
                    "budget_model": "✓ Ready",
                    "timestamp": datetime.now().isoformat()
                }
            except Exception as e:
                return {
                    "status": "⚠️ Models found but failed to load",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }
        else:
            return {
                "status": "⚠️ Model files not found",
                "ranking_model": "✗ Missing" if not ranking_ok else "✓ Found",
                "budget_model": "✗ Missing" if not budget_ok else "✓ Found",
                "timestamp": datetime.now().isoformat()
            }
    except Exception as e:
        return {
            "status": "⚠️ Error checking models",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@router.get("/info")
async def api_info():
    """Get API information"""
    return {
        "name": "Trip Planner ML API",
        "version": "1.0.0",
        "description": "AI-powered trip planning with budget prediction and place recommendations",
        "endpoints": {
            "health": "/health",
            "weather": "/api/weather/current, /api/weather/forecast",
            "budget": "/api/budget/predict, /api/budget/estimate/{destination}",
            "places": "/api/places/nearby, /api/places/search, /api/places/recommend",
            "trip": "/api/trip/plan, /api/trip/estimate"
        },
        "documentation": "/docs"
    }