import requests
import json

url = "https://api.zerobounce.net/v2/validate"
api_key = ""
email = ""
ip_address = "" #ip_address can be blank
print(type(api_key))
params = {"email": email, "api_key": api_key, "ip_address":ip_address}

response = requests.get(url, params=params)

# Print the returned json
print (json.loads(response.content))
