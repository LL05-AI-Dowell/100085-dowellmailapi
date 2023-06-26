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
import csv


load_dotenv()
# load_dotenv("/home/100085/100085-dowellmailapi/.env")
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
        api_services = request.GET.get('service')

        if type_request == "validate":
            return self.validate_email(request,uuid,api_services)
        elif type_request == 'send-email':
            return self.send_email(request,uuid,api_services)
        elif type_request == 'email-finder':
            return self.email_finder(request,uuid,api_services)
        else:
            return self.handle_error(request)

    def validate_email(self, request,uuid,api_services):
        email = request.data.get('email')
        print("---Got the required parameter to send mail---",email)
        
        validate_api_count = processApikey(uuid,api_services)
        data_count = json.loads(validate_api_count)
        print("---data_count---",data_count)
        if data_count['success'] :
            if data_count['count'] >= 0 :
                print("---Data count is ok---")
                email_validation = validateMail(SECRET_KEY,email)
                if email_validation['status'] == "valid":
                    return Response({
                        "success": True,
                        "message": f"Hurray ! {email} is a valid email",
                        "credits": data_count['count']
                    },status=status.HTTP_200_OK)
                else:
                    return Response({
                        "success": False,
                        "message": f"Sorry ! {email} is not a valid email",
                        "creits": data_count['count']
                    },status=status.HTTP_200_OK)
            return Response({
                "success": False,
                "message": data_count['message'],
                "credits": data_count['count']
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                "success": False,
                "message": data_count['message']
            }, status=status.HTTP_400_BAD_REQUEST)

    def send_email(self, request ,uuid,api_services):
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

        validate_api_count = processApikey(uuid,api_services)
        data_count = json.loads(validate_api_count)
        if data_count['success'] :
            if data_count['count'] >= 0:
                print("---Data count is ok---")
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
                        return Response({
                            "success": True,
                            "message":"Mail has been sent!!",
                            "send status":json.dumps(api_response_dict),
                            "credits": data_count['count']
                        },status=status.HTTP_200_OK)
                    except ApiException as e:
                        return Response({"error":"Exception when calling SMTPApi->send_transac_email: %s\n" % e},status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({
                    "success": False,
                    "message": f"Sorry ! {toemail} is not a valid email",
                    "credits": data_count['count']
                },status=status.HTTP_200_OK)
            else:
                return Response({
                "success": False,
                "message": data_count['message'],
                "credits": data_count['count']
                },status=status.HTTP_200_OK)
        else:
            return Response({
                "success": False,
                "message": data_count['message']
            }, status=status.HTTP_400_BAD_REQUEST)

    def email_finder(self,request,uuid,api_services):
        name = request.data.get('name')
        domain = request.data.get('domain')
        print(name, domain,uuid)
        validate_api_count = processApikey(uuid,api_services)
        data_count = json.loads(validate_api_count)
        if data_count['success'] : 
            if data_count['count'] >= 0:
                print("---Data count is ok---")
                emailFiderStatus = emailFinder(SECRET_KEY, domain, name)
                if emailFiderStatus['status'] == "valid":
                    return Response({
                        "success": True,
                        "message":"found a valid email",
                        "result": emailFiderStatus,
                        "credits": data_count['count']
                    })
                else :
                    return Response({
                        "success": False,
                        "message":"Not found a valid email",
                        "result": emailFiderStatus["failure_reason"],
                        "credits": data_count['count']
                    })
            else:
                return Response({
                "success": False,
                "message": data_count['message'],
                "credits": data_count['count']
                },status=status.HTTP_200_OK)
        else:
            return Response({
                "success": False,
                "message": data_count['message']
            }, status=status.HTTP_400_BAD_REQUEST)

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
            if api_key.is_valid >= 0:
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
                            "message": f"Hi {subscriberEmail} , Thank you for subscribing to UX Living Lab newsletter",
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
                                    "message":f"Hi {subscriberEmail}, You have already subscribed to UX Living Lab newsletter",
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
                                            "success":True,
                                            "message":f"Hi {subscriberEmail} , Thank you for resubscribing to UX Living Lab newsletter",
                                            "Count": serializer.data["is_valid"]
                                        },status=status.HTTP_200_OK)
                                    # else:
                                    #     return Response({
                                    #         "success":False,
                                    #         "message": "Something went wrong while updating subscriber"
                                    #     },status=status.HTTP_200_OK)
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
                                "message": f"Hi {subscriberEmail}, Thank you for subscribing to UX Living Lab newsletter",
                                "Details": field,
                                "DATABASE INFO":json.loads(insert_subscriber_data),
                                "Count": serializer.data["is_valid"]
                            },status=status.HTTP_201_CREATED)
                else:
                    return Response({
                        "success": False,
                        "message": f"{subscriberEmail} is not a valid email",
                        "Count": serializer.data["is_valid"]
                    },status=status.HTTP_200_OK)
            else:
                return Response({
                "success": False,
                "message": "Limit exceeded"
            }, status=status.HTTP_423_LOCKED)

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
        topic = request.data.get('topic')
        subscriberEmail = request.data.get('subscriberEmail')
        typeOfSubscriber = request.data.get('typeOfSubscriber')
        field = {
            "APIKey": uuid
        }
        update_field = {
            "status": "OK",
        }

        print("---Fetching data based on apiKey---")
        fetch_all_subscriber = dowellconnection(*subscriber_management,"fetch",field,update_field)
        response = json.loads(fetch_all_subscriber)

        field = {
            "subscriberEmail": subscriberEmail ,
            "subscriberStatus": True,
            "topic": topic,
            "typeOfSubscriber": typeOfSubscriber
        }

        found_combination = None

        for item in response['data']:
            if all(item[key] == field[key] for key in field):
                found_combination = item
                break
        if found_combination:
            data = {
                "document_id": found_combination["_id"],
                "subscriberEmail": found_combination["subscriberEmail"],
                "subscriberStatus": found_combination["subscriberStatus"],
                "topic": found_combination["topic"],
                "typeOfSubscriber": found_combination["typeOfSubscriber"]
            }
            field = {
                "_id":data["document_id"]
            }
            update_field = {
                "subscriberStatus": False
            }
            update_subscriber_status = dowellconnection(*subscriber_management,"update",field,update_field)
            return Response({
                "success": True,
                "message":f"Hi {subscriberEmail}, We are sorry you have unsubscribed from us, and we hope you will consider subscribing soon."
                }, status=status.HTTP_200_OK)
        else:
            return Response({
                "success": True,
                "message":f"Hi {subscriberEmail}, you have already unsubscribed."
                }, status=status.HTTP_200_OK)
        

