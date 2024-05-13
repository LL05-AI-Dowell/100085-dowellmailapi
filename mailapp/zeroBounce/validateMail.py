import requests
import json
from database.datacube import *
from datetime import datetime

def validateMail(api_key, email):
    url = "https://api.zerobounce.net/v2/validate"
    ip_address = "99.123.12.122"

    params = {"email": email, "api_key": api_key, "ip_address": ip_address}

    existingEmail = json.loads(datacube_data_retrieval(
        "1b834e07-c68b-4bf6-96dd-ab7cdc62f07",
        "emaildatabase",
        "emaildata",
        {
            "email": email,
        },
        1,
        0,
        False

    ))
    print(existingEmail)
    
    if not existingEmail["success"]:
        return {"status": "Something went wrong"}
    
    if len(existingEmail["data"]) == 0:
        print("The email is not present in the database")
        checkEmail = requests.get(url, params=params)
        if checkEmail.status_code == 200:
            response_data = json.loads(checkEmail.text)
            if response_data["status"] == "valid" or response_data["status"] == "do_not_mail":
                insert_email_to_db = json.loads(datacube_data_insertion(
                    "1b834e07-c68b-4bf6-96dd-ab7cdc62f07",
                    "emaildatabase",
                    "emaildata",
                    {
                        "email": email,
                        "status": response_data["status"],
                        "checked_on": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "records": [{"record": "1", "type": "overall"}]
                    }
                ))

                if not insert_email_to_db["success"]:
                    return {"status": "Something went wrong"}
                
                return {"status": "valid"}
            else:
                insert_email_to_db = json.loads(datacube_data_insertion(
                    "1b834e07-c68b-4bf6-96dd-ab7cdc62f07",
                    "emaildatabase",
                    "emaildata",
                    {
                        "email": email,
                        "status": response_data["status"],
                        "checked_on": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "records": [{"record": "1", "type": "overall"}]
                    }
                ))

                if not insert_email_to_db["success"]:
                    return {"status": "Something went wrong"}
                return {"status": "Invalid or risky email"}
    
    if existingEmail["data"][0]["status"] == "valid":
        print("The email is already present in the database and it is valid email address")
        return {"status": "valid"}
    else:
        print("The email is already present in the database and it is invalid email address")
        return {"status":"Invalid or risky email"}
    


def emailFinder(api_key, domain, name):
    url = "https://api.zerobounce.net/v2/guessformat"
    params = {"api_key": api_key, "domain": domain, "first_name": name}
    response = requests.get(url, params=params)
    return json.loads(response.content)