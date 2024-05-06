from django.urls import path
from .views import *

urlpatterns = [
    path('<str:api_key>/',newslettersystem.as_view()),
]