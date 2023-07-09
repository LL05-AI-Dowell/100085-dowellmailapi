from django.urls import path
from app.views import *

urlpatterns = [
    path('generate-api-key/',generateKey.as_view()),
    path('generate-api-key/<str:uuid>/',generateKey.as_view()),
    path('mail/<str:uuid>/',sendmail.as_view()),
    path('test-api-key/',test_api_key.as_view()),
    path('subscribe-newsletter/<str:uuid>/',subscribeToNewsletters.as_view()),
    path('send-newsletter/',sendNewsLetterToInternalTeam.as_view()),
    path('unsubscribe-newsletter/<str:uuid>/<str:topic>/<str:typeOfSubscriber>/<str:subscriberEmail>/',unsubscribeToNewsletter.as_view()),
]