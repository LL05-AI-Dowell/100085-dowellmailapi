import json
import requests
import pprint
import uuid

def originalAI(api_key,content,title):
    url = "https://api.originality.ai/api/v1/scan/ai-plag"

    payload = {
        "content": content,
        "title": title,
        "aiModelVersion": "1"
    }
    headers = {
        "X-OAI-API-KEY": api_key,
        "Accept": "application/json"
    }

    response = requests.post(url, json=payload, headers=headers)

    return response.text


def processApikey(api_key):
    url = 'https://100105.pythonanywhere.com/api/v1/process-api-key/'
    payload = {
        "api_key" : api_key,
        "api_service_id" : "DOWELL100019"
    }

    response = requests.post(url, json=payload)
    return response.text