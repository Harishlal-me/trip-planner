"""
Transport Mode Selection and Cost Estimation
Smart selection of transportation based on distance, time, and budget
"""

import logging
from typing import Dict, List, Optional
from dataclasses import dataclass

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class TransportOption:
    """Transportation option details"""
    mode: str
    cost: float
    duration_minutes: float
    distance_km: float
    comfort_level: int
    environmental_impact: str
    notes: List[str]


class TransportSelector:
    """Smart transportation mode selector"""
    
    BASE_COSTS = {
        "walking": 0, "cycling": 0, "bike_rental": 0.5,
        "public_transit": 0.3, "bus": 0.2, "metro": 0.3,
        "taxi": 2.0, "rideshare": 1.8, "car_rental": 0.8,
        "train": 0.4, "flight": 0.15
    }
    
    SPEEDS = {
        "walking": 5, "cycling": 15, "bike_rental": 15,
        "public_transit": 25, "bus": 30, "metro": 40,
        "taxi": 40, "rideshare": 40, "car_rental": 60,
        "train": 100, "flight": 600
    }
    
    COMFORT = {
        "walking": 2, "cycling": 2, "bike_rental": 2,
        "public_transit": 3, "bus": 3, "metro": 3,
        "taxi": 4, "rideshare": 4, "car_rental": 4,
        "train": 4, "flight": 3
    }
    
    def __init__(self, destination_cost_multiplier: float = 1.0):
        self.cost_multiplier = destination_cost_multiplier
    
    def calculate_transport_options(self, distance_km: float,
                                    budget_level: str = "medium",
                                    time_constraint: Optional[float] = None) -> List[TransportOption]:
        """Calculate available transport options"""
        options = []
        practical_modes = self._get_practical_modes(distance_km)
        
        for mode in practical_modes:
            base_cost = self.BASE_COSTS[mode] * distance_km
            cost = base_cost * self.cost_multiplier
            
            # Add fixed costs
            if mode in ["taxi", "rideshare"]:
                cost += 5 * self.cost_multiplier
            elif mode == "car_rental":
                cost += 50
            elif mode == "flight":
                cost += 100
            
            # Calculate duration
            speed = self.SPEEDS[mode]
            duration_hours = distance_km / speed
            duration_minutes = duration_hours * 60
            
            # Add wait time
            if mode in ["public_transit", "bus", "metro"]:
                duration_minutes += 15
            elif mode == "flight":
                duration_minutes += 120
            
            # Check time constraint
            if time_constraint and duration_hours > time_constraint:
                continue
            
            option = TransportOption(
                mode=mode,
                cost=round(cost, 2),
                duration_minutes=round(duration_minutes, 1),
                distance_km=distance_km,
                comfort_level=self.COMFORT[mode],
                environmental_impact=self._get_environmental_impact(mode),
                notes=self._get_notes(mode, distance_km)
            )
            
            options.append(option)
        
        # Sort by suitability
        return sorted(options, key=lambda x: (-x.comfort_level, x.cost))
    
    def _get_practical_modes(self, distance_km: float) -> List[str]:
        """Determine which modes make sense for the distance"""
        modes = []
        
        if distance_km <= 2:
            modes.extend(["walking", "cycling", "bike_rental"])
        if distance_km <= 5:
            modes.extend(["public_transit", "taxi", "rideshare"])
        if distance_km <= 30:
            modes.extend(["bus", "metro", "car_rental"])
        if distance_km <= 200:
            modes.extend(["train"])
        if distance_km > 200:
            modes.extend(["flight"])
        
        return list(set(modes))
    
    def _get_environmental_impact(self, mode: str) -> str:
        """Categorize environmental impact"""
        low = ["walking", "cycling", "bike_rental", "public_transit", "metro", "train"]
        medium = ["bus", "rideshare"]
        
        if mode in low:
            return "low"
        elif mode in medium:
            return "medium"
        else:
            return "high"
    
    def _get_notes(self, mode: str, distance_km: float) -> List[str]:
        """Get helpful notes about the transport mode"""
        notes = []
        
        if mode == "walking":
            if distance_km > 3:
                notes.append("Long walk - consider breaks")
            notes.append("Good for sightseeing")
        elif mode == "cycling":
            notes.append("Healthy and eco-friendly")
        elif mode in ["public_transit", "bus", "metro"]:
            notes.append("Most economical option")
        elif mode in ["taxi", "rideshare"]:
            notes.append("Door-to-door service")
        elif mode == "train":
            notes.append("Comfortable for long distances")
        elif mode == "flight":
            notes.append("Fastest for long distances")
        
        return notes
    
    def recommend_best_option(self, distance_km: float,
                             budget_level: str = "medium") -> Optional[TransportOption]:
        """Get single best recommendation"""
        options = self.calculate_transport_options(distance_km, budget_level)
        return options[0] if options else None
    
    def estimate_daily_transport_budget(self, avg_distance_per_day: float,
                                       num_days: int, budget_level: str = "medium") -> Dict:
        """Estimate total transportation budget for trip"""
        transport_mix = {
            "low": {"public_transit": 0.7, "walking": 0.3},
            "medium": {"public_transit": 0.5, "taxi": 0.2, "walking": 0.3},
            "high": {"taxi": 0.5, "car_rental": 0.3, "public_transit": 0.2}
        }
        
        mix = transport_mix.get(budget_level, transport_mix["medium"])
        
        daily_cost = 0
        breakdown = {}
        
        for mode, proportion in mix.items():
            distance = avg_distance_per_day * proportion
            cost = self.BASE_COSTS[mode] * distance * self.cost_multiplier
            
            if mode == "taxi":
                cost += 5 * self.cost_multiplier
            elif mode == "car_rental":
                cost = 50
            
            daily_cost += cost
            breakdown[mode] = round(cost, 2)
        
        return {
            "daily_budget": round(daily_cost, 2),
            "total_budget": round(daily_cost * num_days, 2),
            "num_days": num_days,
            "breakdown": breakdown,
            "budget_level": budget_level
        }