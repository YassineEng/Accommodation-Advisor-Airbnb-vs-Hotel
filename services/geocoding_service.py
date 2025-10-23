# services/geocoding_service.py
# This file provides functionalities for geographical lookups and finding nearby hotels
# using external APIs like Nominatim for geocoding and Overpass API for OpenStreetMap data.

import requests
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
import logging

# Configure logging for this service.
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize Nominatim Geocoding API client.
# A unique user_agent is required for Nominatim requests.
geolocator = Nominatim(user_agent="accommodation-advisor-app")

# Function to get latitude and longitude for a given hotel name and city.
# Uses Nominatim to convert a human-readable address into geographical coordinates.
def get_coordinates_for_hotel(hotel_name: str, city: str):
    try:
        location_str = f"{hotel_name}, {city}"
        logger.info(f"Nominatim Geocode Query: {location_str}")
        # Attempt to geocode the location string with a timeout.
        location = geolocator.geocode(location_str, timeout=5)
        if location:
            logger.info(f"Nominatim Geocode Result: Lat={location.latitude}, Lon={location.longitude}")
            return location.latitude, location.longitude
        else:
            logger.warning(f"Nominatim Geocode Result: No location found for {location_str}")
    except (GeocoderTimedOut, GeocoderServiceError) as e:
        # Log any errors encountered during geocoding.
        logger.error(f"Error geocoding {hotel_name}, {city}: {e}")
    return None, None

# Function to find hotels near specified coordinates within a given radius.
# Uses the Overpass API to query OpenStreetMap data.
def find_hotels_near_coordinates(latitude: float, longitude: float, radius_km: int):
    overpass_url = "http://overpass-api.de/api/interpreter"
    
    # Calculate approximate latitude and longitude differences for the bounding box
    # based on the given radius. This creates a square search area around the central point.
    lat_diff = radius_km / 111.0 # Approximately 111 km per degree of latitude
    lon_diff = radius_km / (111.0 * abs(latitude)) # Longitude degrees vary with latitude

    # Construct the Overpass API query.
    # It searches for nodes, ways, and relations tagged as various types of tourism lodging
    # within the calculated bounding box. The 'out center tags;' ensures that tags
    # and the center coordinates for ways/relations are included in the output.
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
        # Send the query to the Overpass API.
        response = requests.post(overpass_url, data=overpass_query, timeout=10)
        logger.info(f"Overpass API Response Status: {response.status_code}")
        # Log the full JSON response for debugging purposes.
        logger.info(f"Overpass API Response JSON: {response.json()}")
        response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx).
        data = response.json()
        
        hotels = []
        # Process each element received from the Overpass API.
        for element in data.get('elements', []):
            # Extract latitude and longitude based on element type (node, way, or relation).
            if element['type'] == 'node':
                lat = element['lat']
                lon = element['lon']
            elif element['type'] == 'way' or element['type'] == 'rel':
                # For ways and relations, use the 'center' coordinates if available.
                if 'center' in element:
                    lat = element['center']['lat']
                    lon = element['center']['lon']
                else:
                    continue # Skip if no center defined for way/rel (cannot map it).
            else:
                continue # Skip unknown element types.

            # Safely extract the name and website URL from the element's tags.
            # If 'name' tag is missing or empty, skip the element to avoid "Unnamed Lodging".
            name = element.get('tags', {}).get('name')
            if not name: 
                continue
            # Prioritize 'website' tag, fall back to 'contact:website' if 'website' is not present.
            website = element.get('tags', {}).get('website') or element.get('tags', {}).get('contact:website')
            
            # Append the extracted hotel information to the list.
            hotels.append({
                "name": name,
                "latitude": lat,
                "longitude": lon,
                "price": None, # Price is not typically available from Overpass API.
                "rating": None, # Rating is not typically available from Overpass API.
                "website_url": website # Website URL, if found.
            })
        return hotels
    except requests.exceptions.RequestException as e:
        # Log any errors encountered during the Overpass API request.
        logger.error(f"Error querying Overpass API: {e}")
    return []