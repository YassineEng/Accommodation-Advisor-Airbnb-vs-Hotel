from fastapi import APIRouter, HTTPException, Query
from services.geocoding_service import get_coordinates_for_hotel
from services.database_service import execute_query
from schemas.response_models import AirbnbResponse
from haversine import haversine, Unit
from typing import List

router = APIRouter()

@router.get("/find_airbnbs_near_hotel", response_model=List[AirbnbResponse])
def find_airbnbs_near_hotel(
    hotel_name: str = Query(..., description="Name of the hotel"),
    city: str = Query(..., description="City of the hotel"),
    radius_km: int = Query(..., description="Radius in kilometers")
):
    latitude, longitude = get_coordinates_for_hotel(hotel_name, city)
    if not latitude or not longitude:
        raise HTTPException(status_code=404, detail="Hotel not found")

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
    for listing in all_listings:
        listing_lat = float(listing['latitude'])
        listing_lon = float(listing['longitude'])
        distance = haversine((latitude, longitude), (listing_lat, listing_lon), unit=Unit.KILOMETERS)
        if distance <= radius_km:
            nearby_listings.append(
                {
                    "name": listing['host_name'],
                    "latitude": listing_lat,
                    "longitude": listing_lon,
                    "price": listing['price'],
                    "rating": listing['review_scores_rating'],
                    "distance_km": distance
                }
            )
            
    # Sort by distance first (ascending)
    sorted_by_distance = sorted(nearby_listings, key=lambda x: x['distance_km'])

    # Then sort by rating (descending), placing None ratings at the end
    sorted_by_rating_and_distance = sorted(
        sorted_by_distance,
        key=lambda x: (x['rating'] is not None, x['rating']),
        reverse=True
    )

    # Take the top 10
    top_ten_listings = sorted_by_rating_and_distance[:10]

    return top_ten_listings
