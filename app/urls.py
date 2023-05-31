from django.urls import path
from app.views import *

urlpatterns = [
    path('generate-api-key/',generateKey.as_view()),
    path('generate-api-key/<str:uuid>/',generateKey.as_view()),
    path('mail/<str:uuid>/',sendmail.as_view()),
]