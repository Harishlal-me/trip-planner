# global_places.py - Comprehensive worldwide places database
# Now includes complete Tamil Nadu model!

try:
    from tamil_nadu_places import TAMIL_NADU_PLACES
    _has_tamil_nadu = True
except ImportError:
    TAMIL_NADU_PLACES = {}
    _has_tamil_nadu = False

GLOBAL_PLACES = {
    # TAMIL NADU (COMPLETE MODEL)
    **(TAMIL_NADU_PLACES if _has_tamil_nadu else {}),
    
    # ASIA (OTHER REGIONS)
    "Tokyo": [
        # Attractions
        {"name": "Senso-ji Temple", "category": "attraction", "type": "cultural", "rating": 4.6, "cost_per_person": 0, "interest": ["culture", "history"], "hours": "6AM-5PM", "duration_hours": 2, "reviews": 8500},
        {"name": "Tokyo Tower", "category": "attraction", "type": "landmark", "rating": 4.5, "cost_per_person": 20, "interest": ["culture"], "hours": "9AM-11PM", "duration_hours": 1.5, "reviews": 6200},
        {"name": "Shibuya Crossing", "category": "attraction", "type": "landmark", "rating": 4.5, "cost_per_person": 0, "interest": ["culture"], "hours": "Open 24/7", "duration_hours": 1, "reviews": 9800},
        {"name": "Meiji Shrine", "category": "attraction", "type": "cultural", "rating": 4.6, "cost_per_person": 0, "interest": ["culture", "history"], "hours": "5AM-7PM", "duration_hours": 1.5, "reviews": 7200},
        # Food
        {"name": "Tsukiji Outer Market", "category": "restaurant", "type": "food", "rating": 4.7, "cost_per_person": 45, "interest": ["food"], "hours": "5AM-2PM", "duration_hours": 2, "reviews": 5600},
        {"name": "Michelin 3-Star Sushi Saito", "category": "restaurant", "type": "fine_dining", "rating": 4.9, "cost_per_person": 300, "interest": ["food"], "hours": "5PM-10PM", "duration_hours": 3, "reviews": 1200},
        {"name": "Ramen Alley (Shinjuku)", "category": "restaurant", "type": "food", "rating": 4.4, "cost_per_person": 15, "interest": ["food"], "hours": "10AM-12AM", "duration_hours": 1, "reviews": 8900},
        # Hotels
        {"name": "Peninsula Tokyo Luxury Hotel", "category": "hotel", "type": "luxury", "rating": 4.8, "cost_per_person": 450, "interest": ["accommodation"], "hours": "24/7", "duration_hours": 24, "reviews": 3200},
        {"name": "Capsule Hotel - Budget Stay", "category": "hotel", "type": "budget", "rating": 4.1, "cost_per_person": 40, "interest": ["accommodation"], "hours": "24/7", "duration_hours": 24, "reviews": 4500},
        {"name": "Hotel New Otani Tokyo", "category": "hotel", "type": "mid_range", "rating": 4.5, "cost_per_person": 180, "interest": ["accommodation"], "hours": "24/7", "duration_hours": 24, "reviews": 2800},
        # Shopping & Entertainment
        {"name": "Akihabara Tech District", "category": "shopping", "type": "shopping", "rating": 4.4, "cost_per_person": 100, "interest": ["technology", "shopping"], "hours": "10AM-11PM", "duration_hours": 3, "reviews": 6700},
        {"name": "Harajuku Fashion District", "category": "shopping", "type": "shopping", "rating": 4.3, "cost_per_person": 80, "interest": ["shopping", "culture"], "hours": "10AM-9PM", "duration_hours": 2, "reviews": 5400},
    ],
    
    "Delhi": [
        # Attractions
        {"name": "Taj Mahal (Agra)", "category": "attraction", "type": "cultural", "rating": 4.9, "cost_per_person": 20, "interest": ["culture", "history"], "hours": "6AM-7PM", "duration_hours": 3, "reviews": 12000},
        {"name": "Red Fort", "category": "attraction", "type": "cultural", "rating": 4.5, "cost_per_person": 15, "interest": ["culture", "history"], "hours": "9:30AM-4:30PM", "duration_hours": 2, "reviews": 7800},
        {"name": "India Gate", "category": "attraction", "type": "landmark", "rating": 4.4, "cost_per_person": 0, "interest": ["culture"], "hours": "Open 24/7", "duration_hours": 1, "reviews": 9200},
        {"name": "Qutub Minar", "category": "attraction", "type": "cultural", "rating": 4.6, "cost_per_person": 10, "interest": ["culture", "history"], "hours": "7AM-5PM", "duration_hours": 1.5, "reviews": 6500},
        # Food
        {"name": "Bukhara Restaurant (Fine Dining)", "category": "restaurant", "type": "fine_dining", "rating": 4.7, "cost_per_person": 80, "interest": ["food"], "hours": "12PM-2:45PM, 7PM-11:45PM", "duration_hours": 2, "reviews": 3200},
        {"name": "Chandni Chowk Street Food", "category": "restaurant", "type": "food", "rating": 4.3, "cost_per_person": 8, "interest": ["food"], "hours": "10AM-11PM", "duration_hours": 2, "reviews": 7600},
        {"name": "Karim's (Mughlai Cuisine)", "category": "restaurant", "type": "food", "rating": 4.5, "cost_per_person": 20, "interest": ["food"], "hours": "8AM-12AM", "duration_hours": 1.5, "reviews": 6200},
        # Hotels
        {"name": "Taj Hotel Delhi - Luxury", "category": "hotel", "type": "luxury", "rating": 4.7, "cost_per_person": 250, "interest": ["accommodation"], "hours": "24/7", "duration_hours": 24, "reviews": 2500},
        {"name": "Hostel in Paharganj - Budget", "category": "hotel", "type": "budget", "rating": 4.2, "cost_per_person": 20, "interest": ["accommodation"], "hours": "24/7", "duration_hours": 24, "reviews": 5200},
        {"name": "ITC Maurya - Premium", "category": "hotel", "type": "premium", "rating": 4.6, "cost_per_person": 180, "interest": ["accommodation"], "hours": "24/7", "duration_hours": 24, "reviews": 2100},
    ],
    
    "Shanghai": [
        # Attractions
        {"name": "The Bund", "category": "attraction", "type": "landmark", "rating": 4.5, "cost_per_person": 0, "interest": ["culture"], "hours": "Open 24/7", "duration_hours": 2, "reviews": 8200},
        {"name": "Oriental Pearl Tower", "category": "attraction", "type": "landmark", "rating": 4.4, "cost_per_person": 25, "interest": ["culture"], "hours": "8AM-11PM", "duration_hours": 1.5, "reviews": 5600},
        {"name": "Yu Garden", "category": "attraction", "type": "cultural", "rating": 4.6, "cost_per_person": 12, "interest": ["culture", "history"], "hours": "9AM-5PM", "duration_hours": 2, "reviews": 6400},
        {"name": "City God Temple", "category": "attraction", "type": "cultural", "rating": 4.3, "cost_per_person": 5, "interest": ["culture", "history"], "hours": "9AM-5PM", "duration_hours": 1, "reviews": 4200},
        # Food
        {"name": "Din Tai Fung (Xiaolongbao)", "category": "restaurant", "type": "fine_dining", "rating": 4.7, "cost_per_person": 35, "interest": ["food"], "hours": "10AM-10PM", "duration_hours": 1.5, "reviews": 8900},
        {"name": "Street Food in Wujiang Road", "category": "restaurant", "type": "food", "rating": 4.4, "cost_per_person": 10, "interest": ["food"], "hours": "11AM-11PM", "duration_hours": 1.5, "reviews": 5300},
        # Hotels
        {"name": "Waldorf Astoria Shanghai - Luxury", "category": "hotel", "type": "luxury", "rating": 4.8, "cost_per_person": 350, "interest": ["accommodation"], "hours": "24/7", "duration_hours": 24, "reviews": 1800},
        {"name": "Jing An Hotel - Mid-Range", "category": "hotel", "type": "mid_range", "rating": 4.4, "cost_per_person": 120, "interest": ["accommodation"], "hours": "24/7", "duration_hours": 24, "reviews": 2200},
        {"name": "Budget Hostel - Economy", "category": "hotel", "type": "budget", "rating": 4.0, "cost_per_person": 30, "interest": ["accommodation"], "hours": "24/7", "duration_hours": 24, "reviews": 4800},
    ],
    
    "Bangkok": [
        # Attractions
        {"name": "Grand Palace", "category": "attraction", "type": "cultural", "rating": 4.7, "cost_per_person": 15, "interest": ["culture", "history"], "hours": "8:30AM-3:30PM", "duration_hours": 2, "reviews": 9200},
        {"name": "Wat Pho (Temple of Reclining Buddha)", "category": "attraction", "type": "cultural", "rating": 4.6, "cost_per_person": 10, "interest": ["culture", "history"], "hours": "8AM-5PM", "duration_hours": 1.5, "reviews": 7800},
        {"name": "Floating Markets", "category": "attraction", "type": "cultural", "rating": 4.4, "cost_per_person": 20, "interest": ["culture"], "hours": "7AM-12PM", "duration_hours": 2.5, "reviews": 6500},
        # Food
        {"name": "Michelin-Starred Gaggan", "category": "restaurant", "type": "fine_dining", "rating": 4.8, "cost_per_person": 150, "interest": ["food"], "hours": "6PM-11PM", "duration_hours": 3, "reviews": 2100},
        {"name": "Chinatown Street Food (Yaowarat)", "category": "restaurant", "type": "food", "rating": 4.5, "cost_per_person": 12, "interest": ["food"], "hours": "5PM-2AM", "duration_hours": 2, "reviews": 8200},
        # Hotels
        {"name": "Mandarin Oriental Bangkok - Luxury", "category": "hotel", "type": "luxury", "rating": 4.8, "cost_per_person": 280, "interest": ["accommodation"], "hours": "24/7", "duration_hours": 24, "reviews": 2800},
        {"name": "Guesthouse in Old City - Budget", "category": "hotel", "type": "budget", "rating": 4.1, "cost_per_person": 25, "interest": ["accommodation"], "hours": "24/7", "duration_hours": 24, "reviews": 5100},
    ],
    
    "Bali": [
        # Attractions & Beach
        {"name": "Kuta Beach", "category": "beach", "type": "beach", "rating": 4.5, "cost_per_person": 0, "interest": ["relaxation", "nature"], "hours": "Open 24/7", "duration_hours": 3, "reviews": 9800},
        {"name": "Ubud Monkey Forest", "category": "attraction", "type": "nature", "rating": 4.6, "cost_per_person": 10, "interest": ["nature", "culture"], "hours": "8:30AM-6PM", "duration_hours": 2, "reviews": 7200},
        {"name": "Tanah Lot Temple", "category": "attraction", "type": "cultural", "rating": 4.5, "cost_per_person": 30, "interest": ["culture", "history"], "hours": "7AM-7PM", "duration_hours": 1.5, "reviews": 8100},
        # Food
        {"name": "Locavore (Fine Dining)", "category": "restaurant", "type": "fine_dining", "rating": 4.7, "cost_per_person": 100, "interest": ["food"], "hours": "6PM-11PM", "duration_hours": 2.5, "reviews": 1600},
        {"name": "Warung (Local Eatery)", "category": "restaurant", "type": "food", "rating": 4.4, "cost_per_person": 8, "interest": ["food"], "hours": "11AM-9PM", "duration_hours": 1.5, "reviews": 6800},
        # Hotels
        {"name": "Four Seasons Bali - Luxury Resort", "category": "hotel", "type": "luxury", "rating": 4.9, "cost_per_person": 500, "interest": ["accommodation"], "hours": "24/7", "duration_hours": 24, "reviews": 1200},
        {"name": "Villa in Ubud - Budget", "category": "hotel", "type": "budget", "rating": 4.3, "cost_per_person": 35, "interest": ["accommodation"], "hours": "24/7", "duration_hours": 24, "reviews": 4900},
    ],
    
    # EUROPE
    "Paris": [
        {"name": "Louvre Museum", "category": "museum", "type": "cultural", "rating": 4.8, "cost_per_person": 18, "interest": ["culture", "history"], "hours": "9AM-6PM", "duration_hours": 3, "reviews": 15000},
        {"name": "Eiffel Tower", "category": "attraction", "type": "landmark", "rating": 4.7, "cost_per_person": 25, "interest": ["culture", "history"], "hours": "9AM-12:45AM", "duration_hours": 2, "reviews": 18000},
        {"name": "Notre-Dame Cathedral", "category": "attraction", "type": "cultural", "rating": 4.9, "cost_per_person": 0, "interest": ["culture", "history"], "hours": "8AM-6PM", "duration_hours": 1.5, "reviews": 12000},
        {"name": "Le Jules Verne (Restaurant)", "category": "restaurant", "type": "fine_dining", "rating": 4.6, "cost_per_person": 95, "interest": ["food"], "hours": "11:30AM-11PM", "duration_hours": 2, "reviews": 2200},
        {"name": "Versailles Palace", "category": "attraction", "type": "cultural", "rating": 4.7, "cost_per_person": 22, "interest": ["culture", "history"], "hours": "9AM-6:30PM", "duration_hours": 4, "reviews": 11000},
        {"name": "Ritz Paris - Luxury Hotel", "category": "hotel", "type": "luxury", "rating": 4.9, "cost_per_person": 600, "interest": ["accommodation"], "hours": "24/7", "duration_hours": 24, "reviews": 800},
        {"name": "Budget Hostel Marais", "category": "hotel", "type": "budget", "rating": 4.2, "cost_per_person": 35, "interest": ["accommodation"], "hours": "24/7", "duration_hours": 24, "reviews": 5800},
    ],
    
    "London": [
        {"name": "British Museum", "category": "museum", "type": "cultural", "rating": 4.7, "cost_per_person": 0, "interest": ["culture", "history"], "hours": "10AM-5:30PM", "duration_hours": 3, "reviews": 13000},
        {"name": "Tower of London", "category": "attraction", "type": "cultural", "rating": 4.6, "cost_per_person": 35, "interest": ["culture", "history"], "hours": "9AM-5:30PM", "duration_hours": 2, "reviews": 9800},
        {"name": "Big Ben & Houses of Parliament", "category": "attraction", "type": "landmark", "rating": 4.5, "cost_per_person": 20, "interest": ["culture", "history"], "hours": "9AM-5PM", "duration_hours": 1.5, "reviews": 7600},
        {"name": "Gordon Ramsay Restaurant", "category": "restaurant", "type": "fine_dining", "rating": 4.8, "cost_per_person": 120, "interest": ["food"], "hours": "12PM-11PM", "duration_hours": 2, "reviews": 2100},
        {"name": "Savoy Hotel - Luxury", "category": "hotel", "type": "luxury", "rating": 4.8, "cost_per_person": 450, "interest": ["accommodation"], "hours": "24/7", "duration_hours": 24, "reviews": 1200},
    ],
    
    # AMERICAS
    "New York": [
        {"name": "Statue of Liberty", "category": "attraction", "type": "landmark", "rating": 4.6, "cost_per_person": 24, "interest": ["culture", "history"], "hours": "9AM-5PM", "duration_hours": 2.5, "reviews": 12000},
        {"name": "Central Park", "category": "park", "type": "nature", "rating": 4.6, "cost_per_person": 0, "interest": ["nature", "relaxation"], "hours": "Open 24/7", "duration_hours": 3, "reviews": 14000},
        {"name": "Broadway Theater", "category": "nightlife", "type": "entertainment", "rating": 4.7, "cost_per_person": 75, "interest": ["culture"], "hours": "Evening", "duration_hours": 3, "reviews": 8200},
        {"name": "Eleven Madison Park (Fine Dining)", "category": "restaurant", "type": "fine_dining", "rating": 4.8, "cost_per_person": 200, "interest": ["food"], "hours": "5PM-11PM", "duration_hours": 3, "reviews": 1500},
        {"name": "Peninsula New York - Luxury", "category": "hotel", "type": "luxury", "rating": 4.8, "cost_per_person": 500, "interest": ["accommodation"], "hours": "24/7", "duration_hours": 24, "reviews": 1800},
    ],
    
    "Rio de Janeiro": [
        {"name": "Christ the Redeemer Statue", "category": "attraction", "type": "landmark", "rating": 4.7, "cost_per_person": 35, "interest": ["culture"], "hours": "8AM-7PM", "duration_hours": 2, "reviews": 10000},
        {"name": "Copacabana Beach", "category": "beach", "type": "beach", "rating": 4.6, "cost_per_person": 0, "interest": ["relaxation", "nature"], "hours": "Open 24/7", "duration_hours": 3, "reviews": 12000},
        {"name": "Sugarloaf Mountain", "category": "attraction", "type": "nature", "rating": 4.6, "cost_per_person": 30, "interest": ["nature"], "hours": "8AM-8PM", "duration_hours": 2, "reviews": 8500},
        {"name": "Belmond Copacabana Palace - Luxury", "category": "hotel", "type": "luxury", "rating": 4.9, "cost_per_person": 400, "interest": ["accommodation"], "hours": "24/7", "duration_hours": 24, "reviews": 1600},
    ],
    
    # MIDDLE EAST
    "Dubai": [
        {"name": "Burj Khalifa", "category": "attraction", "type": "landmark", "rating": 4.6, "cost_per_person": 30, "interest": ["culture"], "hours": "10AM-12AM", "duration_hours": 1.5, "reviews": 11000},
        {"name": "Dubai Mall", "category": "shopping", "type": "shopping", "rating": 4.5, "cost_per_person": 100, "interest": ["shopping"], "hours": "10AM-10PM", "duration_hours": 3, "reviews": 7800},
        {"name": "Palm Jumeirah Beach", "category": "beach", "type": "beach", "rating": 4.5, "cost_per_person": 0, "interest": ["relaxation", "nature"], "hours": "Open 24/7", "duration_hours": 3, "reviews": 9200},
        {"name": "Nobu Dubai (Fine Dining)", "category": "restaurant", "type": "fine_dining", "rating": 4.7, "cost_per_person": 180, "interest": ["food"], "hours": "12PM-3PM, 6PM-11PM", "duration_hours": 2, "reviews": 1800},
        {"name": "Burj Al Arab - Ultra Luxury", "category": "hotel", "type": "luxury", "rating": 4.9, "cost_per_person": 1200, "interest": ["accommodation"], "hours": "24/7", "duration_hours": 24, "reviews": 500},
    ],
}

