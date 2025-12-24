"""
Budget prediction endpoints - api/routes/budget.py
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

class BudgetRequest(BaseModel):
    destination: str
    num_days: int
    num_people: int
    accommodation_level: int
    travel_style: str = "moderate"

@router.post("/predict")
async def predict_budget(request: BudgetRequest):
    """Predict trip budget using ML model"""
    try:
        # Validate inputs
        if request.num_days < 1 or request.num_days > 365:
            raise HTTPException(status_code=400, detail="num_days must be between 1 and 365")
        if request.num_people < 1 or request.num_people > 50:
            raise HTTPException(status_code=400, detail="num_people must be between 1 and 50")
        if request.accommodation_level < 1 or request.accommodation_level > 5:
            raise HTTPException(status_code=400, detail="accommodation_level must be between 1 and 5")
        
        from models.budget_prediction.ml_budget_model import MLBudgetModel
        
        # Load model
        model = MLBudgetModel()
        model.load('budget_model')
        
        # Prepare features
        trip_features = {
            'num_days': request.num_days,
            'num_people': request.num_people,
            'accommodation_level': request.accommodation_level,
            'destination_cost_index': 1.0,  # Can be enriched with real data
            'season_multiplier': 1.0  # Can be enriched with season data
        }
        
        # Predict
        predicted_budget = model.predict_trip_budget(trip_features)
        
        # Ensure positive prediction
        if predicted_budget < 0:
            predicted_budget = abs(predicted_budget)
        
        per_person = predicted_budget / request.num_people
        per_day = predicted_budget / request.num_days
        
        return {
            "destination": request.destination,
            "num_days": request.num_days,
            "num_people": request.num_people,
            "accommodation_level": request.accommodation_level,
            "travel_style": request.travel_style,
            "predicted_budget": float(predicted_budget),
            "currency": "USD",
            "per_person": float(per_person),
            "per_day": float(per_day),
            "breakdown": {
                "accommodation": float(predicted_budget * 0.35),
                "food": float(predicted_budget * 0.30),
                "activities": float(predicted_budget * 0.20),
                "transport": float(predicted_budget * 0.15)
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Budget prediction error: {e}")
        raise HTTPException(status_code=500, detail=f"Error predicting budget: {str(e)}")

@router.get("/estimate/{destination}")
async def estimate_budget(
    destination: str,
    num_days: int = 7,
    num_people: int = 2,
    accommodation_level: int = 3
):
    """Quick budget estimate for a destination"""
    try:
        # Validate inputs
        if num_days < 1 or num_days > 365:
            raise HTTPException(status_code=400, detail="num_days must be between 1 and 365")
        if num_people < 1 or num_people > 50:
            raise HTTPException(status_code=400, detail="num_people must be between 1 and 50")
        if accommodation_level < 1 or accommodation_level > 5:
            raise HTTPException(status_code=400, detail="accommodation_level must be between 1 and 5")
        
        from models.budget_prediction.ml_budget_model import MLBudgetModel
        
        model = MLBudgetModel()
        model.load('budget_model')
        
        trip_features = {
            'num_days': num_days,
            'num_people': num_people,
            'accommodation_level': accommodation_level,
            'destination_cost_index': 1.0,
            'season_multiplier': 1.0
        }
        
        predicted_budget = model.predict_trip_budget(trip_features)
        
        if predicted_budget < 0:
            predicted_budget = abs(predicted_budget)
        
        return {
            "destination": destination,
            "num_days": num_days,
            "num_people": num_people,
            "accommodation_level": accommodation_level,
            "estimated_budget": float(predicted_budget),
            "currency": "USD",
            "breakdown": {
                "accommodation": float(predicted_budget * 0.35),
                "food": float(predicted_budget * 0.30),
                "activities": float(predicted_budget * 0.20),
                "transport": float(predicted_budget * 0.15)
            },
            "per_person": float(predicted_budget / num_people),
            "per_day": float(predicted_budget / num_days)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Budget estimation error: {e}")
        raise HTTPException(status_code=500, detail=f"Error estimating budget: {str(e)}")