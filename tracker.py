import os
import ssl
import time
import certifi
import requests
import reverse_geocoder as rg
from geopy.geocoders import Nominatim
from geopy.distance import geodesic

# Simple manual parser for .env files to avoid installing third-party dotenv packages
if os.path.exists(".env"):
    try:
        with open(".env", "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, val = line.split("=", 1)
                    os.environ[key.strip()] = val.strip()
    except Exception as e:
        print(f"Error loading .env file: {e}")

# APOD Caching
apod_cache = {
    "url": None,
    "timestamp": 0
}

def get_ocean_name(lat, lon):
    """
    Returns the name of the ocean or sea based on latitude and longitude.
    This is a simplified approximation using bounding boxes.
    """
    # 1. Polar Regions
    if lat > 65:
        return "Arctic Ocean"
    if lat < -60:
        return "Southern Ocean"
    
    # 2. Specific Seas (Rough Bounding Boxes)
    
    # Mediterranean Sea (Approx: 30N to 46N, 5.5W to 36E)
    if 30 <= lat <= 46 and -6 <= lon <= 36:
        return "Mediterranean Sea"

    # Gulf of Mexico (Approx: 20N to 30N, 98W to -80W)
    if 18 <= lat <= 30 and -98 <= lon <= -80:
        return "Gulf of Mexico"

    # Caribbean Sea (Approx: 9N to 22N, 89W to 60W)
    if 9 <= lat <= 22 and -89 <= lon <= -60:
        return "Caribbean Sea"

    # Red Sea (Approx)
    if 12 <= lat <= 30 and 32 <= lon <= 43:
        return "Red Sea"

    # Black Sea
    if 40 <= lat <= 47 and 27 <= lon <= 42:
        return "Black Sea"
        
    # Baltic Sea
    if 53 <= lat <= 66 and 10 <= lon <= 30:
        return "Baltic Sea"
    
    # Bering Sea (North Pacific Check)
    if 50 <= lat <= 65 and (lon > 160 or lon < -160):
        return "Bering Sea"
        
    # Sea of Japan (East Sea)
    if 35 <= lat <= 50 and 127 <= lon <= 142:
        return "Sea of Japan"

    # South China Sea
    if 0 <= lat <= 23 and 100 <= lon <= 120:
        return "South China Sea"

    # 3. Major Oceans
    
    # Atlantic Ocean: roughly between -80 (Americas) and 20 (Europe/Africa)
    if -80 <= lon <= 20:
        return "Atlantic Ocean"
        
    # Indian Ocean: roughly between 20 (Africa) and 120/146 (Australia/Indonesia)
    if 20 < lon <= 120:
        return "Indian Ocean"
    # Handling the gap around Australia (120 to 146) - usually Indian if South of Aus
    if 120 < lon <= 146 and lat < -10:
        return "Indian Ocean"

    # Pacific Ocean: The rest
    return "Pacific Ocean"


def get_apod_url():
    """
    Fetches the NASA Astronomy Picture of the Day.
    Caches the URL for 1 hour to avoid aggressive API hits.
    """
    current_time = time.time()
    if apod_cache["url"] and (current_time - apod_cache["timestamp"] < 3600):
        return apod_cache["url"]

    # Fallback to the provided key, or use env key if specified
    api_key = os.environ.get("NASA_API_KEY", "E94WTVyQtaJuQQvcfoOh5MbBBZsegjqzOIJ12yPc")
    url = f"https://api.nasa.gov/planetary/apod?api_key={api_key}"
    
    # Fallback image (NASA generic space image)
    fallback_url = "https://www.nasa.gov/sites/default/files/styles/full_width_feature/public/thumbnails/image/orion-nebula-xl.jpg"

    try:
        r = requests.get(url, timeout=5)
        r.raise_for_status()
        data = r.json()
        if "url" in data:
            apod_cache["url"] = data["url"]
            apod_cache["timestamp"] = current_time
            return data["url"]
    except Exception as e:
        print(f"Error fetching APOD: {e}")
    
    if apod_cache["url"]: 
        return apod_cache["url"]

    return fallback_url


def get_iss_location():
    """
    Fetches current ISS position.
    Returns (latitude, longitude, error_message).
    """
    try:
        r = requests.get(url="http://api.open-notify.org/iss-now.json", timeout=10)
        r.raise_for_status()
        data = r.json()
    except Exception as e:
        return None, None, str(e)

    lat = float(data["iss_position"]["latitude"])
    lon = float(data["iss_position"]["longitude"])

    return lat, lon, None


def get_location_details(lat, lon):
    """
    Reverse geocodes coordinates to see if they are over/near land.
    Finds nearest landmass offline as a fallback.
    """
    result = {
        'lat': lat,
        'lon': lon,
        'precise_location': None,
        'nearest_land': None,
        'ocean': None,
        'error': None
    }

    # 1. Try Detailed Address (Nominatim)
    ctx = ssl.create_default_context(cafile=certifi.where())
    geolocator = Nominatim(user_agent="iss_tracker_app", ssl_context=ctx)

    try:
        location = geolocator.reverse(f"{lat}, {lon}", language="en", timeout=10)
    except Exception:
        location = None

    if location:
        addr = location.raw.get("address", {})
        city = addr.get("city") or addr.get("town") or addr.get("village") or addr.get("hamlet")
        state = addr.get("state")
        country = addr.get("country")

        result['precise_location'] = {
            'address': location.address,
            'city': city,
            'state': state,
            'country': country
        }

    # 2. Find Nearest Land (Reverse Geocoder - Offline)
    try:
        results = rg.search((lat, lon))
        if results:
            nearest = results[0]
            place_name = nearest.get('name')
            admin1 = nearest.get('admin1')
            cc = nearest.get('cc')

            nearest_lat = float(nearest.get('lat'))
            nearest_lon = float(nearest.get('lon'))

            distance_km = geodesic((lat, lon), (nearest_lat, nearest_lon)).km

            result['nearest_land'] = {
                'distance': round(distance_km, 2),
                'place_name': place_name,
                'admin1': admin1,
                'cc': cc
            }
    except Exception as e:
        result['error'] = str(e)

    # 3. Identify Ocean/Sea
    result['ocean'] = get_ocean_name(lat, lon)

    return result


# Combined ISS Position & Geocoding Cache (to safeguard Nominatim usage limits)
iss_state_cache = {
    "data": None,
    "timestamp": 0
}

def get_cached_iss_state():
    """
    Returns the current ISS location and geocoded info.
    Throttles request volume by caching combined state for 5 seconds.
    """
    current_time = time.time()
    
    if iss_state_cache["data"] and (current_time - iss_state_cache["timestamp"] < 5):
        return iss_state_cache["data"]

    lat, lon, error = get_iss_location()
    if error:
        if iss_state_cache["data"]:
            # Serves slightly stale data rather than returning error
            return iss_state_cache["data"]
        return {
            "lat": None,
            "lon": None,
            "location_data": None,
            "error": error
        }

    location_data = get_location_details(lat, lon)
    
    state = {
        "lat": lat,
        "lon": lon,
        "location_data": location_data,
        "error": None
    }
    
    iss_state_cache["data"] = state
    iss_state_cache["timestamp"] = current_time
    return state
