# Accommodation Advisor

Accommodation Advisor is a FastAPI-based web service that helps users find the best accommodation options by comparing Airbnb listings and hotels.

## Features

*   **Find Airbnbs near a hotel**: Given a hotel name and city, find the top 10 nearby Airbnb listings.
*   **Find hotels near an Airbnb**: Given an Airbnb listing URL, find nearby hotels.

## API Endpoints

### GET /find_airbnbs_near_hotel

Finds Airbnbs near a specified hotel.

**Query Parameters:**

*   `hotel_name` (str, required): The name of the hotel.
*   `city` (str, required): The city where the hotel is located.
*   `radius_km` (int, required): The search radius in kilometers.

**Example Request:**

```
GET /find_airbnbs_near_hotel?hotel_name=The%20Ritz-Carlton&city=London&radius_km=5
```

**Example Response:**

```json
{
  "origin_latitude": 51.5074,
  "origin_longitude": -0.1278,
  "airbnbs": [
    {
      "name": "Charming Flat in Covent Garden",
      "latitude": 51.5112,
      "longitude": -0.1256,
      "price": 150,
      "rating": 4.8,
      "distance_km": 0.5,
      "listing_url": "https://www.airbnb.com/rooms/123456"
    }
  ]
}
```

### GET /find_hotels_near_airbnb

Finds hotels near a specified Airbnb listing.

**Query Parameters:**

*   `listing_url` (str, required): The URL of the Airbnb listing.
*   `radius_km` (int, required): The search radius in kilometers.

**Example Request:**

```
GET /find_hotels_near_airbnb?listing_url=https://www.airbnb.com/rooms/123456&radius_km=5
```

**Example Response:**

```json
{
  "origin_latitude": 51.5112,
  "origin_longitude": -0.1256,
  "hotels": [
    {
      "name": "The Savoy",
      "latitude": 51.5101,
      "longitude": -0.1208,
      "price": null,
      "rating": null,
      "distance_km": 0.4,
      "website_url": "https://www.thesavoylondon.com/"
    }
  ]
}
```

## Technologies Used

*   [Python](https://www.python.org/)
*   [FastAPI](https://fastapi.tiangolo.com/)
*   [Haversine](https://pypi.org/project/haversine/)
*   [uv](https://github.com/astral-sh/uv)

## Installation and Usage

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/your-username/Accommodation-Advisor-Airbnb-vs-Hotel.git
    cd Accommodation-Advisor-Airbnb-vs-Hotel
    ```

2.  **Install dependencies:**

    ```bash
    uv pip install -r requirements.txt
    ```
    
    *Note: A `requirements.txt` file is not yet present in the project. You can create one using `uv pip freeze > requirements.txt` after installing the dependencies manually.*


3.  **Create a `.env` file:**

    Create a `.env` file in the root directory and add the necessary environment variables (e.g., database credentials, API keys).

4.  **Run the application:**

    ```bash
    uvicorn main:app --reload --port 8001
    ```

    The application will be available at `http://127.0.0.1:8001`.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.