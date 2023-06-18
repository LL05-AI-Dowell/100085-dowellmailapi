from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
import json
from app.helper import validateMail
from database.dowellconnection import dowellconnection , dowellconnectionupdate
from database.dowelleventcreation import get_event_id
from database.database_management import *
from mailapp.sendinblue import getTemplate as gt
from mailapp.sendinblue import getHTMLContent as gTH
import os
from mailapp.zeroBounce import validateMail as vE 
from mailapp.zeroBounce.validateMail import emailFinder
from dotenv import load_dotenv

# load_dotenv()
load_dotenv("/home/100085/100085-dowellmailapi/.env")
SECRET_KEY = str(os.getenv('SECRET_KEY')) 

@method_decorator(csrf_exempt, name='dispatch')
class mailSetting(APIView):
    def post(self, request ):
        key = request.data.get('key')
        fromAddress = request.data.get('fromAddress')
        fromName = request.data.get('fromName')
        templateName = request.data.get('templateName')
        subject = request.data.get('subject')
        topic = request.data.get('topic')
        api_key = request.data.get('apiKey')
        print("---Got the key from the database---")
        get_data = gt.getTemplate(key)
        print("---Template fetching from sedinblue database---")
        data = json.loads(get_data)
        data_temp = []
        for i in data['templates']:
            name = i['name']
            htmlContent = i['htmlContent']
            temp_dist= {"name":name,"htmlContent":htmlContent}
            data_temp.append(temp_dist)
        result = [obj for obj in data_temp if obj['name'] == templateName]
        print("---Found the template based on topic/tempate name---")
        field = {
            "eventId": get_event_id()['event_id'],
            "key" : key,
            "fromAddress" : fromAddress,
            "fromName" : fromName,
            "templateName" : templateName,
            "subject" : subject,
            "topic" : topic,
            "api_key":api_key,
            "template_data": result
        }
        print("---Data inserting Now---")
        response = dowellconnection(*Email_management,"insert",field)
        if response:
        # return Response(result,status=status.HTTP_201_CREATED)
            print("---Data has been inserted---")
            return Response({"INFO":"Setting has been inserted!!"},status=status.HTTP_201_CREATED)
        else:
            return Response({"INFO":"Something went wrong!!"},status=status.HTTP_400_BAD_REQUEST)
        
@method_decorator(csrf_exempt, name='dispatch')
class SendEmail(APIView):
    def post(self, request):
        topic = request.data.get('topic')
        toemail = request.data.get('toEmail')
        toname = request.data.get('toName')
        print("---Got the required parameter to send mail---",topic,toemail,toname)
        field = {
            "topic":topic
        }
        fetched_data = dowellconnection(*Email_management,"find",field)
        print("---Fetching data from our database based on topic---")
        data = json.loads(fetched_data)
        sender = data['data']['fromName']
        fromemail = data['data']['fromAddress']
        subject = data['data']['subject']
        key = data['data']['key']
        message = data['data']['template_data'][0]['htmlContent']
        print("---Got the template the htmlContent---")
        configuration = sib_api_v3_sdk.Configuration()
        configuration.api_key['api-key'] = key
        api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))
        subject = subject
        html_content = message
        sender = {"name": sender, "email": fromemail}
        to = [{"email": toemail, "name": toname}]
        headers = {"Some-Custom-Name": "unique-id-1234"}
        print("---All the data are gethered and ready to send mail---")
        send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(to=to, headers=headers,html_content=html_content, sender=sender, subject=subject)
        try:
            api_response = api_instance.send_transac_email(send_smtp_email)
            api_response_dict = api_response.to_dict()
            print("---The mail has been sent ! Happy :D---")
            return Response({"INFO":"Mail has been sent!!","INFO":json.dumps(api_response_dict)},status=status.HTTP_200_OK)
        except ApiException as e:
            return Response({"error":"Exception when calling SMTPApi->send_transac_email: %s\n" % e},status=status.HTTP_400_BAD_REQUEST)
        
