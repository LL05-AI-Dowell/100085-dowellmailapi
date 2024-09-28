from database.datacube import *
from django.shortcuts import render,redirect
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

@method_decorator(csrf_exempt, name='dispatch')
class datacube_report_view(APIView):
    def post(self, request):
        database=request.data.get("database_name")
        collection_name = request.data.get("collection_name")
        limit = request.data.get("limit")
        offset= request.data.get("offset")
        
        response =json.loads(datacube_data_retrieval(
            api_key,
            database,
            collection_name,
            {},
            limit,
            offset,
            False
        ))
        
        if not response["success"]:
            return Response({
                "success":False,
                "message":"No data or something went wrong"
            }, status= status.HTTP_404_NOT_FOUND)
        return Response({
            "success": True,
            "message": "Data retrived successfully",
            "response": response["data"]
        },status=status.HTTP_200_OK)