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
    print("theeeiisss",response.status_code)
    return response.text


def update_user_usage(email, occurrences):
    url = f"https://100105.pythonanywhere.com//api/v3/experience_database_services/?type=update_user_usage&product_number=UXLIVINGLAB001&email={email}&occurrences={occurrences}"
    response = requests.get(url)
   
    return response.text

def experience_database_services(email, product_number, occurrences):
    registered_user_details_url = f"https://100105.pythonanywhere.com/api/v3/experience_database_services/?type=get_registered_user&email={email}&product_number={product_number}"

    try:
        response = requests.get(registered_user_details_url)
        registered_user_details = response.json()

        if not registered_user_details.get("success", False):
            return {"success": False, "message": registered_user_details.get("message", "Failed to fetch user details")}

        user_data = registered_user_details.get("response", [])

        if not user_data:
            return {"success": False, "message": "No user data found."}

        user_info = user_data[0]
        is_active = user_info.get("is_active", False)
        is_paid = user_info.get("is_paid", False)
        total_time = user_info.get("total_times", 0)
        used_time = user_info.get("used_time", 0)

        if not is_active:
            return {"success": False, "message": "Your account has been suspended"}

        if not is_paid:
            if total_time < occurrences:
                return {"success": False, "message": "You have exceeded your experienced limits."}

        else:
            if total_time < used_time:
                return {"success": False, "message": "You have exceeded your experienced limits."}

        return {"success": True}

    except requests.RequestException as e:
        return {"success": False, "message": f"Request error: {str(e)}"}