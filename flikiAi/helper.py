import requests

def get_supported_utils(api_key,request_type):
    url = f'https://api.fliki.ai/v1/{request_type}'
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.text
        else:
            print(f"Request failed with status code: {response.status_code}")
            return None
    except requests.RequestException as e:
        print(f"Request Exception: {e}")
        return None

import requests
import json

def get_voices(api_key, language_id, dialect_id):
    url = 'https://api.fliki.ai/v1/voices'
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    payload = {
        'languageId': language_id,
        'dialectId': dialect_id
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        if response.status_code == 200:
            return response.text
        else:
            print(f"Request failed with status code: {response.status_code}")
            return None
    except requests.RequestException as e:
        print(f"Request Exception: {e}")
        return None

import requests
import json

def generate_video_or_voiceover(api_key, format_type, scenes, settings, background_music_keywords):
    url = 'https://api.fliki.ai/v1/generate'
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    payload = {
        'format': format_type,
        'scenes': scenes,
        'settings':settings,
        'backgroundMusicKeywords': background_music_keywords
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        if response.status_code == 200:
            return response.text
        else:
            print(f"Request failed with status code: {response.status_code}")
            return None
    except requests.RequestException as e:
        print(f"Request Exception: {e}")
        return None

import requests
import json

def check_generation_status(api_key, generation_id):
    url = 'https://api.fliki.ai/v1/generate/status'
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    payload = {
        'id': generation_id
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        if response.status_code == 200:
            return response.text
        else:
            print(f"Request failed with status code: {response.status_code}")
            return None
    except requests.RequestException as e:
        print(f"Request Exception: {e}")
        return None
