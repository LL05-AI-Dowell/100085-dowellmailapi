from django.urls import path
from mailapp.views import *

urlpatterns = [
    path('send-mail/',SendEmail.as_view()),
    path('mail-setting/',mailSetting.as_view()),
    path('subscribe-newsletter/',subscriberList.as_view()),
    path('signUp-otp-verification/',signUpOTPverification.as_view()),
    path('feedback-survey/',feedbackSurvey.as_view()),
    path('signup-feedback/',signupfeedbackmail.as_view()),
    path('send-newsletter/',sendNewsLetter.as_view()),
    path('sms-setting/',dowellSMSsetting.as_view()),
    path('sms/',dowellSMS.as_view()),
    path('editor-component/',editormailcomponent.as_view()),
    path('validate-mail/',validateEmailapi.as_view()),
    path('send-invitation/',send_invitation.as_view()),
    path('email-finder/',email_domainFinder.as_view()),
    path('newsletter/',subscribeToInternalTeam.as_view()),
    path('validate-exhibitor-email/',validateExhibitorMail.as_view()),
    path('send-api-key/',sendAPIkey.as_view()),
]