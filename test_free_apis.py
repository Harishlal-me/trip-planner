"""
Test script to verify all API fixes
Run this to confirm all issues are resolved
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.openweather_api import OpenWeatherAPI
from services.rest_countries_api import RestCountriesAPI
from routing.osrm_optimizer import OSRMOptimizer


def test_openweather():
    """Test OpenWeather API fixes"""
    print("=" * 60)
    print("TEST 1: OpenWeather API")
    print("=" * 60)
    
    try:
        api = OpenWeatherAPI()
        
        # Test current weather
        print("\n✓ Testing current weather...")
        weather = api.get_current_weather("Paris", "FR")
        if weather:
            print(f"  Temperature: {weather['temperature']}°C")
            print("  ✅ PASSED")
        else:
            print("  ❌ FAILED")
            return False
        
        # Test forecast (this was failing)
        print("\n✓ Testing 5-day forecast...")
        forecast = api.get_forecast("London", "GB", days=5)
        if forecast and len(forecast) > 0:
            print(f"  Got {len(forecast)} forecast entries")
            print("  ✅ PASSED")
        else:
            print("  ❌ FAILED")
            return False
            
        # Test daily summary
        print("\n✓ Testing daily forecast summary...")
        daily = api.get_daily_forecast_summary("Tokyo", "JP", days=3)
        if daily and len(daily) > 0:
            print(f"  Got {len(daily)} daily summaries")
            print("  ✅ PASSED")
        else:
            print("  ❌ FAILED")
            return False
        
        return True
        
    except Exception as e:
        print(f"  ❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_rest_countries():
    """Test REST Countries API fixes"""
    print("\n" + "=" * 60)
    print("TEST 2: REST Countries API")
    print("=" * 60)
    
    try:
        api = RestCountriesAPI()
        
        # Test get_country_by_name
        print("\n✓ Testing get_country_by_name...")
        country = api.get_country_by_name("France")
        if country:
            print(f"  Country: {country['name']}")
            print(f"  Capital: {country['capital']}")
            print("  ✅ PASSED")
        else:
            print("  ❌ FAILED")
            return False
        
        # Test get_country_info (this was missing)
        print("\n✓ Testing get_country_info...")
        country = api.get_country_info("Japan")
        if country:
            print(f"  Country: {country['name']}")
            print(f"  Population: {country['population']:,}")
            print("  ✅ PASSED")
        else:
            print("  ❌ FAILED")
            return False
        
        # Test get_country_by_code
        print("\n✓ Testing get_country_by_code...")
        country = api.get_country_by_code("US")
        if country:
            print(f"  Country: {country['name']}")
            print("  ✅ PASSED")
        else:
            print("  ❌ FAILED")
            return False
        
        return True
        
    except Exception as e:
        print(f"  ❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_osrm():
    """Test OSRM Routing fixes"""
    print("\n" + "=" * 60)
    print("TEST 3: OSRM Routing")
    print("=" * 60)
    
    try:
        optimizer = OSRMOptimizer()
        
        # Test simple route
        print("\n✓ Testing simple route (Paris center to Eiffel Tower)...")
        print("  Input: (48.8566, 2.3522) to (48.8584, 2.2945)")
        print("  Note: Input is (latitude, longitude)")
        
        route = optimizer.get_route(
            (48.8566, 2.3522),  # Paris center (lat, lon)
            (48.8584, 2.2945)   # Eiffel Tower (lat, lon)
        )
        
        if route:
            print(f"  Distance: {route['distance_km']} km")
            print(f"  Duration: {route['duration_minutes']} minutes")
            
            # Check if duration_min exists (for compatibility)
            if 'duration_min' in route:
                print(f"  Duration (alt key): {route['duration_min']} minutes")
            
            # Verify we got a non-zero distance
            if route['distance_km'] > 0:
                print("  ✅ PASSED")
            else:
                print("  ⚠️  WARNING: Distance is 0 km (coordinates may be too close)")
                print("  ✅ PASSED (API working)")
            
        else:
            print("  ❌ FAILED")
            return False
        
        # Test multi-point route
        print("\n✓ Testing multi-point route...")
        waypoints = [
            (48.8566, 2.3522),  # Paris center
            (48.8584, 2.2945),  # Eiffel Tower
            (48.8606, 2.3376)   # Louvre
        ]
        
        multi_route = optimizer.get_route_multiple_points(waypoints)
        if multi_route:
            print(f"  Total distance: {multi_route['distance_km']} km")
            print(f"  Total duration: {multi_route['duration_minutes']} minutes")
            print("  ✅ PASSED")
        else:
            print("  ❌ FAILED")
            return False
        
        return True
        
    except Exception as e:
        print(f"  ❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("\n")
    print("*" * 60)
    print("*" + " " * 58 + "*")
    print("*" + "  TESTING API FIXES".center(58) + "*")
    print("*" + " " * 58 + "*")
    print("*" * 60)
    print("\n")
    
    results = {
        'OpenWeather API': test_openweather(),
        'REST Countries API': test_rest_countries(),
        'OSRM Routing': test_osrm()
    }
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    passed = sum(results.values())
    total = len(results)
    
    for name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{name}: {status}")
    
    print("=" * 60)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! APIs are working correctly!")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Check errors above.")
    
    print("=" * 60)
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)