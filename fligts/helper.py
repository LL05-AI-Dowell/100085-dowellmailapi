import requests

def get_fligts_data(mode,app_id, app_key, use_headers=False):
    url = f'https://api.flightstats.com/flex/{mode}/rest/v1/json/active'
    headers = {}
    params = {}

    if use_headers:
        headers = {
            'appId': app_id,
            'appKey': app_key,
            'Content-Type': 'application/json'
        }
    else:
        params = {
            'appId': app_id,
            'appKey': app_key
        }

    try:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            return {
                "success": True,
                "message": "All airports retrieved successfully",
                "response": response.json()
            }
        else:
            return {
                "success": False,
                "message": f"Request failed with status code: {response.status_code}"
            }
    except requests.RequestException as e:
        return {
            "success": False,
            "message":f"Request Exception: {e}"
        }


def get_airports_data_by_lat_long(latitude, longitude,radiusMiles, app_id, app_key, use_headers=False):
    url = f'https://api.flightstats.com/flex/airports/rest/v1/json/withinRadius/{longitude}/{latitude}/{radiusMiles}'

    params = {
        'appId': app_id,
        'appKey': app_key
    }
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return {
                "success": True,
                "message": "All airports retrieved based on lat and long successfully",
                "response": response.json()
            }
        else:
            return {
                "success": False,
                "message": f"Request failed with status code: {response.status_code}"
            }
    except requests.RequestException as e:
        return {
            "success": False,
            "message":f"Request Exception: {e}"
        }

def get_flights_arrival_departure_by_airport(airport_code,type, year,month,day,hourOfDay,maxFlights, app_id, app_key, use_headers=False):
    url = f"https://api.flightstats.com/flex/flightstatus/rest/v2/json/airport/status/{airport_code}/{type}/{year}/{month}/{day}/{hourOfDay}/?utc=false&numHours=1&maxFlights={maxFlights}"

    print(url)

    params = {
        'appId': app_id,
        'appKey': app_key
    }
    try:
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            return {
                "success": True,
                "message": "Data Recived successfully",
                "response": response.json()
            }
        else:
            return {
                "success": False,
                "message": f"Request failed with status code: {response.status_code}"
            }
    except requests.RequestException as e:
        return {
            "success": False,
            "message":f"Request Exception: {e}"
        }