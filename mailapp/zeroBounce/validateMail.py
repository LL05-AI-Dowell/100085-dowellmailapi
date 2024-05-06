import requests
import json

def validateMail(api_key, email):
    url = "https://api.zerobounce.net/v2/validate"
    ip_address = "99.123.12.122"

    params = {"email": email, "api_key": api_key, "ip_address": ip_address}

    response = requests.get(url, params=params)
    if response.status_code == 200:
        response_data = json.loads(response.text)
        if response_data["status"] == "valid" or response_data["status"] == "do_not_mail":
            return {"status": "valid"}
        else:
            return {"status": "Invalid or risky email"}
    else:
        return {"status": "Something went wrong"}

def emailFinder(api_key, domain, name):
    url = "https://api.zerobounce.net/v2/guessformat"
    params = {"api_key": api_key, "domain": domain, "first_name": name}
    response = requests.get(url, params=params)
    return json.loads(response.content)