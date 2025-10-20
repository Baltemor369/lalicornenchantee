from geopy.geocoders import Nominatim
from geopy.distance import geodesic

geolocator = Nominatim(user_agent="equiconfort")
_ = geolocator.geocode("flavigny, 57130, France")
Centre1 = (_.latitude, _.longitude)
print(Centre1)