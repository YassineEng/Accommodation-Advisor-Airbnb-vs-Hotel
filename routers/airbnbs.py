# routers/airbnbs.py
# This file defines API endpoints related to finding Airbnbs based on hotel locations.

from fastapi import APIRouter, HTTPException, Query
from services.geocoding_service import get_coordinates_for_hotel
from services.database_service import execute_query
from schemas.response_models import AirbnbResponse, AirbnbSearchResponse
from haversine import haversine, Unit
from typing import List

# Create an API router for Airbnb-related endpoints.
router = APIRouter()

# Define the API endpoint to find Airbnbs near a specified hotel.
# This endpoint expects a hotel name, city, and a search radius.
@router.get("/find_airbnbs_near_hotel", response_model=AirbnbSearchResponse)
def find_airbnbs_near_hotel(
    hotel_name: str = Query(..., description="Name of the hotel"),
    city: str = Query(..., description="City of the hotel"),
    radius_km: int = Query(..., description="Radius in kilometers")
):
    # Step 1: Get the geographical coordinates (latitude and longitude) of the specified hotel.
    # This uses an external geocoding service (e.g., Nominatim).
    origin_latitude, origin_longitude = get_coordinates_for_hotel(hotel_name, city)
    
    # If the hotel's coordinates cannot be found, raise an HTTP 404 Not Found error.
    if not origin_latitude or not origin_longitude:
        raise HTTPException(status_code=404, detail="Hotel not found")

    # Step 2: Query the database for all relevant Airbnb listings.
    # It selects listings that are marked as 'local host', and have valid latitude/longitude.
    query = """
        SELECT
            listing_id, host_name, property_city, latitude, longitude, price, review_scores_rating
        FROM
            dim_listings
        WHERE
            is_local_host = 1 AND latitude IS NOT NULL AND longitude IS NOT NULL
    """
    
    all_listings = execute_query(query)
    
    nearby_listings = []
    # Step 3: Iterate through all listings and calculate their distance from the origin hotel.
    for listing in all_listings:
        listing_lat = float(listing['latitude'])
        listing_lon = float(listing['longitude'])
        
        # Calculate the distance between the hotel and the Airbnb listing using the Haversine formula.
        distance = haversine((origin_latitude, origin_longitude), (listing_lat, listing_lon), unit=Unit.KILOMETERS)
        
        # If the listing is within the specified radius, add it to the list of nearby listings.
        if distance <= radius_km:
            nearby_listings.append(
                {
                    "name": listing['host_name'],
                    "latitude": listing_lat,
                    "longitude": listing_lon,
                    "price": listing['price'],
                    "rating": listing['review_scores_rating'],
                    "distance_km": distance,
                    "listing_url": f"https://www.airbnb.com/rooms/{listing['listing_id']}" # Construct Airbnb URL
                }
            )
            
    # Step 4: Sort the nearby listings.
    # First, sort by distance in ascending order.
    sorted_by_distance = sorted(nearby_listings, key=lambda x: x['distance_km'])

    # Then, sort by rating in descending order. Listings with no rating (None) are placed at the end.
    sorted_by_rating_and_distance = sorted(
        sorted_by_distance,
        key=lambda x: (x['rating'] is not None, x['rating']),
        reverse=True
    )

    # Step 5: Take the top 10 listings after sorting.
    airbnbs = sorted_by_rating_and_distance[:10]

    # Step 6: Return the results, including the origin hotel's coordinates and the list of nearby Airbnbs.
    return {
        "origin_latitude": origin_latitude,
        "origin_longitude": origin_longitude,
        "airbnbs": airbnbs
    }
