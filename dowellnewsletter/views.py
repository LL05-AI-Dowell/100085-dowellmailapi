import os
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from .helper import * 
from .constants import *
from dotenv import load_dotenv
import csv
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException

load_dotenv()
SECRET_KEY = str(os.getenv('SECRET_KEY'))
SENDINGBLUE_API_KEY = str(os.getenv('SENDINGBLUE_API_KEY')) 

@method_decorator(csrf_exempt, name='dispatch')
class newslettersystem(APIView):
    def post(self,request,api_key):
        type_request = request.GET.get('type')

        if type_request == "subscribe":
            return self.subscribeNewsletters(request,api_key)
        elif type_request == 'unsubscribe':
            return self.unSubscribeNewsletters(request,api_key)
        elif type_request == 'distribute':
            return self.distributeNewsletters(request,api_key)
        elif type_request == 'subscriberlist':
            return self.subscriberList(request,api_key)
        
        elif type_request == "subscribe_newsletter":
            return self.internalsubscribeNewsletters(request,api_key)
        elif type_request == 'unsubscribe_newsletter':
            return self.internalunSubscribeNewsletters(request,api_key)
        elif type_request == 'distribute_newsletter':
            return self.internaldistributeNewsletters(request,api_key)
        elif type_request == 'subscriberlists':
            return self.internalsubscriberList(request,api_key)
        else:
            return self.handle_error(request)
        
    def subscribeNewsletters(self,request,api_key):
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
                field = {
                    "APIKey": api_key
                }
                update_field = {
                    "status": "OK",
                }

                print("---Fetching data based on apiKey---")
                fetch_all_subscriber = dowellconnection(*subscriber_management,"fetch",field,update_field)
                response = json.loads(fetch_all_subscriber)
                print("---all subacriber data is fetched---")
                validate_api_count = processApikey(api_key)
                data_count = json.loads(validate_api_count)
                print("---data count is---",data_count)
                print("---data_count---",data_count)
                if data_count['success'] :
                    if data_count['total_credits'] >= 0 :
                        print("---Data count is ok---")
                        email_validation = validateMail(SECRET_KEY,subscriberEmail)
                        print("---Checking the the email is valid---")
                        if email_validation['status'] == "valid":
                            print("---Email is verified and Starting subscription Processing---")
                            if(len(response["data"]) == 0):
                                field = {
                                    "topic":topic,
                                    "subscriberEmail":subscriberEmail,
                                    "subscriberStatus":subscriberStatus,
                                    "typeOfSubscriber":typeOfSubscriber,
                                    "APIKey":api_key,
                                    "reason_to_unsubscribe": ""
                                }
                                update_field = {
                                    "status": "OK",
                                }
                                insert_subscriber_data = dowellconnection(*subscriber_management,"insert",field,update_field)
                                print("---inserting data to database---")

                                return Response({
                                    "success": True,
                                    "message": f"Hi {subscriberEmail} , Thank you for subscribing to newsletter",
                                    "Details": field,
                                    "DATABASE INFO":json.loads(insert_subscriber_data),
                                    "Credits": data_count['count']
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
                                            "message":f"Hi {subscriberEmail}, You have already subscribed to newsletter",
                                            "Credits": data_count['count']
                                        },status=status.HTTP_200_OK)
                                    else:
                                        print("---The combination is present but the status is false.---")
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
                                                    "message":f"Hi {subscriberEmail} , Thank you for resubscribing to newsletter",
                                                    "Credits": data_count['count']
                                                },status=status.HTTP_200_OK)
                                else:            
                                    print("The user is not subscribed to particular combination , starting the subscription process")
                                    field = {
                                        "topic":topic,
                                        "subscriberEmail":subscriberEmail,
                                        "subscriberStatus":subscriberStatus,
                                        "typeOfSubscriber":typeOfSubscriber,
                                        "APIKey":api_key,
                                        "reason_to_unsubscribe": ""
                                    }
                                    update_field = {
                                        "status": "OK",
                                    }
                                    insert_subscriber_data = dowellconnection(*subscriber_management,"insert",field,update_field)
                                    print("---inserting data to database---")

                                    return Response({
                                        "success": True,
                                        "message": f"Hi {subscriberEmail}, Thank you for subscribing to newsletter",
                                        "Details": field,
                                        "DATABASE INFO":json.loads(insert_subscriber_data),
                                        "Credits":data_count['total_credits']
                                    },status=status.HTTP_201_CREATED)
                        else:
                            return Response({
                                "success": False,
                                "message": f"{subscriberEmail} is not a valid email",
                                "Credits":data_count['total_credits']
                            },status=status.HTTP_200_OK)
                    else :
                        return Response({
                            "success": False,
                            "message": data_count['message'],
                            "credits": data_count['total_credits']
                        }, status=status.HTTP_200_OK)
                else:
                    return Response({
                        "success": False,
                        "message": data_count['message']
                    }, status=status.HTTP_400_BAD_REQUEST)
    
    def unSubscribeNewsletters(self,request,api_key):
        topic = request.data.get('topic')
        subscriberEmail = request.data.get('subscriberEmail')
        typeOfSubscriber = request.data.get('typeOfSubscriber')
        reason_to_unsubscribe = request.data.get('reasonToUnsubscribe',None)
        field = {
            "APIKey": api_key
        }
        update_field = {
            "status": "OK",
        }

        print("---Fetching data based on apiKey---")
        fetch_all_subscriber = dowellconnection(*subscriber_management,"fetch",field,update_field)
        response = json.loads(fetch_all_subscriber)
        validate_api_count = processApikey(api_key)
        data_count = json.loads(validate_api_count)
        print("---data_count---",data_count)
        if data_count['success'] :
            if data_count['total_credits'] >= 0 :
                print("---Data count is ok---")
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
                        "subscriberStatus": False,
                        "reason_to_unsubscribe": reason_to_unsubscribe
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
            else :
                return Response({
                    "success": False,
                    "message": data_count['message'],
                    "credits": data_count['total_credits']
                }, status=status.HTTP_200_OK)
        else:
            return Response({
                "success": False,
                "message": data_count['message']
            }, status=status.HTTP_400_BAD_REQUEST)

    def distributeNewsletters(self,request,api_key):
        email_list = request.data.get('email')
        file = request.FILES.get('file')
        subject = request.data.get('subject')
        from_email = request.data.get('fromEmail')
        from_name = request.data.get('fromName')
        emailBody = file.read().decode('utf-8')
        email_list = json.loads(email_list)
        validate_api_count = processApikey(api_key)
        data_count = json.loads(validate_api_count)
        print("---data_count---",data_count)
        if data_count['success'] :
            if data_count['total_credits'] >= 0 :
                print("---Data count is ok---")
                configuration = sib_api_v3_sdk.Configuration()
                configuration.api_key['api-key'] = SENDINGBLUE_API_KEY
                api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))
                subject = subject
                html_content = emailBody
                sender = {"name": from_name, "email": from_email}
                to = email_list
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
                        "Credits":data_count['total_credits']
                    },status=status.HTTP_200_OK)
                except ApiException as e:
                    return Response({
                        "success": False,
                        "message":"Exception when calling SMTPApi->send_transac_email: %s\n" % e
                    },status=status.HTTP_400_BAD_REQUEST)
            else :
                return Response({
                    "success": False,
                    "message": data_count['message'],
                    "credits": data_count['total_credits']
                }, status=status.HTTP_200_OK)
        else:
            return Response({
                "success": False,
                "message": data_count['message']
            }, status=status.HTTP_400_BAD_REQUEST)
    
    def subscriberList(self,request,api_key):
        field = {
            "APIKey": api_key
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
    
    """INTERNAL NEWSLETTERS"""
    def internalsubscribeNewsletters(self,request,service_key):
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
                field = {
                    "APIKey": service_key
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
                            "topic":topic,
                            "subscriberEmail":subscriberEmail,
                            "subscriberStatus":subscriberStatus,
                            "typeOfSubscriber":typeOfSubscriber,
                            "service_key":service_key,
                            "reason_to_unsubscribe": ""
                        }
                        update_field = {
                            "status": "OK",
                        }
                        insert_subscriber_data = dowellconnection(*subscriber_management,"insert",field,update_field)
                        print("---inserting data to database---")

                        return Response({
                            "success": True,
                            "message": f"Hi {subscriberEmail} , Thank you for subscribing to newsletter",
                            "Details": field,
                            "DATABASE INFO":json.loads(insert_subscriber_data),
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
                                    "message":f"Hi {subscriberEmail}, You have already subscribed to newsletter"
                                },status=status.HTTP_200_OK)
                            else:
                                print("---The combination is present but the status is false.---")
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
                                            "message":f"Hi {subscriberEmail} , Thank you for resubscribing to newsletter"
                                        },status=status.HTTP_200_OK)
                        else:            
                            print("The user is not subscribed to particular combination , starting the subscription process")
                            field = {
                                "topic":topic,
                                "subscriberEmail":subscriberEmail,
                                "subscriberStatus":subscriberStatus,
                                "typeOfSubscriber":typeOfSubscriber,
                                "service_key":service_key,
                                "reason_to_unsubscribe": ""
                            }
                            update_field = {
                                "status": "OK",
                            }
                            insert_subscriber_data = dowellconnection(*subscriber_management,"insert",field,update_field)
                            print("---inserting data to database---")

                            return Response({
                                "success": True,
                                "message": f"Hi {subscriberEmail}, Thank you for subscribing to newsletter",
                                "Details": field,
                                "DATABASE INFO":json.loads(insert_subscriber_data)
                            },status=status.HTTP_201_CREATED)
                else:
                    return Response({
                        "success": False,
                        "message": f"{subscriberEmail} is not a valid email",
                    },status=status.HTTP_200_OK)

    def internalunSubscribeNewsletters(self,request,api_key):
        topic = request.data.get('topic')
        subscriberEmail = request.data.get('subscriberEmail')
        typeOfSubscriber = request.data.get('typeOfSubscriber')
        reason_to_unsubscribe = request.data.get('reasonToUnsubscribe',None)
        field = {
            "service_key": api_key
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
                "subscriberStatus": False,
                "reason_to_unsubscribe": reason_to_unsubscribe
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

    def internalsubscriberList(self,request,api_key):
        field = {
            "service_key": api_key
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
                
    def handle_error(self, request):
        return Response({
            "success": False,
            "message": "Invalid request type"
        }, status=status.HTTP_400_BAD_REQUEST)
    

