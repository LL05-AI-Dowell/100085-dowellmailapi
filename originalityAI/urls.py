from django.urls import path
from .views import *

urlpatterns = [
    path('<str:userapikey>/', originalAITest.as_view()),
    path('', originalAITestInternal.as_view()),
]