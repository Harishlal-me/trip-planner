"""
Enhanced Trip planning - api/routes/trip.py
Global places database with smart hotel, restaurant, beach recommendations
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from datetime import datetime
import logging
import sys
from pathlib import Path

# Add parent directory to path to import global_places
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from global_places import (
    get_places_for_city,
    filter_places_by_interests,
    select_places_for_itinerary
)
from tamil_nadu_places import get_tamil_nadu_places, filter_tn_places_by_category

router = APIRouter()
logger = logging.getLogger(__name__)

class TripRequest(BaseModel):
    destination: str
    start_date: str
    end_date: str
    num_people: int
    budget_level: str = "medium"
    interests: List[str] = ["culture", "food"]
    accommodation_level: int = 3

@router.post("/plan")
async def plan_trip(request: TripRequest):
    """Create complete trip plan with global recommendations"""
    try:
        # Parse dates
        start_date = datetime.fromisoformat(request.start_date)
        end_date = datetime.fromisoformat(request.end_date)
        num_days = (end_date - start_date).days

        if num_days <= 0:
            raise HTTPException(status_code=400, detail="End date must be after start date")

        # Get city name
        destination_city = request.destination.split(',')[0].strip()

        # Load ML models
        from models.budget_prediction.ml_budget_model import MLBudgetModel

        budget_model = MLBudgetModel()
        budget_model.load('budget_model')

        # Predict budget
        trip_features = {
            'num_days': num_days,
            'num_people': request.num_people,
            'accommodation_level': request.accommodation_level,
            'destination_cost_index': 1.0,
            'season_multiplier': 1.0
        }

        total_budget = budget_model.predict_trip_budget(trip_features)
        if total_budget < 0:
            total_budget = abs(total_budget)

        # Check if it's a Tamil Nadu city
        tamil_nadu_cities = list(TAMIL_NADU_PLACES.keys())
        is_tamil_nadu = destination_city in tamil_nadu_cities or any(
            destination_city.lower() == city.lower() for city in tamil_nadu_cities
        )

        # Get places - prioritize Tamil Nadu
        if is_tamil_nadu:
            all_places = get_tamil_nadu_places(destination_city)
            logger.info(f"Tamil Nadu destination detected: {destination_city}")
        else:
            all_places = get_places_for_city(destination_city)

        # Filter by interests
        filtered_places = filter_places_by_interests(all_places, request.interests)

        # Select places by type and budget
        selected = select_places_for_itinerary(filtered_places, num_days, request.budget_level)

        # Generate detailed itinerary
        itinerary = generate_detailed_itinerary(
            selected,
            num_days,
            request.num_people,
            total_budget,
            request.budget_level
        )

        # Calculate budget breakdown
        accommodation_cost = total_budget * 0.35
        food_cost = total_budget * 0.30
        activities_cost = total_budget * 0.20
        transport_cost = total_budget * 0.15

        return {
            "trip_summary": {
                "destination": request.destination,
                "start_date": request.start_date,
                "end_date": request.end_date,
                "num_days": num_days,
                "num_people": request.num_people,
                "interests": request.interests,
                "budget_level": request.budget_level
            },
            "budget": {
                "total": float(total_budget),
                "per_day": float(total_budget / num_days),
                "per_person": float(total_budget / request.num_people),
                "currency": "USD",
                "breakdown": {
                    "accommodation": float(accommodation_cost),
                    "food": float(food_cost),
                    "activities": float(activities_cost),
                    "transport": float(transport_cost)
                }
            },
            "recommendations": {
                "places": filtered_places[:5],
                "hotels": selected['hotels'],
                "restaurants": selected['restaurants'],
                "attractions": selected['attractions'][:5],
                "count": len(filtered_places)
            },
            "itinerary": itinerary
        }

    except Exception as e:
        logger.error(f"Trip planning error: {e}")
        raise HTTPException(status_code=500, detail=f"Error planning trip: {str(e)}")


def generate_detailed_itinerary(selected, num_days, num_people, total_budget, budget_level):
    """Generate day-by-day itinerary with smart place selection"""
    itinerary = []
    daily_budget = total_budget / num_days

    hotels = selected['hotels']
    restaurants = selected['restaurants']
    attractions = selected['attractions']

    for day in range(1, min(num_days + 1, 8)):
        day_activities = []
        day_cost = 0

        # Morning activity (attraction/museum)
        morning_idx = (day - 1) % len(attractions)
        morning_place = attractions[morning_idx]
        morning_activity = {
            "time": "9:00 AM",
            "period": "morning",
            "place": morning_place['name'],
            "category": morning_place['category'],
            "type": morning_place.get('type', 'attraction'),
            "cost": float(morning_place['cost_per_person'] * num_people),
            "cost_per_person": float(morning_place['cost_per_person']),
            "duration": f"{morning_place['duration_hours']} hours",
            "rating": morning_place['rating'],
            "reviews": morning_place.get('reviews', 0),
            "hours": morning_place['hours']
        }
        day_activities.append(morning_activity)
        day_cost += morning_activity['cost']

        # Afternoon activity (restaurant)
        afternoon_idx = (day - 1) % len(restaurants)
        afternoon_place = restaurants[afternoon_idx]
        afternoon_activity = {
            "time": "1:00 PM",
            "period": "afternoon",
            "place": afternoon_place['name'],
            "category": afternoon_place['category'],
            "type": afternoon_place.get('type', 'restaurant'),
            "cost": float(afternoon_place['cost_per_person'] * num_people),
            "cost_per_person": float(afternoon_place['cost_per_person']),
            "duration": f"{afternoon_place['duration_hours']} hours",
            "rating": afternoon_place['rating'],
            "reviews": afternoon_place.get('reviews', 0),
            "hours": afternoon_place['hours']
        }
        day_activities.append(afternoon_activity)
        day_cost += afternoon_activity['cost']

        # Evening activity (restaurant/entertainment)
        evening_idx = (day) % len(restaurants)
        evening_place = restaurants[evening_idx]
        evening_activity = {
            "time": "7:00 PM",
            "period": "evening",
            "place": evening_place['name'],
            "category": evening_place['category'],
            "type": evening_place.get('type', 'restaurant'),
            "cost": float(evening_place['cost_per_person'] * num_people),
            "cost_per_person": float(evening_place['cost_per_person']),
            "duration": f"{evening_place['duration_hours']} hours",
            "rating": evening_place['rating'],
            "reviews": evening_place.get('reviews', 0),
            "hours": evening_place['hours']
        }
        day_activities.append(evening_activity)
        day_cost += evening_activity['cost']

        # Hotel recommendation (show on first day)
        hotel_recommendation = None
        if day == 1 and hotels:
            hotel = hotels[0]
            hotel_recommendation = {
                "place": hotel['name'],
                "type": hotel['type'],
                "cost_per_night": float(hotel['cost_per_person']),
                "rating": hotel['rating'],
                "reviews": hotel.get('reviews', 0)
            }

        day_plan = {
            "day": day,
            "date": f"Day {day}",
            "daily_budget": float(daily_budget),
            "activities_cost": float(day_cost),
            "activities": day_activities,
            "hotel": hotel_recommendation
        }

        itinerary.append(day_plan)

    return itinerary


@router.post("/estimate")
async def estimate_trip(
    destination: str,
    num_days: int,
    num_people: int,
    budget_level: str = "medium"
):
    """Quick trip estimate"""
    try:
        if num_days < 1 or num_days > 365:
            raise HTTPException(status_code=400, detail="num_days must be between 1 and 365")
        if num_people < 1 or num_people > 50:
            raise HTTPException(status_code=400, detail="num_people must be between 1 and 50")

        from models.budget_prediction.ml_budget_model import MLBudgetModel

        model = MLBudgetModel()
        model.load('budget_model')

        trip_features = {
            'num_days': num_days,
            'num_people': num_people,
            'accommodation_level': 3,
            'destination_cost_index': 1.0,
            'season_multiplier': 1.0
        }

        total_budget = model.predict_trip_budget(trip_features)

        if total_budget < 0:
            total_budget = abs(total_budget)

        return {
            "destination": destination,
            "num_days": num_days,
            "num_people": num_people,
            "budget_level": budget_level,
            "estimated_total": float(total_budget),
            "per_person": float(total_budget / num_people),
            "per_day": float(total_budget / num_days),
            "currency": "USD"
        }
    except Exception as e:
        logger.error(f"Estimate error: {e}")
        raise HTTPException(status_code=500, detail=f"Error estimating trip: {str(e)}")