import requests
import json

def getTemplate(key):
    url = "https://api.sendinblue.com/v3/smtp/templates?limit=50&offset=0&sort=asc"

    headers = {
        "accept": "application/json",
        "api-key": key
    }

    response = requests.get(url, headers=headers)
    return response.text


