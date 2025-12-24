"""
models/location/resolver.py
Location Hierarchy Resolver (Country → State → City)
Handles location validation and resolution using free services
"""

import sys
import os
from typing import Dict, List, Optional, Tuple

# Add parent directories to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from services.nominatim_service import NominatimService


class LocationResolver:
    """
    Resolve and validate location hierarchy: Country → State → City.
    Provides bounding boxes for place searches.
    """
    
    def __init__(self):
        """Initialize location resolver with Nominatim service."""
        self.nominatim = NominatimService()
        self.cache = {}  # Simple in-memory cache
    
    def resolve_location(
        self,
        country: str,
        state: Optional[str] = None,
        city: Optional[str] = None
    ) -> Dict:
        """
        Resolve location hierarchy and get search boundary.
        
        Args:
            country: Country name (required)
            state: State/province name (optional)
            city: City name (optional)
            
        Returns:
            Dictionary with location info and search boundaries
        """
        # Build cache key
        cache_key = f"{country}|{state}|{city}"
        
        # Check cache
        if cache_key in self.cache:
            print(f"📦 Using cached location data for: {cache_key}")
            return self.cache[cache_key]
        
        # Validate location with Nominatim
        print(f"🔍 Resolving location: {self._format_location_string(country, state, city)}")
        
        validation = self.nominatim.validate_location(
            country=country,
            state=state,
            city=city
        )
        
        if not validation['valid']:
            return {
                'success': False,
                'error': validation['error'],
                'message': f"Could not find location: {validation['query']}"
            }
        
        # Determine search scope
        search_scope = self._determine_search_scope(country, state, city)
        
        # Build result
        result = {
            'success': True,
            'query': validation['query'],
            'display_name': validation['display_name'],
            'search_scope': search_scope,
            'coordinates': validation['coordinates'],
            'bounding_box': validation['bounding_box'],
            'resolved_address': validation['resolved_address'],
            'location_type': validation['type'],
            'hierarchy': {
                'country': country,
                'state': state,
                'city': city
            }
        }
        
        # Cache result
        self.cache[cache_key] = result
        
        return result
    
    def get_search_area(
        self,
        country: str,
        state: Optional[str] = None,
        city: Optional[str] = None
    ) -> Optional[Dict]:
        """
        Get search area (bounding box) for place queries.
        
        Args:
            country: Country name
            state: State name (optional)
            city: City name (optional)
            
        Returns:
            Bounding box coordinates for Overpass queries
        """
        resolution = self.resolve_location(country, state, city)
        
        if not resolution['success']:
            return None
        
        bbox = resolution['bounding_box']
        
        return {
            'south': bbox['south'],
            'north': bbox['north'],
            'west': bbox['west'],
            'east': bbox['east'],
            'center_lat': resolution['coordinates']['lat'],
            'center_lon': resolution['coordinates']['lon'],
            'area_name': resolution['display_name']
        }
    
    def get_area_for_overpass(
        self,
        country: str,
        state: Optional[str] = None,
        city: Optional[str] = None
    ) -> str:
        """
        Get area name formatted for Overpass API queries.
        
        Args:
            country: Country name
            state: State name (optional)
            city: City name (optional)
            
        Returns:
            Area name string for Overpass queries
        """
        # Use most specific location available
        if city:
            return city
        elif state:
            return state
        else:
            return country
    
    def _determine_search_scope(
        self,
        country: str,
        state: Optional[str],
        city: Optional[str]
    ) -> str:
        """Determine the search scope based on provided location."""
        if city:
            return f"city: {city}"
        elif state:
            return f"state: {state}"
        else:
            return f"country: {country}"
    
    def _format_location_string(
        self,
        country: str,
        state: Optional[str],
        city: Optional[str]
    ) -> str:
        """Format location as readable string."""
        parts = []
        if city:
            parts.append(city)
        if state:
            parts.append(state)
        if country:
            parts.append(country)
        return ", ".join(parts)
    
    def validate_hierarchy(
        self,
        country: str,
        state: Optional[str] = None,
        city: Optional[str] = None
    ) -> Dict:
        """
        Validate that the location hierarchy is correct.
        
        Args:
            country: Country name
            state: State name (optional)
            city: City name (optional)
            
        Returns:
            Validation result with suggestions if invalid
        """
        resolution = self.resolve_location(country, state, city)
        
        if not resolution['success']:
            return {
                'valid': False,
                'error': resolution['error'],
                'suggestions': self._get_suggestions(country, state, city)
            }
        
        # Check if resolved location matches input
        resolved = resolution['resolved_address']
        
        matches = {
            'country_match': resolved['country'] and 
                           country.lower() in resolved['country'].lower(),
            'state_match': not state or (resolved['state'] and 
                          state.lower() in resolved['state'].lower()),
            'city_match': not city or (resolved['city'] and 
                         city.lower() in resolved['city'].lower())
        }
        
        return {
            'valid': all(matches.values()),
            'matches': matches,
            'resolved': resolved,
            'display_name': resolution['display_name']
        }
    
    def _get_suggestions(
        self,
        country: str,
        state: Optional[str],
        city: Optional[str]
    ) -> List[str]:
        """Get location suggestions if validation fails."""
        suggestions = []
        
        # Try country only
        country_results = self.nominatim.geocode(country, limit=3)
        if country_results:
            suggestions.extend([r['display_name'] for r in country_results])
        
        # Try state if provided
        if state:
            state_results = self.nominatim.geocode(f"{state}, {country}", limit=2)
            if state_results:
                suggestions.extend([r['display_name'] for r in state_results])
        
        return list(set(suggestions))[:5]  # Return up to 5 unique suggestions
    
    def get_nearby_locations(
        self,
        country: str,
        state: Optional[str] = None,
        city: Optional[str] = None,
        radius_km: float = 50
    ) -> List[Dict]:
        """
        Get nearby cities/towns within a radius.
        
        Args:
            country: Country name
            state: State name (optional)
            city: City name (optional)
            radius_km: Search radius in kilometers
            
        Returns:
            List of nearby locations
        """
        resolution = self.resolve_location(country, state, city)
        
        if not resolution['success']:
            return []
        
        coords = resolution['coordinates']
        
        nearby = self.nominatim.get_nearby_cities(
            lat=coords['lat'],
            lon=coords['lon'],
            radius_km=radius_km
        )
        
        return nearby
    
    def get_location_info(
        self,
        country: str,
        state: Optional[str] = None,
        city: Optional[str] = None
    ) -> Dict:
        """
        Get comprehensive location information.
        
        Args:
            country: Country name
            state: State name (optional)
            city: City name (optional)
            
        Returns:
            Complete location information
        """
        resolution = self.resolve_location(country, state, city)
        
        if not resolution['success']:
            return resolution
        
        bbox = resolution['bounding_box']
        
        # Calculate approximate area size
        area_km2 = self._calculate_area(bbox)
        
        return {
            'success': True,
            'location': {
                'country': country,
                'state': state,
                'city': city,
                'display_name': resolution['display_name']
            },
            'coordinates': resolution['coordinates'],
            'bounding_box': bbox,
            'area': {
                'approximate_size_km2': area_km2,
                'size_category': self._categorize_area_size(area_km2)
            },
            'search_scope': resolution['search_scope']
        }
    
    def _calculate_area(self, bbox: Dict) -> float:
        """
        Calculate approximate area of bounding box in km².
        
        Args:
            bbox: Bounding box with north, south, east, west
            
        Returns:
            Area in square kilometers
        """
        # Approximate calculation (1 degree ≈ 111 km)
        lat_diff = abs(bbox['north'] - bbox['south'])
        lon_diff = abs(bbox['east'] - bbox['west'])
        
        # Adjust longitude for latitude (longitude degrees are smaller near poles)
        avg_lat = (bbox['north'] + bbox['south']) / 2
        lon_km_per_deg = 111.0 * abs(cos_deg(avg_lat))
        
        height_km = lat_diff * 111.0
        width_km = lon_diff * lon_km_per_deg
        
        return round(height_km * width_km, 2)
    
    def _categorize_area_size(self, area_km2: float) -> str:
        """Categorize area size."""
        if area_km2 < 100:
            return "small (city)"
        elif area_km2 < 10000:
            return "medium (region)"
        elif area_km2 < 100000:
            return "large (state)"
        else:
            return "very large (country/multiple states)"
    
    def clear_cache(self):
        """Clear the location cache."""
        self.cache = {}
        print("🗑️  Location cache cleared")


