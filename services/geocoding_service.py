import requests
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize Nominatim API
geolocator = Nominatim(user_agent="accommodation-advisor-app")

def get_coordinates_for_hotel(hotel_name: str, city: str):
    try:
        location_str = f"{hotel_name}, {city}"
        logger.info(f"Nominatim Geocode Query: {location_str}")
        location = geolocator.geocode(location_str, timeout=5)
        if location:
            logger.info(f"Nominatim Geocode Result: Lat={location.latitude}, Lon={location.longitude}")
            return location.latitude, location.longitude
        else:
            logger.warning(f"Nominatim Geocode Result: No location found for {location_str}")
    except (GeocoderTimedOut, GeocoderServiceError) as e:
        logger.error(f"Error geocoding {hotel_name}, {city}: {e}")
    return None, None

def find_hotels_near_coordinates(latitude: float, longitude: float, radius_km: int):
    # Overpass API for finding nearby lodging
    overpass_url = "http://overpass-api.de/api/interpreter"
    lat_diff = radius_km / 111.0
    lon_diff = radius_km / (111.0 * abs(latitude))

    overpass_query = f"""
        [out:json];
        (
            node["tourism"~"hotel|hostel|motel|guest_house|chalet|resort|apartment"](
                {latitude - lat_diff}, {longitude - lon_diff}, 
                {latitude + lat_diff}, {longitude + lon_diff}
            );
            way["tourism"~"hotel|hostel|motel|guest_house|chalet|resort|apartment"](
                {latitude - lat_diff}, {longitude - lon_diff}, 
                {latitude + lat_diff}, {longitude + lon_diff}
            );
            rel["tourism"~"hotel|hostel|motel|guest_house|chalet|resort|apartment"](
                {latitude - lat_diff}, {longitude - lon_diff}, 
                {latitude + lat_diff}, {longitude + lon_diff}
            );
        );
        (._;>;);
        out center tags;
    """
    logger.info(f"Overpass API Query: {overpass_query}")

    try:
        response = requests.post(overpass_url, data=overpass_query, timeout=10)
        logger.info(f"Overpass API Response Status: {response.status_code}")
        logger.info(f"Overpass API Response JSON: {response.json()}")
        response.raise_for_status()
        data = response.json()
        
        hotels = []
        for element in data.get('elements', []):
            if element['type'] == 'node':
                lat = element['lat']
                lon = element['lon']
            elif element['type'] == 'way' or element['type'] == 'rel':
                if 'center' in element:
                    lat = element['center']['lat']
                    lon = element['center']['lon']
                else:
                    continue # Skip if no center defined for way/rel
            else:
                continue

            name = element.get('tags', {}).get('name')
            if not name: # Skip if name is None or empty
                continue
            website = element.get('tags', {}).get('website') or element.get('tags', {}).get('contact:website')
            hotels.append({
                "name": name,
                "latitude": lat,
                "longitude": lon,
                "price": None, # Not available from Overpass API
                "rating": None, # Not available from Overpass API
                "website_url": website
            })
        return hotels
    except requests.exceptions.RequestException as e:
        logger.error(f"Error querying Overpass API: {e}")
    return []