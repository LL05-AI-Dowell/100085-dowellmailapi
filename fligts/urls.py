from django.urls import path
from .views import *

urlpatterns = [
    path('heath_check/', health_check.as_view()),
    path('', flight_data.as_view()),
    
]