@method_decorator(csrf_exempt,name ='dispatch')
class subscriberList(APIView):
    def get(self, request):
        field = {
            "eventId": "FB1010000000000000000000003004"
        }
        fetchData = dowellconnection(*subscriber_management,"fetch",field)
        print("---",json.loads(fetchData))
        if(len(json.loads(fetchData)["data"]) == 0):
            return Response({
                "success": False,
                "message": "No subscriber yet",
                "data":json.loads(fetchData),
            })
        else:
            return Response({
                "status":True,
                "message": "Subscriber list",
                "data":json.loads(fetchData)
            })
    

    def post(self, request):
        topic = request.data.get("topic")
        subscriberEmail = request.data.get("subscriberEmail")
        subscriberStatus = request.data.get("subscriberStatus", True)
        typeOfSubscriber = request.data.get("typeOfSubscriber")
        print("---Checking the requests are ok---")
        if not (topic and subscriberEmail and subscriberStatus and typeOfSubscriber):
            print("---Some parameter is missing---")
            missing_values = [key for key, value in request.data.items() if not value]
            return Response({"INFO":f"{', '.join(missing_values)} are missing!"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            email_validation = validateMail(SECRET_KEY,subscriberEmail)
            print("---Checking the the email is valid---")
            if email_validation['status'] == "valid":
                print("---Email is verified---")
                print("---All parameters are ok and ready to insert to our database---")
                field = {
                    "eventId": get_event_id()['event_id'],
                    "topic":topic,
                    "subscriberEmail":subscriberEmail,
                    "subscriberStatus":subscriberStatus,
                    "typeOfSubscriber":typeOfSubscriber
                }
                print("---Data inserting now---")
                inserted_data = dowellconnection(*subscriber_management,"insert",field)
                if inserted_data:
                    print("---Data has been inserted---")
                    return Response({
                        "success": True,
                        "message": f"{subscriberEmail} has subscribed",
                        "DATABASE_INFO":json.loads(inserted_data),
                        "subscriber":{
                            "topic":topic,
                            "subscriberEmail":subscriberEmail,
                            "subscriberStatus":subscriberStatus,
                            "typeOfSubscriber":typeOfSubscriber
                        }
                    }, status=status.HTTP_200_OK)
                else:
                    return Response({
                        "success": True,
                        "message":"Something went wrong while inserting to database!"
                    }, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({
                    "status": False,
                    "message":"it is not a valid email address"
                }, status=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION)


    def put(self,request):
        topic = request.data.get("topic")
        subscriberEmail = request.data.get("subscriberEmail")
        field = {
            "topic":topic,
            "subscriberEmail":subscriberEmail
        }
        print("---Fetching data from database based on required data---")
        fetched_data = dowellconnection(*subscriber_management,"find",field)
        data = json.loads(fetched_data)
        print("---Data has been found and checking if the provided email has subscribed to the topic of not ---")
        if (data['data']['subscriberStatus'] == True):
            field= {
                "_id":data['data']['_id']
            }
            update_field = {
                "subscriberStatus": False
            }
            print("---Provided email was subscribed to the topic and Unsubscribing---")
            update_response = dowellconnectionupdate(*subscriber_management,"update",field,update_field)
            print("---Unsubscribed ! SAD---")
            return Response({
                "status": True,
                "message":"User has unsubscribed" , 
                "DATABASE_INFO":json.loads(update_response)
            },status=status.HTTP_202_ACCEPTED)
        else:
            return Response({
                "status": False,
                "message":"Already an unsubscribed!"
            },status=status.HTTP_406_NOT_ACCEPTABLE)
        
@method_decorator(csrf_exempt, name='dispatch')
class subscribeToInternalTeam(APIView):

    def get(self,request):
        topic = request.GET.get('topic')
        subscriberEmail = request.GET.get('email')
        typeOfSubscriber = request.GET.get('types')

        email_validation = validateMail(SECRET_KEY,subscriberEmail)
        print("---Checking the the email is valid---")
        if email_validation['status'] == "valid":
            print("---Email is verified---")
            print("---All parameters are ok and ready to insert to our database---")
            field = {
                "eventId": get_event_id()['event_id'],
                "topic":topic,
                "subscriberEmail":subscriberEmail,
                "subscriberStatus":True,
                "typeOfSubscriber":typeOfSubscriber
            }
            print("---Data inserting now---")
            inserted_data = dowellconnection(*subscriber_management,"insert",field)
            if inserted_data:
                print("---Data has been inserted---")
                return Response({
                    "success": True,
                    "message": f"Thank you {subscriberEmail} for subscribing to our newsletter",
                    "DATABASE_INFO":json.loads(inserted_data),
                    "subscriber":{
                        "topic":topic,
                        "subscriberEmail":subscriberEmail,
                        "subscriberStatus":True,
                        "typeOfSubscriber":typeOfSubscriber
                    }
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    "success": True,
                    "message":"Something went wrong while inserting to database!"
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({
                "status": False,
                "message":"it is not a valid email address"
            }, status=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION)
        

@method_decorator(csrf_exempt,name ='dispatch')
class signUpOTPverification(APIView):
    def post(self, request):
        topic = request.data.get('topic')
        toemail = request.data.get('toEmail')
        toname = request.data.get('toName')
        otp = request.data.get('otp')
        print("---Got the required parameter to send mail---",topic,toemail,toname,otp)
        field = {
            "topic":topic
        }
        fetched_data = dowellconnection(*Email_management,"find",field)
        data = json.loads(fetched_data)
        sender = data['data']['fromName']
        fromemail = data['data']['fromAddress']
        subject = data['data']['subject']
        key = data['data']['key']
        api_key = data['data']['api_key']
        message = data['data']['template_data'][0]['htmlContent']
        print("---Got the template the htmlContent---")
        emailBody = message.format(toname,otp)
        print("---Checking whether email is valid---")
        email_validation = vE.validateMail(api_key,toemail)
        if email_validation['status'] == "valid":
            print("---Email is valid---")
            configuration = sib_api_v3_sdk.Configuration()
            configuration.api_key['api-key'] = key
            api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))
            subject = subject
            html_content = emailBody
            sender = {"name": sender, "email": fromemail}
            to = [{"email": toemail, "name": toname}]
            headers = {"Some-Custom-Name": "unique-id-1234"}
            print("---All the data are gethered and ready to send mail---")
            send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(to=to, headers=headers,html_content=html_content, sender=sender, subject=subject)
            try:
                api_response = api_instance.send_transac_email(send_smtp_email)
                api_response_dict = api_response.to_dict()
                print("---The mail has been sent ! Happy :D---")
                return Response({"MAIL INFO":"Mail has been sent!!","INFO":json.dumps(api_response_dict)},status=status.HTTP_200_OK)
            except ApiException as e:
                return Response({"error":"Exception when calling SMTPApi->send_transac_email: %s\n" % e},status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"status":"varification failed","error":email_validation['status']},status=status.HTTP_400_BAD_REQUEST)

@method_decorator(csrf_exempt,name='dispatch')
class feedbackSurvey(APIView):
    def post(self,request):
        topic = request.data.get('topic')
        toemail = request.data.get('toEmail')
        toname = request.data.get('toName')
        qr_code_src= request.data.get('qr_code_src') 
        data_survey_id= request.data.get('data_survey_id') 
        survey_title= request.data.get('survey_title') 
        user_name= request.data.get('user_name') 
        print("---Got the required parameter to send mail---",topic,toemail,toname)
        field = {
            "topic":topic
        }
        fetched_data = dowellconnection(*Email_management,"find",field)
        data = json.loads(fetched_data)
        sender = data['data']['fromName']
        fromemail = data['data']['fromAddress']
        subject = data['data']['subject']
        templateName = data['data']['templateName']
        key = data['data']['key']
        message = data['data']['template_data'][0]['htmlContent']
        htmlTemplateContent = gTH.getTemplateHTMLContent(key,templateName)[0]['htmlContent']
        print("---Got the template the htmlContent---")
        emailBody = htmlTemplateContent.format(qr_code_src,survey_title,user_name,qr_code_src, data_survey_id)
        # return Response(emailBody)
        configuration = sib_api_v3_sdk.Configuration()
        configuration.api_key['api-key'] = key
        api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))
        subject = subject
        html_content = emailBody
        sender = {"name": sender, "email": fromemail}
        to = [{"email": toemail, "name": toname}]
        headers = {"Some-Custom-Name": "unique-id-1234"}
        print("---All the data are gethered and ready to send mail---")
        send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(to=to, headers=headers,html_content=html_content, sender=sender, subject=subject)
        try:
            api_response = api_instance.send_transac_email(send_smtp_email)
            api_response_dict = api_response.to_dict()
            print("---The mail has been sent ! Happy :D---")
            return Response({"MAIL INFO":"Mail has been sent!!","INFO":json.dumps(api_response_dict)},status=status.HTTP_200_OK)
        except ApiException as e:
            return Response({"error":"Exception when calling SMTPApi->send_transac_email: %s\n" % e},status=status.HTTP_400_BAD_REQUEST)
        



