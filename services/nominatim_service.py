"""
Nominatim Location Services
High-level services using Nominatim geocoder for trip planning
"""

from typing import Dict, List, Optional, Tuple
import logging
from nominatim_geocoder import NominatimGeocoder

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NominatimService:
    """
    High-level location services for trip planning
    Uses Nominatim geocoder for various travel-related queries
    """
    
    def __init__(self):
        """Initialize the Nominatim service"""
        self.geocoder = NominatimGeocoder()
        
    def find_destination(self, destination: str) -> Optional[Dict]:
        """
        Find and validate a travel destination
        
        Args:
            destination: Destination name (city, landmark, etc.)
            
        Returns:
            Dictionary with destination details
        """
        result = self.geocoder.geocode(destination)
        
        if not result:
            logger.warning(f"Destination not found: {destination}")
            return None
            
        address = result.get('address', {})
        
        return {
            'name': destination,
            'display_name': result['display_name'],
            'coordinates': {
                'latitude': result['latitude'],
                'longitude': result['longitude']
            },
            'city': address.get('city') or address.get('town') or address.get('village'),
            'state': address.get('state'),
            'country': address.get('country'),
            'country_code': address.get('country_code', '').upper(),
            'type': result.get('type'),
            'importance': result['importance']
        }
        
    def find_attractions(self, city: str, country_code: Optional[str] = None,
                        attraction_type: str = 'tourism') -> List[Dict]:
        """
        Find tourist attractions in a city
        
        Args:
            city: City name
            country_code: Optional country code
            attraction_type: Type of attraction ('tourism', 'museum', 'monument', etc.)
            
        Returns:
            List of attractions with details
        """
        city_info = self.geocoder.get_city_info(city, country_code)
        
        if not city_info:
            logger.error(f"City not found: {city}")
            return []
            
        # Search for attractions
        attractions = self.geocoder.search_nearby(
            city_info['latitude'],
            city_info['longitude'],
            attraction_type,
            radius_km=10.0
        )
        
        # Enrich with distance from city center
        city_coords = (city_info['latitude'], city_info['longitude'])
        
        for attraction in attractions:
            attr_coords = (attraction['latitude'], attraction['longitude'])
            attraction['distance_from_center'] = self.geocoder.calculate_distance(
                city_coords, 
                attr_coords
            )
            
        # Sort by distance
        attractions.sort(key=lambda x: x['distance_from_center'])
        
        logger.info(f"Found {len(attractions)} attractions in {city}")
        return attractions
        
    def find_hotels(self, city: str, country_code: Optional[str] = None) -> List[Dict]:
        """
        Find hotels in a city
        
        Args:
            city: City name
            country_code: Optional country code
            
        Returns:
            List of hotels
        """
        return self.geocoder.search_places_by_type('hotel', city, country_code)
        
    def find_restaurants(self, city: str, country_code: Optional[str] = None) -> List[Dict]:
        """
        Find restaurants in a city
        
        Args:
            city: City name
            country_code: Optional country code
            
        Returns:
            List of restaurants
        """
        return self.geocoder.search_places_by_type('restaurant', city, country_code)
        
    def find_museums(self, city: str, country_code: Optional[str] = None) -> List[Dict]:
        """
        Find museums in a city
        
        Args:
            city: City name
            country_code: Optional country code
            
        Returns:
            List of museums
        """
        return self.geocoder.search_places_by_type('museum', city, country_code)
        
    def find_parks(self, city: str, country_code: Optional[str] = None) -> List[Dict]:
        """
        Find parks and green spaces in a city
        
        Args:
            city: City name
            country_code: Optional country code
            
        Returns:
            List of parks
        """
        return self.geocoder.search_places_by_type('park', city, country_code)
        
    def plan_route_between_cities(self, origin: str, destination: str) -> Optional[Dict]:
        """
        Get basic route information between two cities
        
        Args:
            origin: Origin city
            destination: Destination city
            
        Returns:
            Dictionary with route information
        """
        origin_info = self.find_destination(origin)
        dest_info = self.find_destination(destination)
        
        if not origin_info or not dest_info:
            return None
            
        origin_coords = (origin_info['coordinates']['latitude'], 
                        origin_info['coordinates']['longitude'])
        dest_coords = (dest_info['coordinates']['latitude'],
                      dest_info['coordinates']['longitude'])
        
        distance = self.geocoder.calculate_distance(origin_coords, dest_coords)
        
        return {
            'origin': origin_info,
            'destination': dest_info,
            'straight_line_distance_km': round(distance, 2),
            'estimated_driving_distance_km': round(distance * 1.3, 2),  # Approximate
            'estimated_driving_hours': round((distance * 1.3) / 80, 1),  # Assuming 80 km/h avg
            'estimated_flight_hours': round(distance / 800, 1)  # Assuming 800 km/h
        }
        
    def find_points_of_interest(self, city: str, interests: List[str],
                               country_code: Optional[str] = None) -> Dict[str, List[Dict]]:
        """
        Find points of interest based on user interests
        
        Args:
            city: City name
            interests: List of interest types (e.g., ['museum', 'restaurant', 'park'])
            country_code: Optional country code
            
        Returns:
            Dictionary mapping interest types to lists of places
        """
        results = {}
        
        for interest in interests:
            places = self.geocoder.search_places_by_type(interest, city, country_code)
            results[interest] = places[:10]  # Limit to top 10
            
        return results
        
    def get_nearby_cities(self, city: str, radius_km: float = 100.0,
                         country_code: Optional[str] = None) -> List[Dict]:
        """
        Find cities near a given city
        
        Args:
            city: City name
            radius_km: Search radius in kilometers
            country_code: Optional country code
            
        Returns:
            List of nearby cities
        """
        city_info = self.geocoder.get_city_info(city, country_code)
        
        if not city_info:
            return []
            
        # Search for cities/towns nearby
        nearby = self.geocoder.search_nearby(
            city_info['latitude'],
            city_info['longitude'],
            'city',
            radius_km=radius_km
        )
        
        # Filter out the original city and calculate distances
        city_coords = (city_info['latitude'], city_info['longitude'])
        nearby_cities = []
        
        for place in nearby:
            place_name = place['address'].get('city') or place['address'].get('town')
            
            if place_name and place_name.lower() != city.lower():
                place_coords = (place['latitude'], place['longitude'])
                distance = self.geocoder.calculate_distance(city_coords, place_coords)
                
                nearby_cities.append({
                    'name': place_name,
                    'distance_km': round(distance, 2),
                    'coordinates': {
                        'latitude': place['latitude'],
                        'longitude': place['longitude']
                    },
                    'country': place['address'].get('country')
                })
                
        # Sort by distance
        nearby_cities.sort(key=lambda x: x['distance_km'])
        
        return nearby_cities
        
    def validate_address(self, address: str) -> Dict:
        """
        Validate and standardize an address
        
        Args:
            address: Address to validate
            
        Returns:
            Dictionary with validation result and standardized address
        """
        result = self.geocoder.geocode(address)
        
        if not result:
            return {
                'valid': False,
                'message': 'Address could not be found',
                'original': address
            }
            
        components = self.geocoder.get_address_components(address)
        
        return {
            'valid': True,
            'message': 'Address validated successfully',
            'original': address,
            'standardized': result['display_name'],
            'components': components,
            'coordinates': {
                'latitude': result['latitude'],
                'longitude': result['longitude']
            }
        }
        
    def get_location_context(self, latitude: float, longitude: float) -> Optional[Dict]:
        """
        Get contextual information about a location
        
        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            
        Returns:
            Dictionary with location context
        """
        result = self.geocoder.reverse_geocode(latitude, longitude)
        
        if not result:
            return None
            
        address = result.get('address', {})
        
        return {
            'display_name': result['display_name'],
            'city': address.get('city') or address.get('town') or address.get('village'),
            'state': address.get('state'),
            'country': address.get('country'),
            'country_code': address.get('country_code', '').upper(),
            'postcode': address.get('postcode'),
            'neighbourhood': address.get('neighbourhood'),
            'suburb': address.get('suburb'),
            'coordinates': {
                'latitude': result['latitude'],
                'longitude': result['longitude']
            }
        }
        
    def search_accommodation(self, city: str, accommodation_type: str = 'hotel',
                           country_code: Optional[str] = None) -> List[Dict]:
        """
        Search for accommodation in a city
        
        Args:
            city: City name
            accommodation_type: Type of accommodation ('hotel', 'hostel', 'guesthouse')
            country_code: Optional country code
            
        Returns:
            List of accommodation options
        """
        places = self.geocoder.search_places_by_type(accommodation_type, city, country_code)
        
        # Enrich with basic info
        for place in places:
            addr = place.get('address', {})
            place['city'] = addr.get('city') or addr.get('town')
            place['street'] = addr.get('road')
            place['postcode'] = addr.get('postcode')
            
        return places
        
    def calculate_travel_distance(self, waypoints: List[str]) -> Optional[Dict]:
        """
        Calculate total travel distance for multiple waypoints
        
        Args:
            waypoints: List of location names
            
        Returns:
            Dictionary with distance information
        """
        if len(waypoints) < 2:
            return None
            
        # Geocode all waypoints
        coordinates = []
        locations = []
        
        for waypoint in waypoints:
            result = self.find_destination(waypoint)
            if result:
                coordinates.append((
                    result['coordinates']['latitude'],
                    result['coordinates']['longitude']
                ))
                locations.append(result)
            else:
                logger.warning(f"Could not find waypoint: {waypoint}")
                
        if len(coordinates) < 2:
            return None
            
        # Calculate distances between consecutive points
        total_distance = 0
        segments = []
        
        for i in range(len(coordinates) - 1):
            distance = self.geocoder.calculate_distance(coordinates[i], coordinates[i + 1])
            total_distance += distance
            
            segments.append({
                'from': locations[i]['name'],
                'to': locations[i + 1]['name'],
                'distance_km': round(distance, 2)
            })
            
        return {
            'waypoints': waypoints,
            'total_distance_km': round(total_distance, 2),
            'segments': segments,
            'estimated_driving_hours': round(total_distance / 80, 1),
            'number_of_stops': len(waypoints)
        }
        
    def find_central_location(self, cities: List[str]) -> Optional[Dict]:
        """
        Find a central point between multiple cities
        
        Args:
            cities: List of city names
            
        Returns:
            Dictionary with central location information
        """
        if not cities:
            return None
            
        # Geocode all cities
        coordinates = []
        valid_cities = []
        
        for city in cities:
            result = self.find_destination(city)
            if result:
                coordinates.append((
                    result['coordinates']['latitude'],
                    result['coordinates']['longitude']
                ))
                valid_cities.append(city)
                
        if not coordinates:
            return None
            
        # Calculate center point (simple average)
        avg_lat = sum(coord[0] for coord in coordinates) / len(coordinates)
        avg_lon = sum(coord[1] for coord in coordinates) / len(coordinates)
        
        # Find nearest city to center point
        center_location = self.get_location_context(avg_lat, avg_lon)
        
        return {
            'cities': valid_cities,
            'center_coordinates': {
                'latitude': round(avg_lat, 6),
                'longitude': round(avg_lon, 6)
            },
            'nearest_location': center_location,
            'number_of_cities': len(valid_cities)
        }


