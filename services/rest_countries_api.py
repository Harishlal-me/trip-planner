"""
REST Countries API Service - FIXED VERSION
FREE country information - no API key required
Uses v3.1 endpoint (NOT v2 or .eu domain)
"""

import requests
from typing import Dict, List, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RestCountriesAPI:
    """
    Interface for REST Countries API v3.1
    Provides comprehensive country information
    """
    
    def __init__(self):
        """Initialize REST Countries API client"""
        # FIXED: Use v3.1 endpoint ONLY
        self.base_url = "https://restcountries.com/v3.1"
        logger.info(f"REST Countries API initialized: {self.base_url}")
        
    def get_country_by_name(self, country_name: str) -> Optional[Dict]:
        """
        Get detailed country information by name
        
        Args:
            country_name: Name of the country
            
        Returns:
            Dictionary with country information
        """
        # FIXED: Correct v3.1 endpoint
        url = f"{self.base_url}/name/{country_name}"
        
        try:
            logger.info(f"Fetching country: {country_name}")
            response = requests.get(
                url,
                params={'fullText': 'false'},
                timeout=10
            )
            
            logger.info(f"Response status: {response.status_code}")
            response.raise_for_status()
            
            data = response.json()
            
            if not data or len(data) == 0:
                logger.warning(f"No country found with name: {country_name}")
                return None
                
            # FIXED: v3.1 returns array, get first result
            country = data[0]
            
            return self._format_country_data(country)
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                logger.error(f"❌ Country not found: {country_name}")
            else:
                logger.error(f"❌ HTTP error {e.response.status_code}: {e}")
            return None
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Error fetching country '{country_name}': {str(e)}")
            return None
            
    def get_country_info(self, country_name: str) -> Optional[Dict]:
        """
        Get basic country information (alias for get_country_by_name)
        
        Args:
            country_name: Name of the country
            
        Returns:
            Dictionary with country information
        """
        return self.get_country_by_name(country_name)
    
    def get_country_by_code(self, country_code: str) -> Optional[Dict]:
        """
        Get country information by ISO code
        
        Args:
            country_code: 2-letter (alpha2) or 3-letter (alpha3) country code
            
        Returns:
            Dictionary with country information
        """
        # FIXED: Correct v3.1 endpoint
        url = f"{self.base_url}/alpha/{country_code}"
        
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            # FIXED: v3.1 can return single object OR array
            data = response.json()
            
            # If it's a list, get the first item
            if isinstance(data, list):
                if len(data) == 0:
                    logger.warning(f"No country found with code: {country_code}")
                    return None
                country = data[0]
            else:
                country = data
                
            return self._format_country_data(country)
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching country code '{country_code}': {str(e)}")
            return None
            
    def get_countries_by_region(self, region: str) -> List[Dict]:
        """
        Get all countries in a specific region
        
        Args:
            region: Region name (e.g., 'Europe', 'Asia', 'Africa', 'Americas', 'Oceania')
            
        Returns:
            List of country dictionaries
        """
        url = f"{self.base_url}/region/{region}"
        
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            countries = [self._format_country_data(country) for country in data]
            logger.info(f"Found {len(countries)} countries in {region}")
            
            return countries
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching countries in region '{region}': {str(e)}")
            return []
            
    def get_countries_by_currency(self, currency_code: str) -> List[Dict]:
        """
        Get countries that use a specific currency
        
        Args:
            currency_code: 3-letter currency code (e.g., 'USD', 'EUR', 'JPY')
            
        Returns:
            List of country dictionaries
        """
        url = f"{self.base_url}/currency/{currency_code}"
        
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            countries = [self._format_country_data(country) for country in data]
            
            logger.info(f"Found {len(countries)} countries using {currency_code}")
            return countries
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching countries with currency '{currency_code}': {str(e)}")
            return []
            
    def get_countries_by_language(self, language_code: str) -> List[Dict]:
        """
        Get countries where a specific language is spoken
        
        Args:
            language_code: Language code (e.g., 'en', 'es', 'fr', 'zh')
            
        Returns:
            List of country dictionaries
        """
        url = f"{self.base_url}/lang/{language_code}"
        
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            countries = [self._format_country_data(country) for country in data]
            
            logger.info(f"Found {len(countries)} countries speaking {language_code}")
            return countries
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching countries with language '{language_code}': {str(e)}")
            return []
            
    def get_all_countries(self) -> List[Dict]:
        """
        Get information about all countries
        
        Returns:
            List of all country dictionaries
        """
        url = f"{self.base_url}/all"
        
        try:
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            countries = [self._format_country_data(country) for country in data]
            
            logger.info(f"Retrieved {len(countries)} countries")
            return countries
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching all countries: {str(e)}")
            return []
            
    def search_countries(self, query: str) -> List[Dict]:
        """
        Search for countries by name, capital, or region
        
        Args:
            query: Search query
            
        Returns:
            List of matching countries
        """
        all_countries = self.get_all_countries()
        
        query_lower = query.lower()
        matches = []
        
        for country in all_countries:
            # Search in name, capital, and region
            if (query_lower in country['name'].lower() or
                query_lower in country.get('capital', '').lower() or
                query_lower in country.get('region', '').lower()):
                matches.append(country)
                
        logger.info(f"Found {len(matches)} countries matching '{query}'")
        return matches
        
    def get_neighboring_countries(self, country_code: str) -> List[Dict]:
        """
        Get countries that border the specified country
        
        Args:
            country_code: 2 or 3-letter country code
            
        Returns:
            List of neighboring country dictionaries
        """
        country = self.get_country_by_code(country_code)
        
        if not country or not country.get('borders'):
            return []
            
        neighbors = []
        for border_code in country['borders']:
            neighbor = self.get_country_by_code(border_code)
            if neighbor:
                neighbors.append(neighbor)
                
        logger.info(f"Found {len(neighbors)} neighboring countries")
        return neighbors
        
    def _format_country_data(self, country: Dict) -> Dict:
        """
        Format raw API response into standardized structure
        FIXED for v3.1 response format
        
        Args:
            country: Raw country data from API
            
        Returns:
            Formatted country dictionary
        """
        # FIXED: v3.1 structure for name
        name = country.get('name', {})
        common_name = name.get('common', 'Unknown')
        official_name = name.get('official', common_name)
        
        # FIXED: v3.1 structure for currencies
        currencies = country.get('currencies', {})
        currency_list = []
        for code, info in currencies.items():
            currency_list.append({
                'code': code,
                'name': info.get('name'),
                'symbol': info.get('symbol')
            })
            
        # FIXED: v3.1 structure for languages
        languages = country.get('languages', {})
        language_list = list(languages.values())
        
        # FIXED: v3.1 structure for capital
        capitals = country.get('capital', [])
        capital = capitals[0] if capitals else None
        
        # FIXED: v3.1 structure for coordinates
        latlng = country.get('latlng', [None, None])
        
        return {
            'name': common_name,
            'official_name': official_name,
            'code_alpha2': country.get('cca2'),
            'code_alpha3': country.get('cca3'),
            'capital': capital,
            'region': country.get('region'),
            'subregion': country.get('subregion'),
            'population': country.get('population'),
            'area': country.get('area'),
            'currencies': currency_list,
            'languages': language_list,
            'borders': country.get('borders', []),
            'timezones': country.get('timezones', []),
            'flag': country.get('flags', {}).get('png'),
            'flag_emoji': country.get('flag'),
            'coordinates': {
                'latitude': latlng[0] if len(latlng) > 0 else None,
                'longitude': latlng[1] if len(latlng) > 1 else None
            },
            'maps': {
                'google': country.get('maps', {}).get('googleMaps'),
                'openstreetmap': country.get('maps', {}).get('openStreetMaps')
            },
            'independent': country.get('independent', False),
            'un_member': country.get('unMember', False),
            'start_of_week': country.get('startOfWeek', 'monday'),
            'car_side': country.get('car', {}).get('side', 'right'),
            'tld': country.get('tld', [])
        }
        
    def get_country_info(self, country_name: str) -> Optional[Dict]:
        """
        Get basic country information (alias for get_country_by_name)
        
        Args:
            country_name: Name of the country
            
        Returns:
            Dictionary with country information
        """
        return self.get_country_by_name(country_name)
    
    def get_travel_info(self, country_name: str) -> Optional[Dict]:
        """
        Get travel-relevant information for a country
        
        Args:
            country_name: Name of the country
            
        Returns:
            Dictionary with travel information
        """
        country = self.get_country_by_name(country_name)
        
        if not country:
            return None
            
        # Determine if visa might be needed (simplified logic)
        visa_note = "Visa requirements vary by nationality. Check with embassy."
        
        return {
            'country': country['name'],
            'capital': country['capital'],
            'region': country['region'],
            'languages': country['languages'],
            'currencies': country['currencies'],
            'timezone': country['timezones'][0] if country['timezones'] else None,
            'driving_side': country['car_side'],
            'emergency_number': '112' if country['region'] == 'Europe' else 'Varies',
            'visa_note': visa_note,
            'population': country['population'],
            'coordinates': country['coordinates'],
            'map_link': country['maps']['google']
        }