@method_decorator(csrf_exempt,name='dispatch')
class signupfeedbackmail(APIView):
    def post(self,request):
        topic = request.data.get('topic')
        toemail = request.data.get('toEmail')
        toname = request.data.get('toName')
        firstname = request.data.get('firstname')
        lastname = request.data.get('lastname')
        username = request.data.get('username')
        phoneCode = request.data.get('phoneCode')
        phoneNumber = request.data.get('phoneNumber')
        usertype = request.data.get('usertype')
        country = request.data.get('country')
        verified_phone = request.data.get('verified_phone')
        verified_email = request.data.get('verified_email')
        print("---Got the required parameter to send mail---",topic,toemail,toname,firstname,lastname,username,phoneCode,phoneNumber,usertype,country,verified_phone,verified_email)
        field = {
            "topic":topic
        }
        fetched_data = dowellconnection(*Email_management,"find",field)
        data = json.loads(fetched_data)
        sender = data['data']['fromName']
        fromemail = data['data']['fromAddress']
        subject = data['data']['subject']
        templateName = data['data']['templateName']
        key = data['data']['key']
        message = data['data']['template_data'][0]['htmlContent']
        htmlTemplateContent = gTH.getTemplateHTMLContent(key,templateName)[0]['htmlContent']
        print("---Got the template the htmlContent---")
        phone = f"{phoneCode} {phoneNumber}" 
        print("---Got the phone----",phone)
        emailBody = htmlTemplateContent.format(firstname,firstname,lastname,username,phone,verified_phone,toemail,verified_email,usertype,country)
        print("---sets all the fields---")
        configuration = sib_api_v3_sdk.Configuration()
        configuration.api_key['api-key'] = key
        api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))
        subject = subject
        html_content = emailBody
        sender = {"name": sender, "email": fromemail}
        to = [{"email": toemail, "name": toname}]
        bcc = [{"email": "dowell@dowellresearch.uk" , "name":"Dowell Research"},{"email": "customersupport@dowellresearch.sg" , "name":"customer support"},{"email": "nitesh@dowellresearch.in" , "name":"Nitesh"}]
        headers = {"Some-Custom-Name": "unique-id-1234"}
        print("---All the data are gethered and ready to send mail---")
        send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(to=to,bcc=bcc, headers=headers,html_content=html_content, sender=sender, subject=subject)
        try:
            api_response = api_instance.send_transac_email(send_smtp_email)
            api_response_dict = api_response.to_dict()
            print("---The mail has been sent ! Happy :D---")
            return Response({"MAIL INFO":"Mail has been sent!!","INFO":json.dumps(api_response_dict)},status=status.HTTP_200_OK)
        except ApiException as e:
            return Response({"error":"Exception when calling SMTPApi->send_transac_email: %s\n" % e},status=status.HTTP_400_BAD_REQUEST)
        

