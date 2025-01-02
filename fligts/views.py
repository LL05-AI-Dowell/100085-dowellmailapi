
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from dotenv import load_dotenv
import os 
from .helper import *
import json

# load_dotenv()
load_dotenv("/home/100085/100085-dowellmailapi/.env")
FLIGHT_SERVICE_APP_ID = str(os.getenv('FLIGHT_SERVICE_APP_ID')) 
FLIGHT_SERVICE_APP_KEY = str(os.getenv('FLIGHT_SERVICE_APP_KEY')) 

@method_decorator(csrf_exempt, name='dispatch')
class health_check(APIView):
    def get(self, request ):
        return Response({
            "success": True,
            "message":"Dowell Flight server is running fine"
        },status=status.HTTP_200_OK)

@method_decorator(csrf_exempt, name='dispatch')
class flight_data(APIView):

    def post(self, request):
        type_request = request.GET.get('type')

        if type_request == "get_airport_by_lat_long":
            return self.get_airport_by_lat_long(request)
        elif type_request == "get_flights_arrival_departure":
            return self.get_flights_arrival_departure(request)
        else:
            return self.handle_error(request)
    def get(self, request):
        type_request = request.GET.get('type')

        if type_request == "get_airports":
            return self.get_airports(request)
        elif type_request == "get_airlines":
            return self.get_airlines(request)
        else:
            return self.handle_error(request)
        
    def get_airports(self, request):
        res = get_fligts_data('airports',FLIGHT_SERVICE_APP_ID, FLIGHT_SERVICE_APP_KEY)

        if not res['success']:
            return Response({
                "success": False,
                "message": res['message']
            }, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            "success": True,
            "message": "All Airports list retrieved successfully",
            "response": res['response']['airports']  
        })
    
    def get_airlines(self, request):
        res = get_fligts_data('airlines',FLIGHT_SERVICE_APP_ID, FLIGHT_SERVICE_APP_KEY)

        if not res['success']:
            return Response({
                "success": False,
                "message": res['message']
            }, status=status.HTTP_400_BAD_REQUEST)

        print(len(res['response']['airlines']))
        return Response({
            "success": True,
            "message": "All Airports list retrieved successfully",
            "response": res['response']['airlines']  
        })

    def get_airport_by_lat_long(self, request):
        latitude = request.data.get('latitude')
        longitude = request.data.get('longitude')

        if not all([latitude, longitude]):
            return Response({
                "success": False,
                "message": "Please provide both latitude and longitude"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        res = get_airports_data_by_lat_long(latitude, longitude, 20, FLIGHT_SERVICE_APP_ID, FLIGHT_SERVICE_APP_KEY)

        if not res['success']:
            return Response({
                "success": False,
                "message": res['message']
            }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({
            "success": True,
            "message": "All Airports list retrieved successfully",
            "response": res['response']['airports']
        })
    def get_flights_arrival_departure(self, request):
        airport_code = request.data.get('airport_code')
        year = request.data.get('year')
        month = request.data.get('month')
        day = request.data.get('day')
        hourOfDay = request.data.get('hourOfDay')
        maxFlights = request.data.get('maxFlights')

        if not all([airport_code, year, month, day, hourOfDay, maxFlights]):
            return Response({
                "success": False,
                "message": "Please provide all required parameters"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        res = get_flights_arrival_departure_by_airport(airport_code,"arr", year, month, day, hourOfDay, maxFlights, FLIGHT_SERVICE_APP_ID, FLIGHT_SERVICE_APP_KEY)

        if not res['success']:
            return Response({
                "success": False,
                "message": res['message']
            }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({
            "success": True,
            "message": "All Airports list retrieved successfully",
            "response": res['response']['flightStatuses']
        })

    
    def handle_error(self, request): 
        return Response({
            "success": False,
            "message": "Invalid request type"
        }, status=status.HTTP_400_BAD_REQUEST)
