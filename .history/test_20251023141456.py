import requests

# -------------------------------
# 1️⃣ Find Airbnbs near a Hotel
# -------------------------------
hotel_name = "Hilton"
city = "London"
radius_km = 5

airbnb_url = f"http://localhost:8000/find_airbnbs_near_hotel?hotel_name={hotel_name}&city={city}&radius_km={radius_km}"

response_airbnb = requests.get(airbnb_url)
if response_airbnb.status_code == 200:
    airbnb_results = response_airbnb.json()  # assuming API returns JSON
    print(f"Airbnbs near {hotel_name} in {city} ({radius_km} km):")
    for a in airbnb_results:
        print(f"- {a['name']} | {a.get('address', 'No address')}")
else:
    print("Error fetching Airbnbs:", response_airbnb.text)

# -------------------------------
# 2️⃣ Find Hotels near an Airbnb
# -------------------------------
listing_url = "https://www.airbnb.com/rooms/1234567890"
radius_km = 10

hotel_search_url = f"http://localhost:8000/find_hotels_near_airbnb?listing_url={listing_url}&radius_km={radius_km}"

response_hotels = requests.get(hotel_search_url)
if response_hotels.status_code == 200:
    hotel_results = response_hotels.json()  # assuming API returns JSON
    print(f"\nHotels near Airbnb {listing_url} ({radius_km} km):")
    for h in hotel_results:
        print(f"- {h['name']} | {h.get('address', 'No address')}")
else:
    print("Error fetching Hotels:", response_hotels.text)