@method_decorator(csrf_exempt, name='dispatch')
class sendNewsLetter(APIView):
    def post(self, request):
        toemail = request.data.get("toEmail")
        topic = request.data.get('topic')
        
        field = {
            "topic":topic
        }
        fetched_data = dowellconnection(*Email_management,"find",field)
        data = json.loads(fetched_data)
        sender = data['data']['fromName']
        fromemail = data['data']['fromAddress']
        subject = data['data']['subject']
        templateName = data['data']['templateName']
        key = data['data']['key']
        message = data['data']['template_data'][0]['htmlContent']
        htmlTemplateContent = gTH.getTemplateHTMLContent(key,templateName)[0]['htmlContent']
        print("---Got the template the htmlContent---")
        configuration = sib_api_v3_sdk.Configuration()
        configuration.api_key['api-key'] = key
        api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))
        subject = subject
        html_content = htmlTemplateContent
        sender = {"name": sender, "email": fromemail}
        to = toemail
        headers = {"Some-Custom-Name": "unique-id-1234"}
        print("---All the data are gethered and ready to send mail---")
        send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(to=to, headers=headers,html_content=html_content, sender=sender, subject=subject)
        try:
            api_response = api_instance.send_transac_email(send_smtp_email)
            api_response_dict = api_response.to_dict()
            print("---The mail has been sent ! Happy :D---")
            return Response({"MAIL INFO":"Mail has been sent!!","INFO":json.dumps(api_response_dict)},status=status.HTTP_200_OK)
        except ApiException as e:
            return Response({"error":"Exception when calling SMTPApi->send_transac_email: %s\n" % e},status=status.HTTP_400_BAD_REQUEST)
    

