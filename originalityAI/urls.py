from django.urls import path
from .views import *

urlpatterns = [
    path('<str:userapikey>/', originalAITest.as_view()),
    # current api
    path('website-api/<str:userapikey>/', originalityContentTestSaveToDB.as_view()), 
    
    path('website-api/v3/<str:userapikey>/', originalityConentTest.as_view()), 
    path('', originalAITestInternal.as_view()),
]