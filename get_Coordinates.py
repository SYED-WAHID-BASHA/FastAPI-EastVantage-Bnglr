import requests

# api for getting coordinates

# API Secret Key
coordinateApiKey = "eblFYOGlOuT92AtjjJRE4WiznNh81GGM"

# API end point with query ?location=
coordinateApi = f"http://www.mapquestapi.com/geocoding/v1/address?key={coordinateApiKey}&location="


# it returns the address information along with coordinates and address 

# It's take 3 parameter and use them as location query for api 

def getCoordinate(name, addressLine, city, state):
    mainCoordinateApi = f" {coordinateApi}{addressLine},{city},{state}"
    r = requests.get(mainCoordinateApi)
    locationData = r.json()["results"][0]["locations"][0]
    return locationData