if __name__ == "__main__":
    # Test the API
    api = RestCountriesAPI()
    
    print("=" * 60)
    print("Testing REST Countries API - FIXED v3.1")
    print("=" * 60)
    
    # Test 1: Get country by name
    print("\n1. Getting info for India...")
    country = api.get_country_by_name("India")
    if country:
        print(f"   ✅ Name: {country['name']}")
        print(f"   Capital: {country['capital']}")
        print(f"   Population: {country['population']:,}")
        print(f"   Region: {country['region']}")
        if country['currencies']:
            print(f"   Currency: {country['currencies'][0]['name']}")
    else:
        print("   ❌ Failed to get country info")
    
    # Test 2: Get country by code
    print("\n2. Getting info by code (US)...")
    country = api.get_country_by_code("US")
    if country:
        print(f"   ✅ Country: {country['name']}")
        print(f"   Languages: {', '.join(country['languages'])}")
    else:
        print("   ❌ Failed to get country by code")
    
    # Test 3: Get countries in region
    print("\n3. Getting countries in Asia...")
    countries = api.get_countries_by_region("Asia")
    print(f"   ✅ Found {len(countries)} countries")
    
    # Test 4: Get travel info
    print("\n4. Getting travel info for Japan...")
    travel_info = api.get_travel_info("Japan")
    if travel_info:
        print(f"   ✅ Capital: {travel_info['capital']}")
        if travel_info['currencies']:
            print(f"   Currency: {travel_info['currencies'][0]['name']}")
        print(f"   Timezone: {travel_info['timezone']}")
    else:
        print("   ❌ Failed to get travel info")
    
    print("\n" + "=" * 60)
    print("✅ All tests completed!")
    print("=" * 60)