from django.urls import path
from .views import *

urlpatterns = [
    path('health-check/', health_check.as_view()),
    path('<str:document_id>/', bett_event_services.as_view()),
]