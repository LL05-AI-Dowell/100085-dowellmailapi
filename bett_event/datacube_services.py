import json
import requests
from datetime import datetime, timedelta

def datacube_data_insertion(api_key,database_name,collection_name,data):

    url = "https://datacube.uxlivinglab.online/db_api/crud/"

    data = {
        "api_key": api_key,
        "db_name": database_name,
        "coll_name": collection_name,
        "operation": "insert",
        "data":data
        
    }

    response = requests.post(url, json=data)
    return response.text

def datacube_data_retrival(api_key,database_name,collection_name,data,limit,offset,payment):

    url = "https://datacube.uxlivinglab.online/db_api/get_data/"

    data = {
        "api_key": api_key,
        "db_name": database_name,
        "coll_name": collection_name,
        "operation": "fetch",
        "filters":data,
        "limit": limit,
        "offset": offset,
        "payment":payment
    }

    response = requests.post(url, json=data)
    return response.text

def datacube_data_update(api_key,db_name,coll_name,query,update_data):

    url = "https://datacube.uxlivinglab.online/db_api/crud/"

    data = {
        "api_key": api_key,
        "db_name": db_name,
        "coll_name": coll_name,
        "operation": "update",
        "query" : query,
        "update_data":update_data
    }

    response = requests.put(url, json=data)
    return response.text

def datacube_create_collection(api_key,db_name,collection_name):
    url = "https://datacube.uxlivinglab.online/db_api/add_collection/"

    data_to_add = {
        "api_key": api_key,
        "db_name": db_name,
        "coll_names": collection_name,
        "num_collections": 1
    }

    response = requests.post(url, json=data_to_add)
    return response.text

def datacube_collection_retrival(api_key,db_name):
    url = "https://datacube.uxlivinglab.online/db_api/collections/"
    payload = {
        "api_key": api_key,
        "db_name": db_name,
        "payment": False
    }
    response = requests.get(url, json=payload)
    return response.text


def datacube_delete_data(api_key,db_name,collection_name,query):
    url = "https://datacube.uxlivinglab.online/db_api/crud/"

    data = {
        "api_key": api_key,
        "db_name": db_name,
        "coll_name": collection_name,
        "operation": "delete",
        "query": query,

    }
    response = requests.delete(url, json=data)
    print(response.text)