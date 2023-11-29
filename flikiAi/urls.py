from django.urls import path
from .views import *

urlpatterns = [
    path('health-check/', health_check.as_view()),
    path('process_text_to_video/', process_fliki_ai.as_view()),
    
]