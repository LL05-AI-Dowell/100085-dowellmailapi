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
    payload = {
        "service_id" : "DOWELL10003"
    }

    response = requests.post(url, json=payload)
    return response.text

"""Dowell Mail API services"""
def send_email(toname,toemail,subject,email_content):
    url = "https://100085.pythonanywhere.com/api/email/"
    payload = {
        "toname": toname,
        "toemail": toemail,
        "subject": subject,
        "email_content":email_content
    }
    response = requests.post(url, json=payload)
    return response.text


"""DoWell Product Experienced Service"""
def check_the_occurrences(email):
    url = f"https://100105.pythonanywhere.com/api/v3/experience_database_services/?type=get_user_email&product_number=UXLIVINGLAB001&email={email}"
    response = requests.get(url)
    return response.text

def save_experienced_product_data(product_name,email,experienced_data):
    url = "https://100105.pythonanywhere.com/api/v3/experience_database_services/?type=experienced_user_details"
    payload = {
        "product_name": product_name,
        "email": email,
        "experienced_data": experienced_data
    }
    response = requests.post(url, json=payload)
    print(response.status_code)
    return response.text
