from django.urls import path
from mailapp.views import *

urlpatterns = [
    path('send-mail/',SendEmail.as_view()),
    path('mail-setting/',mailSetting.as_view()),
    path('subscribe-newsletter/',subscriberList.as_view()),
]