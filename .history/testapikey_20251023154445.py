import requests

API_KEY = "YOUR_API_KEY"
latitude = 51.5074
longitude = 0.1278
radius = 500
place_type = "hotel"

url = (
    f"https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    f"?location={latitude},{longitude}&radius={radius}&type={place_type}&key={API_KEY}"
)

response = requests.get(url)
data = response.json()

if data.get("status") == "OK":
    print("API key is working! Sample results:")
    for place in data["results"][:5]:  # show first 5 results
        print(place.get("name"), "|", place.get("vicinity"))
else:
    print("API key test failed:", data.get("status"), data.get("error_message"))
