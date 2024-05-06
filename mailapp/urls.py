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
    path('payment-status/',send_payment_status.as_view()),
    path('hr-invitation/',send_mail_from_hr.as_view()),
    path('hr-status/',hr_mail.as_view()),
    path('email/',common_api.as_view()),
    path('uxlivinglab/email/',common_email_api.as_view()),
    path('uxlivinglab/verify-email/',verify_email.as_view()),
    path('candidate_removal/',candidate_removal.as_view()),
    path('dowell_bulk_email/',common_bulk_email.as_view()),
]