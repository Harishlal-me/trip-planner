"""
models/recommender/osm_recommender.py
OSM-Based Destination Recommender
Fetches and recommends places in real-time using OpenStreetMap data
"""

import sys
import os
from typing import Dict, List, Optional, Set
from collections import defaultdict
import time

# Add parent directories to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from services.nominatim_service import NominatimService
from services.overpass_service import OverpassService
from models.location.resolver import LocationResolver


class OSMRecommender:
    """
    Real-time destination recommender using OpenStreetMap data.
    No pre-stored destinations - fetches places on-demand.
    """
    
    # Place categories to fetch
    DEFAULT_CATEGORIES = [
        'tourist_attraction',
        'temple',
        'beach',
        'mountain',
        'museum',
        'park',
        'viewpoint',
        'monument'
    ]
    
    # Category weights for interest matching
    CATEGORY_KEYWORDS = {
        'nature': ['beach', 'mountain', 'park', 'waterfall', 'viewpoint'],
        'religious': ['temple', 'monument'],
        'culture': ['museum', 'monument', 'tourist_attraction'],
        'adventure': ['mountain', 'viewpoint', 'beach'],
        'history': ['monument', 'museum', 'tourist_attraction'],
        'relaxation': ['beach', 'park'],
        'heritage': ['monument', 'tourist_attraction']
    }
    
    def __init__(self):
        """Initialize OSM recommender with required services."""
        self.location_resolver = LocationResolver()
        self.overpass = OverpassService()
        self.nominatim = NominatimService()
        self.cache = {}
    
    def get_recommendations(
        self,
        country: str,
        state: Optional[str] = None,
        city: Optional[str] = None,
        interests: Optional[List[str]] = None,
        limit: int = 10
    ) -> Dict:
        """
        Get destination recommendations for a location.
        
        Args:
            country: Country name (required)
            state: State/province name (optional)
            city: City name (optional)
            interests: List of user interests (e.g., ['nature', 'temples'])
            limit: Number of recommendations to return
            
        Returns:
            Dictionary with recommendations and metadata
        """
        print(f"\n🔍 Fetching recommendations for: {self._format_location(country, state, city)}")
        
        # Resolve location
        location = self.location_resolver.resolve_location(country, state, city)
        
        if not location['success']:
            return {
                'success': False,
                'error': location['error'],
                'recommendations': []
            }
        
        # Get bounding box for search
        bbox = location['bounding_box']
        
        print(f"📦 Search area: {location['display_name']}")
        print(f"🔎 Fetching places from OpenStreetMap...")
        
        # Fetch places from OSM
        places = self.overpass.fetch_places_by_bbox(
            bbox=bbox,
            categories=self.DEFAULT_CATEGORIES,
            limit=100  # Fetch more to rank better
        )
        
        if not places:
            return {
                'success': True,
                'location': location['display_name'],
                'recommendations': [],
                'message': 'No places found in this area. Try a different location.'
            }
        
        print(f"✅ Found {len(places)} places")
        print(f"🧮 Ranking places...")
        
        # Rank places
        ranked_places = self._rank_places(
            places=places,
            interests=interests,
            center_lat=location['coordinates']['lat'],
            center_lon=location['coordinates']['lon']
        )
        
        # Get top recommendations
        top_recommendations = ranked_places[:limit]
        
        return {
            'success': True,
            'location': {
                'country': country,
                'state': state,
                'city': city,
                'display_name': location['display_name'],
                'coordinates': location['coordinates']
            },
            'recommendations': top_recommendations,
            'total_found': len(places),
            'interests_applied': interests or [],
            'search_scope': location['search_scope']
        }
    
    def get_top_places(
        self,
        country: str,
        state: Optional[str] = None,
        city: Optional[str] = None,
        interests: Optional[List[str]] = None
    ) -> List[Dict]:
        """
        Get top 10 places for a location.
        
        Args:
            country: Country name
            state: State name (optional)
            city: City name (optional)
            interests: User interests (optional)
            
        Returns:
            List of top 10 places
        """
        result = self.get_recommendations(
            country=country,
            state=state,
            city=city,
            interests=interests,
            limit=10
        )
        
        return result.get('recommendations', [])
    
    def get_places_by_category(
        self,
        country: str,
        state: Optional[str] = None,
        city: Optional[str] = None,
        category: str = 'tourist_attraction',
        limit: int = 10
    ) -> List[Dict]:
        """
        Get places filtered by specific category.
        
        Args:
            country: Country name
            state: State name (optional)
            city: City name (optional)
            category: Category to filter (e.g., 'temple', 'beach')
            limit: Number of results
            
        Returns:
            List of places in that category
        """
        # Resolve location
        location = self.location_resolver.resolve_location(country, state, city)
        
        if not location['success']:
            return []
        
        bbox = location['bounding_box']
        
        # Fetch specific category
        places = self.overpass.fetch_specific_types(
            bbox=bbox,
            place_type=category,
            limit=limit * 2  # Fetch extra for better ranking
        )
        
        # Rank by basic criteria
        ranked = self._rank_places(
            places=places,
            interests=None,
            center_lat=location['coordinates']['lat'],
            center_lon=location['coordinates']['lon']
        )
        
        return ranked[:limit]
    
    def _rank_places(
        self,
        places: List[Dict],
        interests: Optional[List[str]],
        center_lat: float,
        center_lon: float
    ) -> List[Dict]:
        """
        Rank places using ML-inspired scoring.
        
        Ranking formula:
        Score = 0.35 × Popularity +
                0.25 × Interest Match +
                0.20 × Season Fit +
                0.10 × Distance Balance +
                0.10 × Diversity Boost
        """
        scored_places = []
        category_counts = defaultdict(int)
        
        for place in places:
            # Calculate individual scores
            popularity_score = self._calculate_popularity(place)
            interest_score = self._calculate_interest_match(place, interests)
            season_score = self._calculate_season_fit(place)
            distance_score = self._calculate_distance_score(
                place['lat'], place['lon'], center_lat, center_lon
            )
            
            # Diversity boost (penalize overrepresented categories)
            category = place['category']
            diversity_score = 1.0 / (1.0 + category_counts[category] * 0.1)
            category_counts[category] += 1
            
            # Combined score
            final_score = (
                0.35 * popularity_score +
                0.25 * interest_score +
                0.20 * season_score +
                0.10 * distance_score +
                0.10 * diversity_score
            )
            
            place['rank_score'] = round(final_score, 4)
            place['score_breakdown'] = {
                'popularity': round(popularity_score, 2),
                'interest_match': round(interest_score, 2),
                'season_fit': round(season_score, 2),
                'distance': round(distance_score, 2),
                'diversity': round(diversity_score, 2)
            }
            
            scored_places.append(place)
        
        # Sort by score
        ranked = sorted(scored_places, key=lambda x: x['rank_score'], reverse=True)
        
        # Add rank numbers
        for i, place in enumerate(ranked, 1):
            place['rank'] = i
        
        return ranked
    
    def _calculate_popularity(self, place: Dict) -> float:
        """
        Calculate popularity score (0-1).
        Based on OSM tags presence (proxy for community interest).
        """
        tags = place.get('tags', {})
        
        score = 0.5  # Base score
        
        # Boost for having additional information
        if tags.get('wikipedia'):
            score += 0.2
        if tags.get('website'):
            score += 0.1
        if tags.get('description'):
            score += 0.1
        if tags.get('tourism') == 'attraction':
            score += 0.1
        
        return min(score, 1.0)
    
    def _calculate_interest_match(
        self,
        place: Dict,
        interests: Optional[List[str]]
    ) -> float:
        """Calculate how well place matches user interests (0-1)."""
        if not interests:
            return 0.5  # Neutral score if no interests
        
        place_category = place['category'].lower()
        score = 0.0
        
        for interest in interests:
            interest = interest.lower()
            
            # Check if interest keywords match category
            if interest in self.CATEGORY_KEYWORDS:
                relevant_categories = self.CATEGORY_KEYWORDS[interest]
                for cat in relevant_categories:
                    if cat in place_category:
                        score += 1.0 / len(interests)
                        break
            
            # Direct keyword match
            if interest in place_category or place_category in interest:
                score += 0.5 / len(interests)
        
        return min(score, 1.0)
    
    def _calculate_season_fit(self, place: Dict) -> float:
        """
        Calculate season fitness score (0-1).
        Simple heuristic based on place type.
        """
        category = place['category'].lower()
        
        # Get current month (simplified - would use actual date in production)
        import datetime
        month = datetime.datetime.now().month
        
        # Season rules
        if 'beach' in category:
            # Better in summer (June-August in Northern Hemisphere)
            if 6 <= month <= 8:
                return 1.0
            elif 3 <= month <= 5 or 9 <= month <= 11:
                return 0.7
            else:
                return 0.4
        
        elif 'mountain' in category or 'hill' in category:
            # Better in spring/fall
            if 3 <= month <= 5 or 9 <= month <= 11:
                return 1.0
            else:
                return 0.7
        
        else:
            # Indoor/all-season places
            return 0.8
    
    def _calculate_distance_score(
        self,
        place_lat: float,
        place_lon: float,
        center_lat: float,
        center_lon: float
    ) -> float:
        """
        Calculate distance score (0-1).
        Prefers places not too far from center.
        """
        # Simple distance calculation
        lat_diff = abs(place_lat - center_lat)
        lon_diff = abs(place_lon - center_lon)
        distance = (lat_diff**2 + lon_diff**2)**0.5
        
        # Normalize (0.5 degrees ≈ 55km, reasonable range)
        if distance < 0.1:
            return 1.0
        elif distance < 0.3:
            return 0.8
        elif distance < 0.5:
            return 0.6
        else:
            return 0.4
    
    def _format_location(
        self,
        country: str,
        state: Optional[str],
        city: Optional[str]
    ) -> str:
        """Format location as string."""
        parts = []
        if city:
            parts.append(city)
        if state:
            parts.append(state)
        if country:
            parts.append(country)
        return ", ".join(parts)
    
    def get_summary_statistics(
        self,
        recommendations: List[Dict]
    ) -> Dict:
        """
        Get summary statistics for recommendations.
        
        Args:
            recommendations: List of recommended places
            
        Returns:
            Statistics summary
        """
        if not recommendations:
            return {}
        
        # Category distribution
        categories = defaultdict(int)
        for place in recommendations:
            categories[place['category']] += 1
        
        # Average score
        avg_score = sum(p['rank_score'] for p in recommendations) / len(recommendations)
        
        return {
            'total_places': len(recommendations),
            'categories': dict(categories),
            'average_score': round(avg_score, 2),
            'top_category': max(categories, key=categories.get)
        }


