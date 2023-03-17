from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt


@method_decorator(csrf_exempt, name='dispatch')
class serverReports(APIView):
    def get(self, request ):
        return Response({"Dowell Mail Service is running..."},status=status.HTTP_200_OK)
    