from googlesearch import search

query = "Hospital near 19.044164141318113 72.82141979702497"
num_results = 5  # You can adjust the number of results as needed

# Perform the Google search and limit the number of results using enumerate
results = list(search(query, num_results=num_results))

# Print the search results
for i, result in enumerate(results, start=1):
    print(f"{i}. {result}")


""" import requests

# Specify the coordinates (latitude and longitude)
latitude = 19.044164141318113
longitude = 72.82141979702497

# Nominatim API endpoint
nominatim_url = "https://nominatim.openstreetmap.org/search"

# Parameters for the search request
params = {
    'format': 'json',
    'lat': latitude,
    'lon': longitude,
    'radius': 5000,  # Adjust the radius as needed (in meters)
    'q': 'hospital',  # Search term for hospitals
}

# Perform the search request
response = requests.get(nominatim_url, params=params)
data = response.json()

print(data)

# Print the hospital information
for place in data:
    print(place['display_name'])
 """

""" import requests

# Replace 'YOUR_MAPBOX_ACCESS_TOKEN' with your actual Mapbox API access token
mapbox_access_token = 'pk.eyJ1Ijoic3BpZHk4NjU1IiwiYSI6ImNscnJwb3l2bDAweXUya3FlM3RhcWNuNTIifQ.SbKps1pbouNlb8Ws6fcHqA'

# Specify the coordinates (latitude and longitude)
latitude = 19.044164141318113
longitude = 72.82141979702497

# Mapbox Geocoding API endpoint
mapbox_geocoding_url = "https://api.mapbox.com/geocoding/v5/mapbox.places/"

mapbox_geocoding_url = f'https://api.mapbox.com/v4/mapbox.mapbox-streets-v8/tilequery/{longitude},{latitude}.json?limit=50&radius=1000&layers=building&dedupe=true&access_token={mapbox_access_token}'
# Perform the search request
response = requests.get(mapbox_geocoding_url)
data = response.json()
print(data) """