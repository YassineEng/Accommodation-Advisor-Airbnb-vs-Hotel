from pydantic import BaseModel
from typing import Optional

class AirbnbResponse(BaseModel):
    name: str
    latitude: float
    longitude: float
    price: Optional[float]
    rating: Optional[float]
    distance_km: float

class HotelResponse(BaseModel):
    name: str
    latitude: float
    longitude: float
    price: Optional[float]
    rating: Optional[float]
    distance_km: float
