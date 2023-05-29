from django.urls import path
from app.views import *

urlpatterns = [
    path('generate-api-key/',generateKey.as_view()),
    path('generate-api-key/<str:uuid>/',generateKey.as_view()),
    path('send-email/<str:uuid>/',sendmail.as_view()),
]