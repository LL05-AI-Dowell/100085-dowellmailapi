import json
import requests
import pprint


def otp():
    url = "https://100085.pythonanywhere.com/api/signUp-otp-verification/"
    payload = json.dumps({
        "toEmail":"mdashsharma95@gmail.com",
        "toName":"Manish",
        "topic":"RegisterOtp",
        "otp":4862
        })
    headers = {
        'Content-Type': 'application/json'
        }

    response = requests.request("POST", url, headers=headers, data=payload)
    res= json.loads(response.text)

    return res

print (otp())