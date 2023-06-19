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
    
    def get(self, request):
        username = request.GET.get('user')
        print(username)
        if username == "manish":
            api_keys = ApiKey.objects.all()
            print(api_keys)
            return Response(list(api_keys.values()), status=status.HTTP_200_OK)
        else:
            return Response("Invalid username", status=status.HTTP_400_BAD_REQUEST)

@method_decorator(csrf_exempt, name='dispatch')
class sendmail(APIView):
    def post(self, request, uuid):
        type_request = request.GET.get('type')

        if type_request == "validate":
            return self.validate_email(request,uuid)
        elif type_request == 'send-email':
            return self.send_email(request,uuid)
        elif type_request == 'email-finder':
            return self.email_finder(request,uuid)
        else:
            return self.handle_error(request)

    def validate_email(self, request,uuid):
        email = request.data.get('email')
        print("---Got the required parameter to send mail---",email)
        try:
            api_key = ApiKey.objects.get(uuid=uuid)
            print("---Got apiKey---",api_key)
        except ApiKey.DoesNotExist:
            return Response("API Key not found.", status=status.HTTP_404_NOT_FOUND)
        
        api_key.is_valid -= 1
        api_key.save()

        email_validation = validateMail(SECRET_KEY,email)
        if api_key.is_valid >= 0:
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
        else:
            return Response({
                "success": False,
                "message": "Limit exceeded"
            }, status=status.HTTP_423_LOCKED)
        
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

    def email_finder(self,request,uuid):
        name = request.data.get('name')
        domain = request.data.get('domain')
        print(name, domain,uuid)
        try:
            api_key = ApiKey.objects.get(uuid=uuid)
            print("---Got apiKey---",api_key)
        except ApiKey.DoesNotExist:
            return Response("API Key not found.", status=status.HTTP_404_NOT_FOUND)
        
        api_key.is_valid -= 1
        api_key.save()
        if api_key.is_valid >= 0:
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
                    "result": emailFiderStatus["failure_reason"]
                })
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
    
@method_decorator(csrf_exempt, name='dispatch')
class test_api_key(APIView):
    def post(self, request):
        fields = {
            "name": request.data.get('name'),
            "email": request.data.get('email'),
            "uuid": generate_uuid()
        }

        return Response({
            "success": True,
            "message": "Test api key was successfully created",
            "info": fields
        }, status=status.HTTP_200_OK)
    def get(self, request):
        username = request.GET.get('user')
        if username == "manish":
            data = [
                {
                    "id": 1,
                    "uuid": "xyz-abc-efg",
                    "name": "Name",
                    "email": "email@gmail.com",
                    "is_active": True,
                    "is_valid": 25,
                    "is_paid": False
                }
            ]
            return Response({
                "success": True,
                "message": "Data was successfully retrieved",
                "info": data
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                "status" :False,
                "message" : f"{username} is not authorized"
            })
        
