from geopy.geocoders import Nominatim

# Define your coordinates
latitude = 19.044164141318113
longitude = 72.82141979702497

# Set up Nominatim geocoder
geolocator = Nominatim(user_agent="your_app_name")

# Get the address details from coordinates
location = geolocator.reverse((latitude, longitude), language="en")

# Extract relevant address components
address = location.raw.get('address', {})
city = address.get('city')
suburb = address.get('suburb')
neighborhood = address.get('neighbourhood')
locality = address.get('locality')
amenity = address.get('amenity')

# Print the extracted information
print("Amenity:",amenity)
print("City:", city)
print("Suburb:", suburb)
print("Neighborhood:", neighborhood)
print("Locality:", locality)
