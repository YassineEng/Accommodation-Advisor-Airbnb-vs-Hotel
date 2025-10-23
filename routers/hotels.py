from fastapi import APIRouter, HTTPException, Query
from services.geocoding_service import find_hotels_near_coordinates
from services.database_service import execute_query
from schemas.response_models import HotelResponse, HotelSearchResponse
from haversine import haversine, Unit
import re
from typing import List

router = APIRouter()

def get_listing_id_from_url(url: str):
    match = re.search(r"/rooms/(\d+)", url)
    if match:
        return match.group(1)
    return None

@router.get("/find_hotels_near_airbnb", response_model=HotelSearchResponse)
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
        raise HTTPException(status_code=404, detail="Property not included in our database.")

    origin_latitude = float(results[0]['latitude'])
    origin_longitude = float(results[0]['longitude'])

    hotels = find_hotels_near_coordinates(origin_latitude, origin_longitude, radius_km)

    nearby_hotels = []
    for hotel in hotels:
        hotel_lat = hotel['latitude']
        hotel_lon = hotel['longitude']
        distance = haversine((origin_latitude, origin_longitude), (hotel_lat, hotel_lon), unit=Unit.KILOMETERS)
        nearby_hotels.append(
            {
                "name": hotel['name'],
                "latitude": hotel_lat,
                "longitude": hotel_lon,
                "price": hotel.get('price'),
                "rating": hotel.get('rating'),
                "distance_km": distance,
                "website_url": hotel.get('website_url')
            }
        )

    sorted_hotels = sorted(nearby_hotels, key=lambda x: x['distance_km'])

    return {
        "origin_latitude": origin_latitude,
        "origin_longitude": origin_longitude,
        "hotels": sorted_hotels
    }