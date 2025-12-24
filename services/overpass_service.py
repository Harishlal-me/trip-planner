"""
services/overpass_service.py
Free Places Data Service using Overpass API (OpenStreetMap)
Fetch unlimited tourist attractions, landmarks, and POIs globally
"""

import requests
import time
from typing import Dict, List, Optional, Set
import json


class OverpassService:
    """
    Free places/POI service using Overpass API (OpenStreetMap).
    No API key required, fetches unlimited real-world places.
    """
    
    # Public Overpass API endpoints
    ENDPOINTS = [
        "https://overpass-api.de/api/interpreter",
        "https://overpass.kumi.systems/api/interpreter",
        "https://overpass.openstreetmap.ru/api/interpreter"
    ]
    
    def __init__(self, timeout: int = 60):
        """
        Initialize Overpass service.
        
        Args:
            timeout: Request timeout in seconds
        """
        self.timeout = timeout
        self.current_endpoint = 0
        self.last_request_time = 0
        self.rate_limit_delay = 2.0  # 2 seconds between requests
    
    def _rate_limit(self):
        """Ensure reasonable rate limiting."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - time_since_last)
        
        self.last_request_time = time.time()
    
    def _get_endpoint(self) -> str:
        """Get current endpoint and rotate if needed."""
        return self.ENDPOINTS[self.current_endpoint % len(self.ENDPOINTS)]
    
    def _rotate_endpoint(self):
        """Rotate to next endpoint on failure."""
        self.current_endpoint += 1
        print(f"🔄 Rotating to endpoint: {self._get_endpoint()}")
    
    def _make_request(self, query: str) -> Optional[Dict]:
        """
        Execute Overpass query.
        
        Args:
            query: Overpass QL query string
            
        Returns:
            JSON response or None if failed
        """
        self._rate_limit()
        
        max_retries = len(self.ENDPOINTS)
        
        for attempt in range(max_retries):
            try:
                endpoint = self._get_endpoint()
                
                response = requests.post(
                    endpoint,
                    data={'data': query},
                    timeout=self.timeout
                )
                response.raise_for_status()
                return response.json()
                
            except requests.exceptions.RequestException as e:
                print(f"❌ Overpass API error (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    self._rotate_endpoint()
                    time.sleep(2)
                else:
                    return None
        
        return None
    
    def fetch_places_by_bbox(
        self,
        bbox: Dict,
        categories: Optional[List[str]] = None,
        limit: int = 100
    ) -> List[Dict]:
        """
        Fetch places within a bounding box.
        
        Args:
            bbox: Bounding box with keys: south, north, west, east
            categories: List of place categories to fetch
            limit: Maximum number of results
            
        Returns:
            List of places with details
        """
        if categories is None:
            categories = [
                'tourist_attraction',
                'temple',
                'beach',
                'mountain',
                'museum',
                'park',
                'viewpoint',
                'monument'
            ]
        
        # Build Overpass query
        query = self._build_bbox_query(bbox, categories, limit)
        
        # Execute query
        result = self._make_request(query)
        
        if not result or 'elements' not in result:
            return []
        
        # Parse and format results
        places = []
        for element in result['elements']:
            place = self._parse_element(element)
            if place:
                places.append(place)
        
        return places
    
    def fetch_places_by_area(
        self,
        area_name: str,
        categories: Optional[List[str]] = None,
        limit: int = 100
    ) -> List[Dict]:
        """
        Fetch places within a named area (country, state, city).
        
        Args:
            area_name: Name of the area (e.g., "Tamil Nadu")
            categories: List of place categories
            limit: Maximum number of results
            
        Returns:
            List of places
        """
        if categories is None:
            categories = [
                'tourist_attraction',
                'temple',
                'beach',
                'mountain',
                'museum',
                'park',
                'viewpoint'
            ]
        
        # Build Overpass query for named area
        query = self._build_area_query(area_name, categories, limit)
        
        # Execute query
        result = self._make_request(query)
        
        if not result or 'elements' not in result:
            return []
        
        # Parse results
        places = []
        for element in result['elements']:
            place = self._parse_element(element)
            if place:
                places.append(place)
        
        return places
    
    def fetch_specific_types(
        self,
        bbox: Dict,
        place_type: str,
        limit: int = 50
    ) -> List[Dict]:
        """
        Fetch specific type of places (e.g., only temples, only beaches).
        
        Args:
            bbox: Bounding box
            place_type: OSM tag value (e.g., 'temple', 'beach')
            limit: Maximum results
            
        Returns:
            List of places
        """
        query = f"""
        [out:json][timeout:{self.timeout}];
        (
          node["tourism"="{place_type}"]({bbox['south']},{bbox['west']},{bbox['north']},{bbox['east']});
          way["tourism"="{place_type}"]({bbox['south']},{bbox['west']},{bbox['north']},{bbox['east']});
          node["natural"="{place_type}"]({bbox['south']},{bbox['west']},{bbox['north']},{bbox['east']});
          way["natural"="{place_type}"]({bbox['south']},{bbox['west']},{bbox['north']},{bbox['east']});
          node["historic"="{place_type}"]({bbox['south']},{bbox['west']},{bbox['north']},{bbox['east']});
          way["historic"="{place_type}"]({bbox['south']},{bbox['west']},{bbox['north']},{bbox['east']});
        );
        out center {limit};
        """
        
        result = self._make_request(query)
        
        if not result or 'elements' not in result:
            return []
        
        places = []
        for element in result['elements']:
            place = self._parse_element(element)
            if place:
                places.append(place)
        
        return places
    
    def _build_bbox_query(
        self,
        bbox: Dict,
        categories: List[str],
        limit: int
    ) -> str:
        """Build Overpass query for bounding box search."""
        
        # Category mapping to OSM tags
        category_tags = {
            'tourist_attraction': 'tourism=attraction',
            'temple': 'amenity=place_of_worship',
            'beach': 'natural=beach',
            'mountain': 'natural=peak',
            'museum': 'tourism=museum',
            'park': 'leisure=park',
            'viewpoint': 'tourism=viewpoint',
            'monument': 'historic=monument',
            'castle': 'historic=castle',
            'waterfall': 'natural=waterfall'
        }
        
        # Build query parts
        query_parts = []
        for category in categories:
            tag = category_tags.get(category, f'tourism={category}')
            
            # Query both nodes and ways
            query_parts.append(
                f'node[{tag}]({bbox["south"]},{bbox["west"]},{bbox["north"]},{bbox["east"]});'
            )
            query_parts.append(
                f'way[{tag}]({bbox["south"]},{bbox["west"]},{bbox["north"]},{bbox["east"]});'
            )
        
        query = f"""
        [out:json][timeout:{self.timeout}];
        (
          {' '.join(query_parts)}
        );
        out center {limit};
        """
        
        return query
    
    def _build_area_query(
        self,
        area_name: str,
        categories: List[str],
        limit: int
    ) -> str:
        """Build Overpass query for named area search."""
        
        category_tags = {
            'tourist_attraction': 'tourism=attraction',
            'temple': 'amenity=place_of_worship',
            'beach': 'natural=beach',
            'mountain': 'natural=peak',
            'museum': 'tourism=museum',
            'park': 'leisure=park',
            'viewpoint': 'tourism=viewpoint',
            'monument': 'historic=monument'
        }
        
        query_parts = []
        for category in categories:
            tag = category_tags.get(category, f'tourism={category}')
            query_parts.append(f'node[{tag}](area.searchArea);')
            query_parts.append(f'way[{tag}](area.searchArea);')
        
        query = f"""
        [out:json][timeout:{self.timeout}];
        area["name"="{area_name}"]->.searchArea;
        (
          {' '.join(query_parts)}
        );
        out center {limit};
        """
        
        return query
    
    def _parse_element(self, element: Dict) -> Optional[Dict]:
        """Parse OSM element into standardized place format."""
        
        tags = element.get('tags', {})
        
        # Extract name
        name = tags.get('name') or tags.get('name:en') or tags.get('ref')
        
        if not name:
            return None
        
        # Get coordinates
        if element['type'] == 'node':
            lat = element.get('lat')
            lon = element.get('lon')
        elif 'center' in element:
            lat = element['center'].get('lat')
            lon = element['center'].get('lon')
        else:
            return None
        
        if not lat or not lon:
            return None
        
        # Determine category
        category = self._categorize_place(tags)
        
        # Extract additional info
        place = {
            'name': name,
            'category': category,
            'lat': float(lat),
            'lon': float(lon),
            'osm_id': element.get('id'),
            'osm_type': element.get('type'),
            'tags': {
                'tourism': tags.get('tourism'),
                'natural': tags.get('natural'),
                'historic': tags.get('historic'),
                'leisure': tags.get('leisure'),
                'amenity': tags.get('amenity'),
                'religion': tags.get('religion'),
                'wikipedia': tags.get('wikipedia'),
                'website': tags.get('website'),
                'description': tags.get('description')
            }
        }
        
        return place
    
    def _categorize_place(self, tags: Dict) -> str:
        """Categorize place based on OSM tags."""
        
        # Priority-based categorization
        if tags.get('natural') == 'beach':
            return 'Beach'
        elif tags.get('natural') == 'peak':
            return 'Mountain'
        elif tags.get('natural') == 'waterfall':
            return 'Waterfall'
        elif tags.get('tourism') == 'attraction':
            return 'Tourist Attraction'
        elif tags.get('tourism') == 'museum':
            return 'Museum'
        elif tags.get('tourism') == 'viewpoint':
            return 'Viewpoint'
        elif tags.get('historic') == 'monument':
            return 'Monument'
        elif tags.get('historic') == 'castle':
            return 'Castle'
        elif tags.get('historic') == 'archaeological_site':
            return 'Archaeological Site'
        elif tags.get('amenity') == 'place_of_worship':
            religion = tags.get('religion', 'Religious Site')
            return f'{religion.title()} Temple' if religion else 'Temple'
        elif tags.get('leisure') == 'park':
            return 'Park'
        else:
            return 'Point of Interest'
    
    def get_place_details(
        self,
        osm_id: int,
        osm_type: str = 'node'
    ) -> Optional[Dict]:
        """
        Get detailed information about a specific place.
        
        Args:
            osm_id: OpenStreetMap ID
            osm_type: Type (node, way, relation)
            
        Returns:
            Detailed place information
        """
        query = f"""
        [out:json][timeout:{self.timeout}];
        {osm_type}({osm_id});
        out body;
        """
        
        result = self._make_request(query)
        
        if not result or 'elements' not in result or not result['elements']:
            return None
        
        return self._parse_element(result['elements'][0])


if __name__ == "__main__":
    print("✅ Overpass Service - Ready for unlimited place queries!")