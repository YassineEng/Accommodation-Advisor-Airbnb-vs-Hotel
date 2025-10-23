# routers/hotels.py
# This file defines API endpoints related to finding hotels based on Airbnb listing locations.

from fastapi import APIRouter, HTTPException, Query
from services.geocoding_service import find_hotels_near_coordinates
from services.database_service import execute_query
from schemas.response_models import HotelResponse, HotelSearchResponse
from haversine import haversine, Unit
import re
from typing import List

# Create an API router for hotel-related endpoints.
router = APIRouter()

# Helper function to extract the Airbnb listing ID from a given URL.
# Uses regular expressions to find the numeric ID in the URL path.
def get_listing_id_from_url(url: str):
    match = re.search(r"/rooms/(\d+)", url)
    if match:
        return match.group(1)
    return None

# Define the API endpoint to find hotels near a specified Airbnb listing.
# This endpoint expects an Airbnb listing URL and a search radius.
@router.get("/find_hotels_near_airbnb", response_model=HotelSearchResponse)
def find_hotels_near_airbnb(
    listing_url: str = Query(..., description="URL of the Airbnb listing"),
    radius_km: int = Query(..., description="Radius in kilometers")
):
    # Step 1: Extract the listing ID from the provided Airbnb URL.
    listing_id = get_listing_id_from_url(listing_url)
    
    # If no valid listing ID can be extracted, raise an HTTP 400 Bad Request error.
    if not listing_id:
        raise HTTPException(status_code=400, detail="Invalid Airbnb listing URL")

    # Step 2: Query the database to get the geographical coordinates (latitude and longitude)
    # of the specified Airbnb listing.
    query = """
        SELECT
            latitude, longitude
        FROM
            dim_listings
        WHERE
            listing_id = ?
    """
    
    results = execute_query(query, (listing_id,))
    
    # If the Airbnb listing is not found in the database, raise an HTTP 404 Not Found error.
    if not results:
        raise HTTPException(status_code=404, detail="Property not included in our database.")

    # Extract the origin (Airbnb) coordinates.
    origin_latitude = float(results[0]['latitude'])
    origin_longitude = float(results[0]['longitude'])

    # Step 3: Find nearby hotels using an external geocoding service (Overpass API).
    # This function filters hotels based on the origin coordinates and radius.
    hotels = find_hotels_near_coordinates(origin_latitude, origin_longitude, radius_km)

    nearby_hotels = []
    # Step 4: Calculate the distance of each found hotel from the origin Airbnb.
    for hotel in hotels:
        hotel_lat = hotel['latitude']
        hotel_lon = hotel['longitude']
        
        # Calculate the distance using the Haversine formula.
        distance = haversine((origin_latitude, origin_longitude), (hotel_lat, hotel_lon), unit=Unit.KILOMETERS)
        
        # Append the hotel details, including the calculated distance and website URL.
        nearby_hotels.append(
            {
                "name": hotel['name'],
                "latitude": hotel_lat,
                "longitude": hotel_lon,
                "price": hotel.get('price'),
                "rating": hotel.get('rating'),
                "distance_km": distance,
                "website_url": hotel.get('website_url') # Include website URL if available
            }
        )

    # Step 5: Sort the nearby hotels by distance in ascending order.
    sorted_hotels = sorted(nearby_hotels, key=lambda x: x['distance_km'])

    # Step 6: Return the results, including the origin Airbnb's coordinates and the list of nearby hotels.
    return {
        "origin_latitude": origin_latitude,
        "origin_longitude": origin_longitude,
        "hotels": sorted_hotels
    }