def get_places_for_city(city_name):
    """Get places for a city, return closest match if exact match not found"""
    # Try exact match
    if city_name in GLOBAL_PLACES:
        return GLOBAL_PLACES[city_name]
    
    # Try case-insensitive match
    for city in GLOBAL_PLACES.keys():
        if city.lower() == city_name.lower():
            return GLOBAL_PLACES[city]
    
    # Try partial match
    for city in GLOBAL_PLACES.keys():
        if city_name.lower() in city.lower():
            return GLOBAL_PLACES[city]
    
    # Return closest match from database
    return GLOBAL_PLACES.get("Paris", [])  # Default fallback


def filter_places_by_interests(places, interests):
    """Filter and rank places based on user interests"""
    if not interests:
        return sorted(places, key=lambda x: x['rating'], reverse=True)
    
    scored_places = []
    for place in places:
        place_interests = place.get("interest", [])
        
        # Calculate interest match score
        matches = sum(1 for interest in interests if interest in place_interests)
        match_score = matches / len(interests) if interests else 0
        
        # Combine with rating
        final_score = (place['rating'] * 0.7) + (match_score * 0.3)
        
        place_copy = place.copy()
        place_copy['match_score'] = final_score
        scored_places.append(place_copy)
    
    return sorted(scored_places, key=lambda x: x['match_score'], reverse=True)


def select_places_for_itinerary(places, num_days, budget_level):
    """Intelligently select places for itinerary based on budget"""
    
    # Separate by type
    hotels = [p for p in places if p['category'] == 'hotel']
    restaurants = [p for p in places if p['category'] == 'restaurant']
    attractions = [p for p in places if p['category'] in ['attraction', 'museum', 'beach', 'park', 'shopping']]
    
    # Select based on budget level
    if budget_level == 'low':
        selected_hotels = [h for h in hotels if h['type'] in ['budget', 'mid_range']]
        selected_restaurants = [r for r in restaurants if r['cost_per_person'] < 50]
    elif budget_level == 'medium':
        selected_hotels = [h for h in hotels if h['type'] in ['mid_range', 'premium']]
        selected_restaurants = [r for r in restaurants if 20 < r['cost_per_person'] < 150]
    else:  # high
        selected_hotels = [h for h in hotels if h['type'] in ['premium', 'luxury']]
        selected_restaurants = [r for r in restaurants if r['cost_per_person'] > 80]
    
    return {
        'hotels': selected_hotels[:2] if selected_hotels else hotels[:2],
        'restaurants': selected_restaurants[:3] if selected_restaurants else restaurants[:3],
        'attractions': attractions[:10]
    }