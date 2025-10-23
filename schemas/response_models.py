# schemas/response_models.py
# This file defines the Pydantic models used for validating and structuring API requests and responses.
# These models ensure data consistency and provide automatic documentation for the API.

from pydantic import BaseModel
from typing import List, Optional

# Pydantic model for a single Airbnb listing's details.
class AirbnbResponse(BaseModel):
    name: str
    latitude: float
    longitude: float
    price: Optional[float] # Optional as price might not always be available.
    rating: Optional[float] # Optional as rating might not always be available.
    distance_km: float
    listing_url: Optional[str] # Optional as URL might not always be available.

# Pydantic model for the response when searching for Airbnbs near a hotel.
# Includes the origin hotel's coordinates and a list of nearby Airbnbs.
class AirbnbSearchResponse(BaseModel):
    origin_latitude: float
    origin_longitude: float
    airbnbs: List[AirbnbResponse]

# Pydantic model for a single hotel's details.
class HotelResponse(BaseModel):
    name: str
    latitude: float
    longitude: float
    price: Optional[float] # Optional as price might not always be available.
    rating: Optional[float] # Optional as rating might not always be available.
    distance_km: float
    website_url: Optional[str] = None # Optional, with a default of None if not provided.

# Pydantic model for the response when searching for hotels near an Airbnb.
# Includes the origin Airbnb's coordinates and a list of nearby hotels.
class HotelSearchResponse(BaseModel):
    origin_latitude: float
    origin_longitude: float
    hotels: List[HotelResponse]