if __name__ == "__main__":
    # Test the service
    service = NominatimService()
    
    print("=" * 60)
    print("Testing Nominatim Location Services")
    print("=" * 60)
    
    # Test 1: Find destination
    print("\n1. Finding destination: Paris, France")
    dest = service.find_destination("Paris, France")
    if dest:
        print(f"   ✅ Found: {dest['display_name']}")
        print(f"   Coordinates: {dest['coordinates']}")
    
    # Test 2: Find attractions
    print("\n2. Finding attractions in Paris...")
    attractions = service.find_attractions("Paris", "FR")
    print(f"   ✅ Found {len(attractions)} attractions")
    if attractions:
        print(f"   Top attraction: {attractions[0]['name']}")
    
    # Test 3: Find hotels
    print("\n3. Finding hotels in Tokyo...")
    hotels = service.find_hotels("Tokyo", "JP")
    print(f"   ✅ Found {len(hotels)} hotels")
    
    # Test 4: Plan route between cities
    print("\n4. Planning route: Paris to London...")
    route = service.plan_route_between_cities("Paris", "London")
    if route:
        print(f"   ✅ Distance: {route['straight_line_distance_km']} km")
        print(f"   Estimated driving: {route['estimated_driving_hours']} hours")
    
    # Test 5: Find nearby cities
    print("\n5. Finding cities near Paris (50km radius)...")
    nearby = service.get_nearby_cities("Paris", radius_km=50, country_code="FR")
    print(f"   ✅ Found {len(nearby)} nearby cities")
    if nearby:
        print(f"   Nearest: {nearby[0]['name']} ({nearby[0]['distance_km']} km)")
    
    # Test 6: Points of interest
    print("\n6. Finding points of interest in Rome...")
    interests = ['museum', 'restaurant', 'park']
    poi = service.find_points_of_interest("Rome", interests, "IT")
    print(f"   ✅ Found:")
    for interest, places in poi.items():
        print(f"      {interest}: {len(places)} places")
    
    # Test 7: Calculate multi-city travel
    print("\n7. Calculating travel distance for multi-city trip...")
    waypoints = ["Paris", "Brussels", "Amsterdam", "Berlin"]
    travel = service.calculate_travel_distance(waypoints)
    if travel:
        print(f"   ✅ Total distance: {travel['total_distance_km']} km")
        print(f"   Estimated driving: {travel['estimated_driving_hours']} hours")
    
    print("\n" + "=" * 60)
    print("✅ All service tests completed!")
    print("=" * 60)