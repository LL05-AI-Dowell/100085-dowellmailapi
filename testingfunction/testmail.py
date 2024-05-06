import requests
import json

def mail():
    email_c = """
        <!DOCTYPE html>
        <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Document</title>
            </head>
            <body>
                <h1>manish</h1>
            </body>
        </html>
    """
    url = "http://127.0.0.1:8000/api/email/"
    payload = json.dumps({
        "toname": "manish",
        "toemail": "manish@dowellresearch.in",
        "subject": "testing",
        "email_content": email_c
    })
    headers = {
        'Content-Type': 'application/json'
        }

    response = requests.request("POST", url, headers=headers, data=payload)
    res= json.loads(response.text)

    return res

print (mail())