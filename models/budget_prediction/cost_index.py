"""
Cost Index Database for Different Cities/Countries
Contains cost of living data for budget predictions
"""

# Cost index relative to baseline (1.0 = average)
CITY_COST_INDEX = {
    # Asia - Budget Friendly
    "bangkok": 0.55, "hanoi": 0.45, "ho chi minh": 0.50, "manila": 0.50,
    "jakarta": 0.48, "kuala lumpur": 0.52, "delhi": 0.42, "mumbai": 0.48,
    "bangalore": 0.50, "kathmandu": 0.40, "colombo": 0.45,
    
    # Asia - Moderate
    "beijing": 0.75, "shanghai": 0.80, "seoul": 1.15, "taipei": 0.85,
    "osaka": 1.10, "kyoto": 1.05, "dubai": 1.25,
    
    # Asia - Expensive
    "tokyo": 1.45, "hong kong": 1.50, "singapore": 1.55,
    
    # Europe - Budget Friendly
    "sofia": 0.55, "bucharest": 0.58, "budapest": 0.65, "prague": 0.75,
    "warsaw": 0.70, "lisbon": 0.80, "athens": 0.78, "barcelona": 0.95,
    
    # Europe - Moderate
    "rome": 1.05, "milan": 1.10, "berlin": 0.95, "vienna": 1.00,
    "amsterdam": 1.20, "dublin": 1.15,
    
    # Europe - Expensive
    "london": 1.40, "paris": 1.35, "zurich": 1.75, "oslo": 1.60,
    "copenhagen": 1.55, "stockholm": 1.45,
    
    # North America
    "mexico city": 0.60, "toronto": 1.10, "vancouver": 1.15,
    "new york": 1.50, "san francisco": 1.60, "los angeles": 1.35,
    "miami": 1.05, "chicago": 1.20,
    
    # South America
    "buenos aires": 0.62, "santiago": 0.70, "rio de janeiro": 0.68,
    "lima": 0.55, "bogota": 0.52,
    
    # Oceania
    "sydney": 1.35, "melbourne": 1.30, "auckland": 1.25,
}

COUNTRY_COST_INDEX = {
    "thailand": 0.55, "vietnam": 0.48, "india": 0.45, "indonesia": 0.48,
    "china": 0.75, "japan": 1.25, "singapore": 1.55, "south korea": 1.15,
    "spain": 0.92, "italy": 1.05, "france": 1.30, "germany": 1.00,
    "uk": 1.35, "switzerland": 1.72, "norway": 1.60,
    "usa": 1.25, "canada": 1.10, "mexico": 0.60,
    "australia": 1.30, "new zealand": 1.22,
}

def get_destination_cost_index(destination: str) -> float:
    """Get cost index for a destination"""
    dest_lower = destination.lower().strip()
    
    if dest_lower in CITY_COST_INDEX:
        return CITY_COST_INDEX[dest_lower]
    
    if dest_lower in COUNTRY_COST_INDEX:
        return COUNTRY_COST_INDEX[dest_lower]
    
    for city, index in CITY_COST_INDEX.items():
        if city in dest_lower:
            return index
    
    for country, index in COUNTRY_COST_INDEX.items():
        if country in dest_lower:
            return index
    
    return 1.0  # Default


def estimate_daily_cost(destination: str, accommodation_level: str = "mid_range") -> dict:
    """Estimate daily cost for a destination"""
    base_cost = 100.0
    dest_multiplier = get_destination_cost_index(destination)
    
    acc_multipliers = {
        "hostel": 0.3, "budget_hotel": 0.5, "mid_range": 1.0,
        "upscale": 1.8, "luxury": 3.0
    }
    
    acc_mult = acc_multipliers.get(accommodation_level, 1.0)
    
    accommodation_cost = base_cost * 0.4 * dest_multiplier * acc_mult
    food_cost = base_cost * 0.3 * dest_multiplier
    transport_cost = base_cost * 0.15 * dest_multiplier
    activities_cost = base_cost * 0.12 * dest_multiplier
    misc_cost = base_cost * 0.03 * dest_multiplier
    
    total = accommodation_cost + food_cost + transport_cost + activities_cost + misc_cost
    
    return {
        "destination": destination,
        "total_daily_cost": round(total, 2),
        "breakdown": {
            "accommodation": round(accommodation_cost, 2),
            "food": round(food_cost, 2),
            "transportation": round(transport_cost, 2),
            "activities": round(activities_cost, 2),
            "miscellaneous": round(misc_cost, 2)
        }
    }