@method_decorator(csrf_exempt, name='dispatch')
class subscribeToNewsletters(APIView):
    def get(self,request,uuid):
        try:
            api_key = ApiKey.objects.get(uuid=uuid)
            print("---Got apiKey---",api_key)
        except ApiKey.DoesNotExist:
            return Response("API Key not found.", status=status.HTTP_404_NOT_FOUND)
        field = {
            "APIKey": uuid
        }
        update_field = {
            "status": "Ok"
        }
        fetch_data = dowellconnection(*subscriber_management,"fetch",field,update_field)
        return Response({
            "success": True,
            "message": "List of subscriber",
            "Details": json.loads(fetch_data)
        },status=status.HTTP_200_OK)
        
    def post(self,request,uuid):
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
            try:
                api_key = ApiKey.objects.get(uuid=uuid)
                print("---Got apiKey---",api_key)
            except ApiKey.DoesNotExist:
                return Response("API Key not found.", status=status.HTTP_404_NOT_FOUND)
            print("---Decrementing API key count---")
            api_key.is_valid -= 1
            api_key.save()
            serializer = ApiKeySerializer(api_key)

            field = {
                "APIKey": uuid
            }
            update_field = {
                "status": "OK",
            }

            print("---Fetching data based on apiKey---")
            fetch_all_subscriber = dowellconnection(*subscriber_management,"fetch",field,update_field)
            response = json.loads(fetch_all_subscriber)
            print("---all subacriber data is fetched---")
            email_validation = validateMail(SECRET_KEY,subscriberEmail)
            print("---Checking the the email is valid---")
            if email_validation['status'] == "valid":
                print("---Email is verified and Starting subscription Processing---")
                if(len(response["data"]) == 0):
                    field = {
                        "eventId": get_event_id()['event_id'],
                        "topic":topic,
                        "subscriberEmail":subscriberEmail,
                        "subscriberStatus":subscriberStatus,
                        "typeOfSubscriber":typeOfSubscriber,
                        "APIKey":uuid,
                        "API Owner Name": serializer.data["name"],
                        "API Owner Email": serializer.data["email"]
                    }
                    update_field = {
                        "status": "OK",
                    }
                    insert_subscriber_data = dowellconnection(*subscriber_management,"insert",field,update_field)
                    print("---inserting data to database---")
                    
                    return Response({
                        "success": True,
                        "message": "Thank you for subscribing to our newsletter !",
                        "Details": field,
                        "DATABASE INFO":json.loads(insert_subscriber_data),
                        "Count": serializer.data["is_valid"]
                    },status=status.HTTP_201_CREATED)
                else:
                    list_subscriber = []
                    for item in response['data']:
                        listOfSubscriber = {
                            'document_id': item['_id'],
                            'subscriberEmail': item['subscriberEmail'],
                            'typeOfSubscriber': item['typeOfSubscriber'],
                            'subscriberStatus': item['subscriberStatus']
                        }
                        list_subscriber.append(listOfSubscriber)
                    field = {
                        "subscriberEmail":subscriberEmail,
                        "subscriberStatus":subscriberStatus,
                        "typeOfSubscriber":typeOfSubscriber
                    }
                    combination_present = False
                    subscribed = False
                    for item in list_subscriber:
                        if item['subscriberEmail'] == field['subscriberEmail'] and item['typeOfSubscriber'] == field['typeOfSubscriber']:
                            combination_present = True
                            subscribed = item['subscriberStatus']
                            break
                    if combination_present:
                        if subscribed:
                            print("The combination is present and the status is true.")
                            return Response({
                                "success":True,
                                "message":f"User has already subscribed",
                                "Count": serializer.data["is_valid"]
                            },status=status.HTTP_200_OK)
                        else:
                            print("The combination is present but the status is false.")
                            for item in list_subscriber:
                                if item['subscriberEmail'] == field['subscriberEmail'] and item['typeOfSubscriber'] == field['typeOfSubscriber']:
                                    field = {
                                        "_id": item['document_id']
                                    }
                                    update_field = {
                                        "subscriberStatus": True
                                    }
                                    print("---The updation process started---")
                                    update_subscriber_data = dowellconnection(*subscriber_management,"update",field,update_field)
                                    return Response({
                                        "status":True, 
                                        "message":"Thank you resubscribing to the newsletter",
                                        "Count": serializer.data["is_valid"]
                                    },status=status.HTTP_208_ALREADY_REPORTED)
                                else:
                                    return Response({
                                        "status":False,
                                        "message": "Something went wrong while updating subscriber"
                                    },status=status.HTTP_400_BAD_REQUEST)          
                    else:
                        print("The user is not subscribed to particular combination , starting the subscription process")
                        field = {
                            "eventId": get_event_id()['event_id'],
                            "topic":topic,
                            "subscriberEmail":subscriberEmail,
                            "subscriberStatus":subscriberStatus,
                            "typeOfSubscriber":typeOfSubscriber,
                            "APIKey":uuid,
                            "API Owner Name": serializer.data["name"],
                            "API Owner Email": serializer.data["email"]
                        }
                        update_field = {
                            "status": "OK",
                        }
                        insert_subscriber_data = dowellconnection(*subscriber_management,"insert",field,update_field)
                        print("---inserting data to database---")
                        
                        return Response({
                            "success": True,
                            "message": "Thank you for subscribing to our newsletter !",
                            "Details": field,
                            "DATABASE INFO":json.loads(insert_subscriber_data),
                            "Count": serializer.data["is_valid"]
                        },status=status.HTTP_201_CREATED)
            else:
                return Response({
                    "success": False,
                    "message": f"{subscriberEmail} is not a valid email",
                    "Count": serializer.data["is_valid"]
                },status=status.HTTP_400_BAD_REQUEST)    
               
    def put(self,request,uuid):
        try:
            api_key = ApiKey.objects.get(uuid=uuid)
            print("---Got apiKey---",api_key)
        except ApiKey.DoesNotExist:
            return Response("API Key not found.", status=status.HTTP_404_NOT_FOUND)
        print("---Decrementing API key count---")
        api_key.is_valid -= 1
        api_key.save()
        serializer = ApiKeySerializer(api_key)
        topic = request.data.get("topic")
        subscriberEmail = request.data.get("subscriberEmail")
        field = {
            "topic":topic,
            "subscriberEmail":subscriberEmail
        }
        update_field={
            "status":"ok"
        }
        print("---Fetching data from database based on required data---")
        fetched_data = dowellconnection(*subscriber_management,"find",field,update_field)
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
            update_response = dowellconnection(*subscriber_management,"update",field,update_field)
            print("---Unsubscribed ! SAD---")
            return Response({
                "success": True,
                "message":"We are sorry you have unsubscribed from us, and we hope you will consider subscribing soon." , 
                "Subscriber Email Address": subscriberEmail
            },status=status.HTTP_202_ACCEPTED)
        else:
            return Response({
                "success": False,
                "message":"Already an unsubscribed!"
            },status=status.HTTP_406_NOT_ACCEPTABLE)