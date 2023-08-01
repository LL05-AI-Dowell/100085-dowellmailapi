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
    url = f'https://100105.pythonanywhere.com/api/v3/process-services/?type=api_service&api_key={api_key}'
    print(api_key)
    print(url)
    payload = {
        "service_id" : "DOWELL10003"
    }

    response = requests.post(url, json=payload)
    return response.text