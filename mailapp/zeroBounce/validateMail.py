import requests
import json

def validateMail(api_key,email):
    url = "https://api.zerobounce.net/v2/validate"
    api_key = api_key
    email = email
    ip_address = "99.123.12.122"

    params = {"email": email, "api_key": api_key, "ip_address":ip_address}

    response = requests.get(url, params=params)
    return json.loads(response.content)