# Example usage and testing
def test_osm_recommender():
    """Test the OSM recommender with sample queries."""
    print("🗺️  Testing OSM Destination Recommender")
    print("="*60)
    
    recommender = OSMRecommender()
    
    # Test 1: Get recommendations for Tamil Nadu
    print("\n1️⃣  Getting top 10 places in Tamil Nadu, India")
    print("   (This may take 20-30 seconds...)")
    
    result = recommender.get_recommendations(
        country="India",
        state="Tamil Nadu",
        interests=['nature', 'temples'],
        limit=10
    )
    
    if result['success']:
        print(f"\n   ✅ Found {result['total_found']} places total")
        print(f"   🏆 Top 10 recommendations:")
        
        for place in result['recommendations'][:10]:
            print(f"\n   {place['rank']}. {place['name']}")
            print(f"      Category: {place['category']}")
            print(f"      Score: {place['rank_score']}")
            print(f"      📍 Location: {place['lat']:.4f}, {place['lon']:.4f}")
    else:
        print(f"   ❌ Error: {result['error']}")
    
    # Test 2: Get temples only
    print("\n\n2️⃣  Getting top temples in Tamil Nadu")
    temples = recommender.get_places_by_category(
        country="India",
        state="Tamil Nadu",
        category='place_of_worship',
        limit=5
    )
    
    if temples:
        print(f"   ✅ Found {len(temples)} temples")
        for i, temple in enumerate(temples[:3], 1):
            print(f"   {i}. {temple['name']}")
    
    print("\n" + "="*60)
    print("✅ OSM recommender test complete!")
    print("\n💡 Note: Results are fetched in real-time from OpenStreetMap")


if __name__ == "__main__":
    print("✅ OSM Recommender - Ready!")