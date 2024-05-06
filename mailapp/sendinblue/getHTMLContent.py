import requests
import json

def getTemplateHTMLContent(key,templateName):
    url = "https://api.sendinblue.com/v3/smtp/templates?limit=50&offset=0&sort=asc"

    headers = {
        "accept": "application/json",
        "api-key": key
    }

    response = requests.get(url, headers=headers)
    data = data = json.loads(response.text)
    data_temp = []
    for i in data['templates']:
        name = i['name']
        htmlContent = i['htmlContent']
        temp_dist= {"name":name,"htmlContent":htmlContent}
        data_temp.append(temp_dist)
    result = [obj for obj in data_temp if obj['name'] == templateName]
    return result