@method_decorator(csrf_exempt, name='dispatch')
class dowellSMSsetting(APIView):
    def post(self, request ):
        key = request.data.get('key')
        created_by = request.data.get('created_by')
        print("---Got the key from the database---")
        field = {
            "eventId": get_event_id()['event_id'],
            "key" : key,
            "created_by" : created_by
        }
        print("---Data inserting Now---")
        response = dowellconnection(*dowellSMSsettings,"insert",field)
        print("---Data has been inserted---")
        if response:
            return Response({"INFO":"Setting has been inserted!!"},status=status.HTTP_201_CREATED)
        else:
            return Response({"INFO":"Something went wrong!!"},status=status.HTTP_400_BAD_REQUEST)

@method_decorator(csrf_exempt, name='dispatch')
class dowellSMS(APIView):
    def post(self, request ):
        sender = request.data.get('sender')
        recipient = request.data.get('recipient')
        content = request.data.get('content')
        created_by = request.data.get('created_by')
        print("---Got the key from the database---")
        field = {
            "created_by" : created_by
        }
        print("---Data fetching Now---")
        fetched_data = dowellconnection(*dowellSMSsettings,"find",field)
        data = json.loads(fetched_data)
        print("---Data fetched---")
        key = data["data"]["key"]
        configuration = sib_api_v3_sdk.Configuration()
        configuration.api_key['api-key'] = key
        # configuration.api_key['api-key'] = os.getenv("SECRET_KEY")

        api_instance = sib_api_v3_sdk.TransactionalSMSApi(sib_api_v3_sdk.ApiClient(configuration))
        send_transac_sms = sib_api_v3_sdk.SendTransacSms(sender=sender, recipient=recipient, content=content)

        try:
            api_response = api_instance.send_transac_sms(send_transac_sms)
            api_response_dict = api_response.to_dict()
            print("---The SMS has been sent ! Happy :D---")
            return Response({"MAIL INFO":"SMS has been sent!!","INFO":json.dumps(api_response_dict)},status=status.HTTP_200_OK)
        except ApiException as e:
            return Response({"error":"Exception when calling SMTPApi->send_transac_email: %s\n" % e},status=status.HTTP_400_BAD_REQUEST)


@method_decorator(csrf_exempt, name='dispatch')
class editormailcomponent(APIView):
    def post(self, request ):
        topic = request.data.get('topic')
        toemail = request.data.get('toEmail')
        toname = request.data.get('toName')
        fromName = request.data.get('fromName')
        fromemail = request.data.get('fromEmail')
        subject = request.data.get('subject')
        email_body = request.data.get('email_body') 
        print("---Got the required parameter to send mail---",topic,toemail,toname,fromemail,email_body)
        field = {
            "topic":topic
        }
        fetched_data = dowellconnection(*Email_management,"find",field)
        data = json.loads(fetched_data)
        sender = fromName
        subject = subject
        templateName = data['data']['templateName']
        key = data['data']['key']
        message = data['data']['template_data'][0]['htmlContent']
        htmlTemplateContent = gTH.getTemplateHTMLContent(key,templateName)[0]['htmlContent']
        print("---Got the template the htmlContent---")
        emailBody = htmlTemplateContent.format(toname,email_body)
        # return Response({
        #     "toemail" : toemail, 
        #     "toname" : toname, 
        #     "fromName" :fromName,
        #     "fromemail": fromemail,
        #     "subject" : subject,
        #     "email_body" : emailBody,
        # },status=status.HTTP_200_OK)
        configuration = sib_api_v3_sdk.Configuration()
        configuration.api_key['api-key'] = key
        api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))
        subject = subject
        html_content = emailBody
        sender = {"name": sender, "email": fromemail}
        to = [{"email": toemail, "name": toname}]
        headers = {"Some-Custom-Name": "unique-id-1234"}
        print("---All the data are gethered and ready to send mail---")
        send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(to=to, headers=headers,html_content=html_content, sender=sender, subject=subject)
        try:
            api_response = api_instance.send_transac_email(send_smtp_email)
            api_response_dict = api_response.to_dict()
            print("---The mail has been sent ! Happy :D---")
            return Response({"MAIL INFO":"Mail has been sent!!","INFO":json.dumps(api_response_dict)},status=status.HTTP_200_OK)
        except ApiException as e:
            return Response({"error":"Exception when calling SMTPApi->send_transac_email: %s\n" % e},status=status.HTTP_400_BAD_REQUEST)
        
