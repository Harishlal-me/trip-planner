"""
Places and attractions endpoints - api/routes/places.py
Uses free Nominatim/OpenStreetMap API (no API key required)
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import logging
import aiohttp

router = APIRouter()
logger = logging.getLogger(__name__)

class PlaceFilter(BaseModel):
    category: str = None
    min_rating: float = 0.0
    max_price: int = 5

@router.get("/nearby")
async def get_nearby_places(
    city: str,
    category: str = None,
    radius_km: int = 5
):
    """Get nearby places in a city"""
    try:
        # Get city coordinates
        geo_url = f"https://nominatim.openstreetmap.org/search?city={city}&format=json&limit=1"
        
        headers = {'User-Agent': 'TripPlannerML/1.0'}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(geo_url, headers=headers) as resp:
                results = await resp.json()
        
        if not results:
            raise HTTPException(status_code=404, detail=f"City '{city}' not found")
        
        latitude = float(results[0]['lat'])
        longitude = float(results[0]['lon'])
        
        # Sample nearby places (in production, use Overpass API)
        sample_places = [
            {
                "id": 1,
                "name": "City Center Museum",
                "category": "museum",
                "rating": 4.7,
                "reviews": 234,
                "latitude": latitude + 0.01,
                "longitude": longitude + 0.01,
                "distance_km": 0.5,
                "price_level": 2,
                "open_now": True,
                "description": "Main city museum with cultural exhibits"
            },
            {
                "id": 2,
                "name": "Local Restaurant",
                "category": "restaurant",
                "rating": 4.5,
                "reviews": 156,
                "latitude": latitude - 0.01,
                "longitude": longitude - 0.01,
                "distance_km": 1.2,
                "price_level": 2,
                "open_now": True,
                "description": "Popular local cuisine restaurant"
            },
            {
                "id": 3,
                "name": "Public Park",
                "category": "park",
                "rating": 4.3,
                "reviews": 89,
                "latitude": latitude,
                "longitude": longitude + 0.02,
                "distance_km": 2.0,
                "price_level": 1,
                "open_now": True,
                "description": "Beautiful green space for walking"
            },
            {
                "id": 4,
                "name": "Historic Cathedral",
                "category": "attraction",
                "rating": 4.8,
                "reviews": 345,
                "latitude": latitude + 0.02,
                "longitude": longitude - 0.01,
                "distance_km": 1.5,
                "price_level": 1,
                "open_now": True,
                "description": "Ancient cathedral with architectural significance"
            },
            {
                "id": 5,
                "name": "Shopping District",
                "category": "shopping",
                "rating": 4.2,
                "reviews": 123,
                "latitude": latitude - 0.02,
                "longitude": longitude + 0.01,
                "distance_km": 2.5,
                "price_level": 3,
                "open_now": True,
                "description": "Main shopping and retail area"
            }
        ]
        
        # Filter by category if provided
        if category:
            sample_places = [p for p in sample_places if p['category'].lower() == category.lower()]
        
        # Sort by distance
        sample_places = sorted(sample_places, key=lambda x: x['distance_km'])
        
        return {
            "city": city,
            "latitude": latitude,
            "longitude": longitude,
            "search_radius_km": radius_km,
            "places_count": len(sample_places),
            "places": sample_places
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Places error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search")
async def search_places(query: str, limit: int = 10):
    """Search for places by name"""
    try:
        if limit > 50:
            limit = 50
        if limit < 1:
            limit = 1
        
        geo_url = f"https://nominatim.openstreetmap.org/search?q={query}&format=json&limit={limit}"
        headers = {'User-Agent': 'TripPlannerML/1.0'}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(geo_url, headers=headers) as resp:
                results = await resp.json()
        
        places = []
        for result in results:
            places.append({
                "name": result.get('name'),
                "type": result.get('type'),
                "latitude": float(result.get('lat')),
                "longitude": float(result.get('lon')),
                "display_name": result.get('display_name'),
                "importance": result.get('importance')
            })
        
        return {
            "query": query,
            "results_count": len(places),
            "places": places
        }
    except Exception as e:
        logger.error(f"Search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/recommend")
async def recommend_places(
    city: str,
    interests: List[str] = None,
    top_k: int = 10
):
    """Get place recommendations using ML model"""
    try:
        if not interests:
            interests = ["culture", "food"]
        
        if top_k > 20:
            top_k = 20
        if top_k < 1:
            top_k = 1
        
        from models.recommender.ml_ranking_model import MLRankingModel
        import pandas as pd
        
        # Load model
        model = MLRankingModel()
        model.load('ranking_model')
        
        # Create sample places dataframe
        sample_places = pd.DataFrame({
            'place_id': [1, 2, 3, 4, 5],
            'name': ['Museum', 'Restaurant', 'Park', 'Beach', 'Shopping Center'],
            'category': ['museum', 'restaurant', 'park', 'beach', 'shopping'],
            'rating': [4.7, 4.5, 4.3, 4.8, 4.2],
            'reviews_count': [234, 156, 89, 345, 123],
            'price_level': [2, 2, 1, 1, 3]
        })
        
        # Create user features
        user_features = {}
        for interest in interests:
            user_features[f'interest_{interest}'] = 1
        user_features['budget_encoded'] = 2
        
        # Rank places
        recommendations = model.rank_places(sample_places, user_features, top_k=top_k)
        
        return {
            "city": city,
            "interests": interests,
            "recommendations_count": len(recommendations),
            "recommendations": recommendations
        }
    except Exception as e:
        logger.error(f"Recommendation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))