def cos_deg(degrees: float) -> float:
    """Calculate cosine of degrees."""
    import math
    return math.cos(math.radians(degrees))


# Example usage and testing
def test_location_resolver():
    """Test the location resolver with sample queries."""
    print("🗺️  Testing Location Resolver")
    print("="*60)
    
    resolver = LocationResolver()
    
    # Test 1: Country only
    print("\n1️⃣  Resolving: India (country only)")
    result = resolver.resolve_location(country="India")
    if result['success']:
        print(f"   ✅ Resolved: {result['display_name']}")
        print(f"   📍 Center: {result['coordinates']['lat']}, {result['coordinates']['lon']}")
        print(f"   🔍 Search scope: {result['search_scope']}")
    
    # Test 2: Country + State
    print("\n2️⃣  Resolving: Tamil Nadu, India")
    result = resolver.resolve_location(country="India", state="Tamil Nadu")
    if result['success']:
        print(f"   ✅ Resolved: {result['display_name']}")
        print(f"   📦 Bounding box: N={result['bounding_box']['north']:.2f}, S={result['bounding_box']['south']:.2f}")
    
    # Test 3: Country + State + City
    print("\n3️⃣  Resolving: Ooty, Tamil Nadu, India")
    result = resolver.resolve_location(country="India", state="Tamil Nadu", city="Ooty")
    if result['success']:
        print(f"   ✅ Resolved: {result['display_name']}")
        print(f"   📍 Coordinates: {result['coordinates']}")
    
    # Test 4: Get search area
    print("\n4️⃣  Getting search area for Tamil Nadu")
    search_area = resolver.get_search_area(country="India", state="Tamil Nadu")
    if search_area:
        print(f"   ✅ Search area retrieved")
        print(f"   📏 Area: {search_area['area_name']}")
    
    # Test 5: Location info
    print("\n5️⃣  Getting comprehensive info for Chennai")
    info = resolver.get_location_info(country="India", state="Tamil Nadu", city="Chennai")
    if info['success']:
        print(f"   ✅ Info retrieved")
        print(f"   📊 Area size: {info['area']['approximate_size_km2']} km²")
        print(f"   📏 Category: {info['area']['size_category']}")
    
    # Test 6: Invalid location
    print("\n6️⃣  Testing invalid location: XYZ City")
    result = resolver.resolve_location(country="India", state="Tamil Nadu", city="XYZ")
    if not result['success']:
        print(f"   ✅ Correctly identified as invalid")
        print(f"   ❌ Error: {result['error']}")
    
    print("\n" + "="*60)
    print("✅ Location resolver test complete!")


if __name__ == "__main__":
    print("✅ Location Resolver - Ready!")