"""
Nominatim Geocoding Service (OpenStreetMap)
FREE geocoding service - no API key required
"""

import requests
import time
from typing import Dict, List, Optional, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NominatimGeocoder:
    """
    Free geocoding service using OpenStreetMap's Nominatim API
    Converts addresses to coordinates and vice versa
    """
    
    def __init__(self, user_agent: str = "TripPlannerML/1.0"):
        """
        Initialize the Nominatim geocoder
        
        Args:
            user_agent: User agent string for API requests (required by Nominatim)
        """
        self.base_url = "https://nominatim.openstreetmap.org"
        self.user_agent = user_agent
        self.last_request_time = 0
        self.min_request_interval = 1.0  # Nominatim requires 1 second between requests
        
    def _wait_for_rate_limit(self):
        """Ensure we respect Nominatim's rate limit (1 request per second)"""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        
        if time_since_last_request < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last_request
            time.sleep(sleep_time)
            
        self.last_request_time = time.time()
        
    def geocode(self, address: str, country_code: Optional[str] = None) -> Optional[Dict]:
        """
        Convert address to geographic coordinates
        
        Args:
            address: Address or place name to geocode
            country_code: Optional 2-letter country code to limit search (e.g., 'US', 'FR')
            
        Returns:
            Dictionary with coordinates and address details, or None if not found
        """
        self._wait_for_rate_limit()
        
        params = {
            'q': address,
            'format': 'json',
            'addressdetails': 1,
            'limit': 1
        }
        
        if country_code:
            params['countrycodes'] = country_code.lower()
            
        headers = {
            'User-Agent': self.user_agent
        }
        
        try:
            response = requests.get(
                f"{self.base_url}/search",
                params=params,
                headers=headers,
                timeout=10
            )
            response.raise_for_status()
            
            results = response.json()
            
            if not results:
                logger.warning(f"No results found for address: {address}")
                return None
                
            result = results[0]
            
            return {
                'latitude': float(result['lat']),
                'longitude': float(result['lon']),
                'display_name': result['display_name'],
                'address': result.get('address', {}),
                'importance': float(result.get('importance', 0)),
                'place_id': result.get('place_id'),
                'osm_type': result.get('osm_type'),
                'osm_id': result.get('osm_id'),
                'type': result.get('type'),
                'class': result.get('class')
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error geocoding address '{address}': {str(e)}")
            return None
            
    def reverse_geocode(self, latitude: float, longitude: float) -> Optional[Dict]:
        """
        Convert coordinates to address
        
        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            
        Returns:
            Dictionary with address details, or None if not found
        """
        self._wait_for_rate_limit()
        
        params = {
            'lat': latitude,
            'lon': longitude,
            'format': 'json',
            'addressdetails': 1
        }
        
        headers = {
            'User-Agent': self.user_agent
        }
        
        try:
            response = requests.get(
                f"{self.base_url}/reverse",
                params=params,
                headers=headers,
                timeout=10
            )
            response.raise_for_status()
            
            result = response.json()
            
            if 'error' in result:
                logger.warning(f"No address found for coordinates: ({latitude}, {longitude})")
                return None
                
            return {
                'display_name': result['display_name'],
                'address': result.get('address', {}),
                'latitude': float(result['lat']),
                'longitude': float(result['lon']),
                'place_id': result.get('place_id'),
                'osm_type': result.get('osm_type'),
                'osm_id': result.get('osm_id')
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error reverse geocoding ({latitude}, {longitude}): {str(e)}")
            return None
            
    def search_nearby(self, latitude: float, longitude: float, 
                     query: str, radius_km: float = 5.0) -> List[Dict]:
        """
        Search for places near a location
        
        Args:
            latitude: Center latitude
            longitude: Center longitude
            query: Search query (e.g., 'restaurant', 'museum')
            radius_km: Search radius in kilometers
            
        Returns:
            List of nearby places
        """
        self._wait_for_rate_limit()
        
        # Calculate bounding box (approximate)
        lat_delta = radius_km / 111.0  # 1 degree latitude ≈ 111 km
        lon_delta = radius_km / (111.0 * abs(float(latitude)) if latitude != 0 else 111.0)
        
        params = {
            'q': query,
            'format': 'json',
            'addressdetails': 1,
            'limit': 20,
            'viewbox': f"{longitude - lon_delta},{latitude + lat_delta},"
                      f"{longitude + lon_delta},{latitude - lat_delta}",
            'bounded': 1
        }
        
        headers = {
            'User-Agent': self.user_agent
        }
        
        try:
            response = requests.get(
                f"{self.base_url}/search",
                params=params,
                headers=headers,
                timeout=10
            )
            response.raise_for_status()
            
            results = response.json()
            
            places = []
            for result in results:
                places.append({
                    'name': result.get('display_name'),
                    'latitude': float(result['lat']),
                    'longitude': float(result['lon']),
                    'address': result.get('address', {}),
                    'importance': float(result.get('importance', 0)),
                    'place_id': result.get('place_id'),
                    'type': result.get('type'),
                    'category': result.get('class')
                })
                
            logger.info(f"Found {len(places)} places near ({latitude}, {longitude})")
            return places
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error searching nearby: {str(e)}")
            return []
            
    def get_city_info(self, city_name: str, country_code: Optional[str] = None) -> Optional[Dict]:
        """
        Get detailed information about a city
        
        Args:
            city_name: Name of the city
            country_code: Optional 2-letter country code
            
        Returns:
            Dictionary with city information
        """
        result = self.geocode(city_name, country_code)
        
        if not result:
            return None
            
        address = result.get('address', {})
        
        return {
            'name': city_name,
            'display_name': result['display_name'],
            'latitude': result['latitude'],
            'longitude': result['longitude'],
            'country': address.get('country'),
            'country_code': address.get('country_code', '').upper(),
            'state': address.get('state'),
            'county': address.get('county'),
            'importance': result['importance'],
            'place_id': result['place_id'],
            'type': result.get('type'),
            'postcode': address.get('postcode')
        }
        
    def batch_geocode(self, addresses: List[str], 
                     delay: float = 1.0) -> List[Optional[Dict]]:
        """
        Geocode multiple addresses (respecting rate limits)
        
        Args:
            addresses: List of addresses to geocode
            delay: Delay between requests in seconds (minimum 1.0)
            
        Returns:
            List of geocoding results (None for failed addresses)
        """
        if delay < 1.0:
            logger.warning("Delay must be at least 1.0 seconds for Nominatim")
            delay = 1.0
            
        results = []
        
        for i, address in enumerate(addresses):
            logger.info(f"Geocoding {i+1}/{len(addresses)}: {address}")
            result = self.geocode(address)
            results.append(result)
            
            if i < len(addresses) - 1:
                time.sleep(delay)
                
        return results
        
    def get_coordinates(self, location: str) -> Optional[Tuple[float, float]]:
        """
        Simple helper to get just the coordinates for a location
        
        Args:
            location: Location name or address
            
        Returns:
            Tuple of (latitude, longitude) or None if not found
        """
        result = self.geocode(location)
        
        if result:
            return (result['latitude'], result['longitude'])
        return None
        
    def search_places_by_type(self, place_type: str, city: str, 
                             country_code: Optional[str] = None) -> List[Dict]:
        """
        Search for specific types of places in a city
        
        Args:
            place_type: Type of place (e.g., 'hotel', 'restaurant', 'museum', 'park')
            city: City name
            country_code: Optional country code
            
        Returns:
            List of places
        """
        # First get city coordinates
        city_info = self.get_city_info(city, country_code)
        
        if not city_info:
            logger.error(f"Could not find city: {city}")
            return []
            
        # Search nearby
        return self.search_nearby(
            city_info['latitude'],
            city_info['longitude'],
            place_type,
            radius_km=10.0
        )
        
    def calculate_distance(self, coord1: Tuple[float, float], 
                          coord2: Tuple[float, float]) -> float:
        """
        Calculate approximate distance between two coordinates (Haversine formula)
        
        Args:
            coord1: First coordinate (latitude, longitude)
            coord2: Second coordinate (latitude, longitude)
            
        Returns:
            Distance in kilometers
        """
        import math
        
        lat1, lon1 = coord1
        lat2, lon2 = coord2
        
        R = 6371  # Earth's radius in kilometers
        
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        
        a = (math.sin(dlat / 2) ** 2 + 
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * 
             math.sin(dlon / 2) ** 2)
        
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        distance = R * c
        
        return distance
        
    def get_address_components(self, address: str) -> Optional[Dict]:
        """
        Extract detailed address components
        
        Args:
            address: Address string
            
        Returns:
            Dictionary with structured address components
        """
        result = self.geocode(address)
        
        if not result:
            return None
            
        addr = result.get('address', {})
        
        return {
            'street': addr.get('road'),
            'house_number': addr.get('house_number'),
            'city': addr.get('city') or addr.get('town') or addr.get('village'),
            'state': addr.get('state'),
            'postcode': addr.get('postcode'),
            'country': addr.get('country'),
            'country_code': addr.get('country_code', '').upper(),
            'suburb': addr.get('suburb'),
            'neighbourhood': addr.get('neighbourhood'),
            'full_address': result['display_name']
        }


if __name__ == "__main__":
    # Test the geocoder
    geocoder = NominatimGeocoder()
    
    print("=" * 60)
    print("Testing Nominatim Geocoding Service")
    print("=" * 60)
    
    # Test 1: Geocode a famous location
    print("\n1. Geocoding 'Eiffel Tower, Paris'...")
    result = geocoder.geocode("Eiffel Tower, Paris")
    if result:
        print(f"   ✅ Found: {result['display_name']}")
        print(f"   Coordinates: ({result['latitude']}, {result['longitude']})")
        print(f"   Type: {result.get('type')}")
    
    # Test 2: Reverse geocode
    print("\n2. Reverse geocoding (48.8584, 2.2945)...")
    result = geocoder.reverse_geocode(48.8584, 2.2945)
    if result:
        print(f"   ✅ Found: {result['display_name']}")
        addr = result.get('address', {})
        print(f"   City: {addr.get('city', 'N/A')}")
    
    # Test 3: Get city info
    print("\n3. Getting city info for 'Tokyo, Japan'...")
    result = geocoder.get_city_info("Tokyo", "JP")
    if result:
        print(f"   ✅ City: {result['name']}")
        print(f"   Country: {result['country']}")
        print(f"   Coordinates: ({result['latitude']}, {result['longitude']})")
    
    # Test 4: Search nearby
    print("\n4. Searching for restaurants near Eiffel Tower...")
    places = geocoder.search_nearby(48.8584, 2.2945, "restaurant", radius_km=1.0)
    print(f"   ✅ Found {len(places)} restaurants nearby")
    if places:
        print(f"   First result: {places[0]['name']}")
    
    # Test 5: Get address components
    print("\n5. Extracting address components...")
    components = geocoder.get_address_components("10 Downing Street, London")
    if components:
        print(f"   ✅ Street: {components.get('street')}")
        print(f"   City: {components.get('city')}")
        print(f"   Country: {components.get('country')}")
    
    # Test 6: Calculate distance
    print("\n6. Calculating distance between Paris and London...")
    paris = (48.8566, 2.3522)
    london = (51.5074, -0.1278)
    distance = geocoder.calculate_distance(paris, london)
    print(f"   ✅ Distance: {distance:.2f} km")
    
    print("\n" + "=" * 60)
    print("✅ All tests completed!")
    print("=" * 60)