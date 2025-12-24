"""
OSRM Route Optimizer - FIXED VERSION
FREE routing service - no API key required
CRITICAL: Uses LONGITUDE,LATITUDE order (NOT lat,lon)
"""

import requests
from typing import Dict, List, Optional, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OSRMOptimizer:
    """
    Interface for OSRM (Open Source Routing Machine) API
    Provides route optimization and distance calculations
    
    IMPORTANT: OSRM uses LONGITUDE,LATITUDE order!
    """
    
    def __init__(self):
        """Initialize OSRM optimizer"""
        self.base_url = "https://router.project-osrm.org"
        logger.info("OSRM Optimizer initialized")
        
    def get_route(self, start: Tuple[float, float], end: Tuple[float, float],
                  profile: str = 'driving') -> Optional[Dict]:
        """
        Get route between two points
        
        Args:
            start: Starting coordinates (latitude, longitude)
            end: Ending coordinates (latitude, longitude)
            profile: Transportation profile ('driving', 'walking', 'cycling')
            
        Returns:
            Dictionary with route information
            
        CRITICAL: Input is (lat, lon) but OSRM needs (lon, lat)!
        """
        # FIXED: Convert (lat, lon) to (lon, lat) for OSRM
        start_lat, start_lon = start
        end_lat, end_lon = end
        
        # OSRM format: longitude,latitude;longitude,latitude
        coords = f"{start_lon},{start_lat};{end_lon},{end_lat}"
        
        url = f"{self.base_url}/route/v1/{profile}/{coords}"
        
        params = {
            'overview': 'full',
            'geometries': 'geojson',
            'steps': 'true'
        }
        
        try:
            logger.info(f"Requesting route from ({start_lat},{start_lon}) to ({end_lat},{end_lon})")
            logger.info(f"OSRM coords (lon,lat format): {coords}")
            response = requests.get(url, params=params, timeout=15)
            
            logger.info(f"Response status: {response.status_code}")
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('code') != 'Ok':
                logger.error(f"OSRM error: {data.get('message', 'Unknown error')}")
                return None
                
            route = data['routes'][0]
            
            return {
                'distance_meters': route['distance'],
                'distance_km': round(route['distance'] / 1000, 2),
                'duration_seconds': route['duration'],
                'duration_minutes': round(route['duration'] / 60, 1),
                'duration_min': round(route['duration'] / 60, 1),  # Alias for compatibility
                'duration_hours': round(route['duration'] / 3600, 2),
                'geometry': route['geometry'],
                'steps': self._format_steps(route.get('legs', [{}])[0].get('steps', [])),
                'start_point': {'latitude': start_lat, 'longitude': start_lon},
                'end_point': {'latitude': end_lat, 'longitude': end_lon},
                'profile': profile
            }
            
        except requests.exceptions.HTTPError as e:
            logger.error(f"❌ HTTP error: {e}")
            logger.error(f"URL used: {url}")
            return None
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Error getting route: {str(e)}")
            return None
            
    def get_route_multiple_points(self, waypoints: List[Tuple[float, float]],
                                  profile: str = 'driving') -> Optional[Dict]:
        """
        Get route through multiple waypoints
        
        Args:
            waypoints: List of (latitude, longitude) tuples
            profile: Transportation profile
            
        Returns:
            Dictionary with route information
        """
        if len(waypoints) < 2:
            logger.error("Need at least 2 waypoints")
            return None
            
        # FIXED: Convert all (lat, lon) to (lon, lat) for OSRM
        coords_list = []
        for lat, lon in waypoints:
            coords_list.append(f"{lon},{lat}")
            
        coords = ";".join(coords_list)
        
        url = f"{self.base_url}/route/v1/{profile}/{coords}"
        
        params = {
            'overview': 'full',
            'geometries': 'geojson'
        }
        
        try:
            logger.info(f"Requesting multi-point route with {len(waypoints)} waypoints")
            response = requests.get(url, params=params, timeout=20)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('code') != 'Ok':
                logger.error(f"OSRM error: {data.get('message')}")
                return None
                
            route = data['routes'][0]
            
            return {
                'distance_meters': route['distance'],
                'distance_km': round(route['distance'] / 1000, 2),
                'duration_seconds': route['duration'],
                'duration_minutes': round(route['duration'] / 60, 1),
                'duration_hours': round(route['duration'] / 3600, 2),
                'geometry': route['geometry'],
                'waypoints': [{'latitude': lat, 'longitude': lon} for lat, lon in waypoints],
                'num_waypoints': len(waypoints),
                'profile': profile
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting multi-point route: {str(e)}")
            return None
            
    def optimize_trip(self, waypoints: List[Tuple[float, float]],
                     start_index: int = 0, end_index: Optional[int] = None,
                     profile: str = 'driving') -> Optional[Dict]:
        """
        Optimize order of waypoints for shortest route (Traveling Salesman Problem)
        
        Args:
            waypoints: List of (latitude, longitude) tuples
            start_index: Index of starting point (default: 0)
            end_index: Index of ending point (default: same as start)
            profile: Transportation profile
            
        Returns:
            Dictionary with optimized route
        """
        if len(waypoints) < 2:
            logger.error("Need at least 2 waypoints")
            return None
            
        # FIXED: Convert (lat, lon) to (lon, lat)
        coords_list = []
        for lat, lon in waypoints:
            coords_list.append(f"{lon},{lat}")
            
        coords = ";".join(coords_list)
        
        # Set source and destination
        source = start_index
        destination = end_index if end_index is not None else start_index
        
        url = f"{self.base_url}/trip/v1/{profile}/{coords}"
        
        params = {
            'source': source,
            'destination': destination,
            'roundtrip': 'false' if end_index is not None else 'true',
            'overview': 'full',
            'geometries': 'geojson'
        }
        
        try:
            logger.info(f"Optimizing trip with {len(waypoints)} waypoints")
            response = requests.get(url, params=params, timeout=20)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('code') != 'Ok':
                logger.error(f"OSRM error: {data.get('message')}")
                return None
                
            trip = data['trips'][0]
            
            # Get optimized order
            waypoint_indices = [wp['waypoint_index'] for wp in data['waypoints']]
            optimized_waypoints = [waypoints[i] for i in waypoint_indices]
            
            return {
                'distance_meters': trip['distance'],
                'distance_km': round(trip['distance'] / 1000, 2),
                'duration_seconds': trip['duration'],
                'duration_minutes': round(trip['duration'] / 60, 1),
                'duration_hours': round(trip['duration'] / 3600, 2),
                'geometry': trip['geometry'],
                'original_waypoints': waypoints,
                'optimized_waypoints': optimized_waypoints,
                'optimized_order': waypoint_indices,
                'profile': profile
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error optimizing trip: {str(e)}")
            return None
            
    def get_distance_matrix(self, locations: List[Tuple[float, float]],
                           profile: str = 'driving') -> Optional[Dict]:
        """
        Get distance matrix between multiple locations
        
        Args:
            locations: List of (latitude, longitude) tuples
            profile: Transportation profile
            
        Returns:
            Dictionary with distance matrix
        """
        if len(locations) < 2:
            logger.error("Need at least 2 locations")
            return None
            
        # FIXED: Convert (lat, lon) to (lon, lat)
        coords_list = []
        for lat, lon in locations:
            coords_list.append(f"{lon},{lat}")
            
        coords = ";".join(coords_list)
        
        url = f"{self.base_url}/table/v1/{profile}/{coords}"
        
        try:
            logger.info(f"Getting distance matrix for {len(locations)} locations")
            response = requests.get(url, timeout=20)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('code') != 'Ok':
                logger.error(f"OSRM error: {data.get('message')}")
                return None
                
            return {
                'distances': data['distances'],  # Matrix in meters
                'durations': data['durations'],  # Matrix in seconds
                'locations': [{'latitude': lat, 'longitude': lon} for lat, lon in locations],
                'profile': profile
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting distance matrix: {str(e)}")
            return None
            
    def _format_steps(self, steps: List[Dict]) -> List[Dict]:
        """Format navigation steps"""
        formatted = []
        
        for step in steps:
            formatted.append({
                'instruction': step.get('maneuver', {}).get('instruction', ''),
                'distance_meters': step.get('distance', 0),
                'duration_seconds': step.get('duration', 0),
                'type': step.get('maneuver', {}).get('type', ''),
                'modifier': step.get('maneuver', {}).get('modifier')
            })
            
        return formatted
        
    def get_nearest_road(self, location: Tuple[float, float],
                        profile: str = 'driving') -> Optional[Dict]:
        """
        Snap a coordinate to the nearest road
        
        Args:
            location: (latitude, longitude) tuple
            profile: Transportation profile
            
        Returns:
            Dictionary with snapped location
        """
        lat, lon = location
        
        # FIXED: Use (lon, lat) for OSRM
        coords = f"{lon},{lat}"
        
        url = f"{self.base_url}/nearest/v1/{profile}/{coords}"
        
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('code') != 'Ok':
                return None
                
            waypoint = data['waypoints'][0]
            snapped_lon, snapped_lat = waypoint['location']
            
            return {
                'original': {'latitude': lat, 'longitude': lon},
                'snapped': {'latitude': snapped_lat, 'longitude': snapped_lon},
                'distance_to_road': waypoint.get('distance', 0),
                'name': waypoint.get('name')
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error finding nearest road: {str(e)}")
            return None


if __name__ == "__main__":
    # Test the optimizer
    optimizer = OSRMOptimizer()
    
    print("=" * 60)
    print("Testing OSRM Route Optimizer - FIXED VERSION")
    print("=" * 60)
    
    # Test 1: Simple route (Paris to Eiffel Tower)
    print("\n1. Getting route: Paris center to Eiffel Tower...")
    print("   Coordinates: (48.8566, 2.3522) to (48.8584, 2.2945)")
    route = optimizer.get_route(
        (48.8566, 2.3522),  # Paris center (lat, lon)
        (48.8584, 2.2945)   # Eiffel Tower (lat, lon)
    )
    if route:
        print(f"   ✅ Distance: {route['distance_km']} km")
        print(f"   Duration: {route['duration_minutes']} minutes")
    else:
        print("   ❌ Failed to get route")
    
    # Test 2: Multi-point route
    print("\n2. Getting route through 3 points...")
    waypoints = [
        (48.8566, 2.3522),  # Paris
        (48.8584, 2.2945),  # Eiffel Tower
        (48.8606, 2.3376)   # Louvre
    ]
    multi_route = optimizer.get_route_multiple_points(waypoints)
    if multi_route:
        print(f"   ✅ Total distance: {multi_route['distance_km']} km")
        print(f"   Total duration: {multi_route['duration_minutes']} minutes")
    else:
        print("   ❌ Failed to get multi-point route")
    
    # Test 3: Trip optimization
    print("\n3. Optimizing trip order...")
    optimized = optimizer.optimize_trip(waypoints)
    if optimized:
        print(f"   ✅ Optimized distance: {optimized['distance_km']} km")
        print(f"   Optimized order: {optimized['optimized_order']}")
    else:
        print("   ❌ Failed to optimize trip")
    
    # Test 4: Distance matrix
    print("\n4. Getting distance matrix...")
    matrix = optimizer.get_distance_matrix(waypoints[:2])
    if matrix:
        print(f"   ✅ Matrix calculated for {len(waypoints[:2])} locations")
    else:
        print("   ❌ Failed to get matrix")
    
    print("\n" + "=" * 60)
    print("✅ All tests completed!")
    print("=" * 60)
    print("\n💡 KEY POINT: OSRM uses LONGITUDE,LATITUDE order!")
    print("   Input as (lat, lon) → Converted to (lon, lat) internally")