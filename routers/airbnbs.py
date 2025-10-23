from fastapi import APIRouter, HTTPException, Query
from services.geocoding_service import find_hotels_near_coordinates
from services.database_service import execute_query
from schemas.response_models import HotelResponse
from haversine import haversine, Unit
import re
from typing import List

router = APIRouter()

def get_listing_id_from_url(url: str):
    match = re.search(r"/rooms/(\d+)", url)
    if match:
        return match.group(1)
    return None

@router.get("/find_hotels_near_airbnb", response_model=List[HotelResponse])
def find_hotels_near_airbnb(
    listing_url: str = Query(..., description="URL of the Airbnb listing"),
    radius_km: int = Query(..., description="Radius in kilometers")
):
    listing_id = get_listing_id_from_url(listing_url)
    if not listing_id:
        raise HTTPException(status_code=400, detail="Invalid Airbnb listing URL")

    query = """
        SELECT
            latitude, longitude
        FROM
            dim_listings
        WHERE
            listing_id = ?
    """
    
    results = execute_query(query, (listing_id,))
    
    if not results:
        raise HTTPException(status_code=404, detail="Airbnb listing not found")

    airbnb_lat = float(results[0]['latitude'])
    airbnb_lon = float(results[0]['longitude'])

    hotels = find_hotels_near_coordinates(airbnb_lat, airbnb_lon, radius_km)

    nearby_hotels = []
    for hotel in hotels:
        hotel_lat = hotel['latitude']
        hotel_lon = hotel['longitude']
        distance = haversine((airbnb_lat, airbnb_lon), (hotel_lat, hotel_lon), unit=Unit.KILOMETERS)
        nearby_hotels.append(
            {
                "name": hotel['name'],
                "latitude": hotel_lat,
                "longitude": hotel_lon,
                "price": hotel.get('price'),
                "rating": hotel.get('rating'),
                "distance_km": distance
            }
        )

    sorted_hotels = sorted(nearby_hotels, key=lambda x: x['distance_km'])

    return sorted_hotels