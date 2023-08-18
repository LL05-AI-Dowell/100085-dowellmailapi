import requests
import json

def validateMail(api_key,email):
    url = "https://api.zerobounce.net/v2/validate"
    api_key = api_key
    email = email
    ip_address = "99.123.12.122"

    params = {"email": email, "api_key": api_key, "ip_address":ip_address}

    response = requests.get(url, params=params)
    print(response.text)
    response = json.loads(response.text)
    if response["status"] == "valid" or response["status"] == "do_not_mail" :
        response = {
            "status": "valid"
        }
        return response
    else :
        response = {"status": "Something went wrong"}
        return response
def emailFinder(api_key, domain, name):
    url = "https://api.zerobounce.net/v2/guessformat"
    params = {"api_key": api_key, "domain": domain, "first_name": name}
    response = requests.get(url, params=params)
    return json.loads(response.content)