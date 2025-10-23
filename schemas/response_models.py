from pydantic import BaseModel
from typing import List, Optional

class AirbnbResponse(BaseModel):
    name: str
    latitude: float
    longitude: float
    price: Optional[float]
    rating: Optional[float]
    distance_km: float
    listing_url: Optional[str]

class AirbnbSearchResponse(BaseModel):
    origin_latitude: float
    origin_longitude: float
    airbnbs: List[AirbnbResponse]

class HotelResponse(BaseModel):
    name: str
    latitude: float
    longitude: float
    price: Optional[float]
    rating: Optional[float]
    distance_km: float
    website_url: Optional[str] = None

class HotelSearchResponse(BaseModel):
    origin_latitude: float
    origin_longitude: float
    hotels: List[HotelResponse]
