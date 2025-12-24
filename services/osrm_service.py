"""
services/osrm_service.py
Free Routing Service using OSRM (Open Source Routing Machine)
Calculate routes, distances, and travel times globally
"""

import requests
import time
from typing import Dict, List, Optional, Tuple
import json


class OSRMService:
    """
    Free routing service using OSRM public API.
    No API key required, supports driving, walking, cycling.
    """
    
    BASE_URL = "http://router.project-osrm.org"
    
    PROFILES = {
        'car': 'driving',
        'driving': 'driving',
        'walk': 'foot',
        'walking': 'foot',
        'foot': 'foot',
        'bike': 'bike',
        'cycling': 'bike',
        'bicycle': 'bike'
    }
    
    def __init__(self):
        """Initialize OSRM service."""
        self.last_request_time = 0
        self.rate_limit_delay = 0.5
    
    def _rate_limit(self):
        """Rate limiting for fair usage."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - time_since_last)
        
        self.last_request_time = time.time()
    
    def _get_profile(self, mode: str) -> str:
        """Get OSRM profile from transport mode."""
        return self.PROFILES.get(mode.lower(), 'driving')
    
    def _make_request(self, url: str) -> Optional[Dict]:
        """Make HTTP request to OSRM API."""
        self._rate_limit()
        
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ OSRM API error: {e}")
            return None
    
    def get_route(
        self,
        coordinates: List[Tuple[float, float]],
        mode: str = 'driving',
        alternatives: bool = False,
        steps: bool = True,
        overview: str = 'full'
    ) -> Optional[Dict]:
        """Get route between multiple points."""
        if len(coordinates) < 2:
            return None
        
        profile = self._get_profile(mode)
        coords_str = ';'.join([f"{lon},{lat}" for lon, lat in coordinates])
        
        url = f"{self.BASE_URL}/route/v1/{profile}/{coords_str}"
        params = []
        if alternatives:
            params.append("alternatives=true")
        if steps:
            params.append("steps=true")
        params.append(f"overview={overview}")
        params.append("geometries=geojson")
        
        if params:
            url += "?" + "&".join(params)
        
        result = self._make_request(url)
        
        if not result or result.get('code') != 'Ok':
            return None
        
        route = result['routes'][0]
        
        return {
            'distance_km': round(route['distance'] / 1000, 2),
            'distance_m': route['distance'],
            'duration_seconds': route['duration'],
            'duration_minutes': round(route['duration'] / 60, 2),
            'duration_hours': round(route['duration'] / 3600, 2),
            'geometry': route.get('geometry'),
            'legs': self._parse_legs(route.get('legs', [])),
            'mode': mode
        }
    
    def get_distance(
        self,
        origin: Tuple[float, float],
        destination: Tuple[float, float],
        mode: str = 'driving'
    ) -> Optional[Dict]:
        """Get distance and duration between two points."""
        route = self.get_route(
            [origin, destination],
            mode=mode,
            steps=False,
            overview='false'
        )
        
        if not route:
            return None
        
        return {
            'origin': {'lon': origin[0], 'lat': origin[1]},
            'destination': {'lon': destination[0], 'lat': destination[1]},
            'distance_km': route['distance_km'],
            'duration_minutes': route['duration_minutes'],
            'duration_hours': route['duration_hours'],
            'mode': mode
        }
    
    def get_distance_matrix(
        self,
        sources: List[Tuple[float, float]],
        destinations: Optional[List[Tuple[float, float]]] = None,
        mode: str = 'driving'
    ) -> Optional[Dict]:
        """Get distance matrix between multiple points."""
        if not sources:
            return None
        
        if destinations is None:
            destinations = sources
        
        profile = self._get_profile(mode)
        all_coords = sources + destinations
        coords_str = ';'.join([f"{lon},{lat}" for lon, lat in all_coords])
        
        source_indices = ';'.join([str(i) for i in range(len(sources))])
        dest_indices = ';'.join([str(i + len(sources)) for i in range(len(destinations))])
        
        url = f"{self.BASE_URL}/table/v1/{profile}/{coords_str}"
        url += f"?sources={source_indices}&destinations={dest_indices}"
        
        result = self._make_request(url)
        
        if not result or result.get('code') != 'Ok':
            return None
        
        return {
            'distances': result['distances'],
            'durations': result['durations'],
            'sources': sources,
            'destinations': destinations,
            'mode': mode
        }
    
    def optimize_route(
        self,
        coordinates: List[Tuple[float, float]],
        mode: str = 'driving',
        roundtrip: bool = True
    ) -> Optional[Dict]:
        """Optimize route order for multiple waypoints (TSP solver)."""
        if len(coordinates) < 2:
            return None
        
        profile = self._get_profile(mode)
        coords_str = ';'.join([f"{lon},{lat}" for lon, lat in coordinates])
        
        url = f"{self.BASE_URL}/trip/v1/{profile}/{coords_str}"
        url += f"?roundtrip={'true' if roundtrip else 'false'}"
        url += "&source=first&destination=last&geometries=geojson"
        
        result = self._make_request(url)
        
        if not result or result.get('code') != 'Ok':
            return None
        
        trip = result['trips'][0]
        waypoint_order = [wp['waypoint_index'] for wp in result['waypoints']]
        
        return {
            'distance_km': round(trip['distance'] / 1000, 2),
            'duration_minutes': round(trip['duration'] / 60, 2),
            'duration_hours': round(trip['duration'] / 3600, 2),
            'optimized_order': waypoint_order,
            'optimized_coordinates': [coordinates[i] for i in waypoint_order],
            'geometry': trip.get('geometry'),
            'mode': mode,
            'roundtrip': roundtrip
        }
    
    def _parse_legs(self, legs: List[Dict]) -> List[Dict]:
        """Parse route legs into simplified format."""
        parsed_legs = []
        
        for leg in legs:
            parsed_legs.append({
                'distance_km': round(leg['distance'] / 1000, 2),
                'duration_minutes': round(leg['duration'] / 60, 2),
                'steps': len(leg.get('steps', []))
            })
        
        return parsed_legs
    
    def calculate_travel_time(
        self,
        distance_km: float,
        mode: str = 'driving'
    ) -> Dict:
        """Estimate travel time based on distance and mode."""
        speeds = {
            'driving': 60,
            'car': 60,
            'walking': 5,
            'foot': 5,
            'cycling': 15,
            'bike': 15
        }
        
        avg_speed = speeds.get(mode.lower(), 60)
        hours = distance_km / avg_speed
        
        return {
            'mode': mode,
            'distance_km': round(distance_km, 2),
            'estimated_hours': round(hours, 2),
            'estimated_minutes': round(hours * 60, 2),
            'average_speed_kmh': avg_speed
        }


if __name__ == "__main__":
    print("✅ OSRM Service - Ready for free routing!")