@method_decorator(csrf_exempt, name='dispatch')
class validateEmailapi(APIView):
    def post(self, request ):
        topic = request.data.get('topic')
        email = request.data.get('email')
        print("---Got the required parameter to send mail---",topic,email)
        field = {
            "topic":topic
        }
        fetched_data = dowellconnection(*Email_management,"find",field)
        data = json.loads(fetched_data)
        key = data['data']['key']
        api_key = data['data']['api_key']
        email_validation = vE.validateMail(api_key,email)
        if email_validation['status'] == "valid":
            return Response({
                "success": True,
                "message": f"Hurray ! {email} is a valid email"  
            },status=status.HTTP_200_OK)
        else:
            return Response({
                "success": False,
                "message": f"Sorry ! {email} is not a valid email"  
            },status=status.HTTP_401_UNAUTHORIZED)

@method_decorator(csrf_exempt, name='dispatch')
class send_invitation(APIView):
    def post(self, request):
        file = request.FILES.get('file') 
        topic = request.data.get('topic')
        toemail = request.data.get('toemail')
        toname = request.data.get('toname') 
        print("---Got the required parameter to send mail---",topic,toemail,toname)
        field = {
            "topic":topic
        }
        file_content = file.read().decode('utf-8') 
        fetched_data = dowellconnection(*Email_management,"find",field)
        data = json.loads(fetched_data)
        sender = data['data']['fromName']
        fromemail = data['data']['fromAddress']
        subject = data['data']['subject']
        templateName = data['data']['templateName']
        key = data['data']['key']
        api_key = data['data']['api_key']
        message = data['data']['template_data'][0]['htmlContent']
        print("---Got the template the htmlContent---")
        emailBody = file_content
        print("---Checking whether email is valid---")
        email_validation = vE.validateMail(api_key,toemail)
        if email_validation['status'] == "valid":
            print("---Email is valid---")
            configuration = sib_api_v3_sdk.Configuration()
            configuration.api_key['api-key'] = key
            api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))
            subject = subject
            html_content = emailBody
            sender = {"name": sender, "email": fromemail}
            to = [{"email": toemail, "name": toname}]
            headers = {"Some-Custom-Name": "unique-id-1234"}
            print("---All the data are gethered and ready to send mail---")
            send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(to=to, headers=headers,html_content=html_content, sender=sender, subject=subject)
            try:
                api_response = api_instance.send_transac_email(send_smtp_email)
                api_response_dict = api_response.to_dict()
                print("---The mail has been sent ! Happy :D---")
                return Response({"MAIL INFO":"Mail has been sent!!","INFO":json.dumps(api_response_dict)},status=status.HTTP_200_OK)
            except ApiException as e:
                return Response({"error":"Exception when calling SMTPApi->send_transac_email: %s\n" % e},status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"status":"varification failed","error":email_validation['status']},status=status.HTTP_400_BAD_REQUEST)

@method_decorator(csrf_exempt, name='dispatch')
class email_domainFinder(APIView):
    def post(self, request):
        name = request.data.get('name')
        domain = request.data.get('domain')
        print(name, domain)
        emailFiderStatus = emailFinder(SECRET_KEY, domain, name)
        if emailFiderStatus['status'] == "valid":
            return Response({
                "success": True,
                "message":"found a valid email",
                "result": emailFiderStatus
            })
        else :
            return Response({
                "success": False,
                "message":"Not found a valid email",
                "result": emailFiderStatus
            })
    

