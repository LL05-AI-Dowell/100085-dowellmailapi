import os
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
import json
from app.helper import *
from .models import ApiKey
from .serializers import *
from database.database_management import *
from mailapp.sendinblue import getHTMLContent as gTH
from dotenv import load_dotenv

# load_dotenv()
load_dotenv("/home/100085/100085-dowellmailapi/.env")
SECRET_KEY = str(os.getenv('SECRET_KEY')) 
@method_decorator(csrf_exempt, name='dispatch')
class generateKey(APIView):
    def post(self, request):
        field = {
            "name": request.data.get('name'),
            "email": request.data.get('email'),
            "uuid": generate_uuid()
        }
        serializer = ApiKeySerializer(data=field)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    def put(self, request):
        try:
            api_key = ApiKey.objects.all()
        except ApiKey.DoesNotExist:
            return Response("API Key not found.", status=status.HTTP_404_NOT_FOUND)
        for i in api_key:
            if not i.is_paid:
                i.is_valid = 25
                i.save()
        
        return Response("API valid count updated successfully.", status=status.HTTP_200_OK)
      
@method_decorator(csrf_exempt, name='dispatch')
class sendmail(APIView):
    def post(self, request, uuid):
        type_request = request.GET.get('type')

        if type_request == "validate":
            return self.validate_email(request)
        elif type_request == 'send-email':
            return self.send_email(request,uuid)
        else:
            return self.handle_error(request)

    def validate_email(self, request):
        email = request.data.get('email')
        print("---Got the required parameter to send mail---",email,SECRET_KEY)
        email_validation = validateMail(SECRET_KEY,email)
        print(email_validation)
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
        
    def send_email(self, request ,uuid):
        topic = "EditorMailComponent"
        toemail = request.data.get('email')
        toname = request.data.get('name')
        fromName = request.data.get('fromName')
        fromemail = request.data.get('fromEmail')
        subject = request.data.get('subject')
        email_body = request.data.get('body')
        print("---Got the required parameters to send mail---", topic,toemail, toname, fromemail,subject, email_body)
        
        field = {
            "topic": topic
        }
        update_field = {
            "status": "not_found"
        }
        
        fetched_data = dowellconnection(*Email_management, "find", field, update_field)
        data = json.loads(fetched_data)
        
        sender = fromName
        subject = subject
        templateName = data['data']['templateName']
        key = data['data']['key']
        message = data['data']['template_data'][0]['htmlContent']
        htmlTemplateContent = gTH.getTemplateHTMLContent(key, templateName)[0]['htmlContent']
        
        print("---Got the template's htmlContent---")
        
        emailBody = htmlTemplateContent.format(toname, email_body)
        
        try:
            api_key = ApiKey.objects.get(uuid=uuid)
            print("---Got apiKey---",api_key)
        except ApiKey.DoesNotExist:
            return Response("API Key not found.", status=status.HTTP_404_NOT_FOUND)
        
        api_key.is_valid -= 1
        api_key.save()
        
        serializer = ApiKeySerializer(api_key)
        if api_key.is_valid >= 0:
            email_validation = validateMail(SECRET_KEY,toemail)
            print(email_validation)
            if email_validation['status'] == "valid":
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
                    return Response({"success": True,"message":"Mail has been sent!!","send status":json.dumps(api_response_dict),"is_valid_count":serializer.data["is_valid"]},status=status.HTTP_200_OK)
                except ApiException as e:
                    return Response({"error":"Exception when calling SMTPApi->send_transac_email: %s\n" % e},status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({
                "success": False,
                "message": f"Sorry ! {toemail} is not a valid email"  
            },status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response({
                "success": False,
                "message": "Limit exceeded"
            }, status=status.HTTP_423_LOCKED)
        
    def handle_error(self, request):
        return Response({
            "success": False,
            "message": "Invalid request type"
        }, status=status.HTTP_400_BAD_REQUEST)
    