@method_decorator(csrf_exempt, name='dispatch')
class sendNewsLetterToInternalTeam(APIView):
    def post(self, request):
        field = {
            "APIKey":"e4f8bbdf-d998-4b3a-bc21-e99ab8267c86"
        }
        update_field = {
            "status":"ok"
        }
        response = dowellconnection(*subscriber_management,"fetch",field,update_field)
        data = json.loads(response)
        filtered_data = [entry["subscriberEmail"] for entry in data["data"] if entry["subscriberStatus"]]
        with open("subscribers.csv", "w", newline="") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(["Email"])  
            for email in filtered_data:
                writer.writerow([email])
        return Response("Done")
    

@method_decorator(csrf_exempt, name= 'dispatch')
class unsubscribeToNewsletter(APIView):
    def get(self, request,uuid,topic,typeOfSubscriber,subscriberEmail):
        try:
            api_key = ApiKey.objects.get(uuid=uuid)
            print("---Got apiKey---",api_key)
        except ApiKey.DoesNotExist:
            return Response("API Key not found.", status=status.HTTP_404_NOT_FOUND)
        print("---Decrementing API key count---")
        api_key.is_valid -= 1
        api_key.save()
        serializer = ApiKeySerializer(api_key)
        topic = topic
        subscriberEmail = subscriberEmail
        typeOfSubscriber = typeOfSubscriber
        field = {
            "APIKey": uuid
        }
        update_field = {
            "status": "OK",
        }

        print("---Fetching data based on apiKey---")
        fetch_all_subscriber = dowellconnection(*subscriber_management,"fetch",field,update_field)
        response = json.loads(fetch_all_subscriber)

        field = {
            "subscriberEmail": subscriberEmail ,
            "subscriberStatus": True,
            "topic": topic,
            "typeOfSubscriber": typeOfSubscriber
        }

        found_combination = None

        for item in response['data']:
            if all(item[key] == field[key] for key in field):
                found_combination = item
                break
        if found_combination:
            data = {
                "document_id": found_combination["_id"],
                "subscriberEmail": found_combination["subscriberEmail"],
                "subscriberStatus": found_combination["subscriberStatus"],
                "topic": found_combination["topic"],
                "typeOfSubscriber": found_combination["typeOfSubscriber"]
            }
            field = {
                "_id":data["document_id"]
            }
            update_field = {
                "subscriberStatus": False
            }
            update_subscriber_status = dowellconnection(*subscriber_management,"update",field,update_field)
            return Response({
                "success": True,
                "message":f"Hi {subscriberEmail}, We are sorry you have unsubscribed from us, and we hope you will consider subscribing soon."
                }, status=status.HTTP_200_OK)
        else:
            return Response({
                "success": True,
                "message":f"Hi {subscriberEmail}, you have already unsubscribed."
                }, status=status.HTTP_200_OK)
