import os
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import json
from .helper import *
from dotenv import load_dotenv
from .serializers import *
import datetime
from threading import Thread
load_dotenv()
# load_dotenv("/home/100085/100085-dowellmailapi/.env")
ORIGINAL_API_KEY = str(os.getenv('ORIGINAL_API_KEY'))

EMAIL_FROM_WEBSITE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Samanta Content Evaluator</title>
</head>
<body>
    <div style="font-family: Helvetica,Arial,sans-serif;min-width:100px;overflow:auto;line-height:2">
        <div style="margin:50px auto;width:70%;padding:20px 0">
          <div style="border-bottom:1px solid #eee">
            <a href="#" style="font-size:1.2em;color: #00466a;text-decoration:none;font-weight:600">Dowell UX Living Lab</a>
          </div>
          <p style="font-size:1.1em">Email : {},</p>
          <p style="font-size:1.1em">Title : {},</p>
          <p style="font-size:1.1em">Content : {}</p>
          <p style="font-size:1.1em">Confidence_level_created_by_AI : {}</p>
          <p style="font-size:1.1em">Confidence_level_created_by_Human : {}</p>
          <p style="font-size:1.1em">AI_Check : {}</p>
          <p style="font-size:1.1em">Creative : {}</p>
          <p style="font-size:1.1em">Plagiarised : {}</p>
          <p style="font-size:1.1em">Total_characters : {}</p>
          <p style="font-size:1.1em">Total_sentences : {}</p>
          <p style="font-size:1.1em">Total_paragraphs : {}</p>
        </div>
      </div>
</body>
</html>
"""

EMAIL_FROM_WEBSITE_FAILED = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Samanta Content Evaluator</title>
</head>
<body>
    <div style="font-family: Helvetica,Arial,sans-serif;min-width:100px;overflow:auto;line-height:2">
        <div style="margin:50px auto;width:70%;padding:20px 0">
          <div style="border-bottom:1px solid #eee">
            <a href="#" style="font-size:1.2em;color: #00466a;text-decoration:none;font-weight:600">Dowell UX Living Lab</a>
          </div>
          <p style="font-size:1.1em">Email : {},</p>
          <p style="font-size:1.1em">Title : {},</p>
          <p style="font-size:1.1em">Content : {}</p>
          <h1 style="font-size:1.1em">Reason : {}</h1>
        </div>
      </div>
</body>
</html>
"""
@method_decorator(csrf_exempt, name='dispatch')
class originalAITest(APIView):
    def post(self, request, userapikey):
        api_key = ORIGINAL_API_KEY
        content = request.data.get('content')
        title = request.data.get('title')

        field = {
            "content": content,
            "title": title
        }

        serializer = APIInputCheckup(data=field)
        if serializer.is_valid():
            validate_api_count = processApikey(userapikey)
            data_count = json.loads(validate_api_count)
            print("---data_count---", data_count)
            if data_count['success']:
                if data_count['total_credits'] >= 0:
                    print("---Data count is ok---")
                    response = originalAI(api_key, content, title)
                    parsed_data = json.loads(response)
                    print("---parsed_data---", parsed_data)

                    if 'success' in parsed_data and parsed_data['success']:
                        originality_score = parsed_data['ai']['score']['original']
                        ai_score = parsed_data['ai']['score']['ai']
                        plagiarism_text_score = float(parsed_data['plagiarism']['total_text_score'].strip('%'))

                        originality_score_percent = originality_score * 100
                        ai_score_percent = ai_score * 100
                        creative = 100 - plagiarism_text_score

                        readability_stats = parsed_data['readability']['textStats']
                        letter_count = readability_stats['letterCount']
                        sentence_count = readability_stats['sentenceCount']
                        paragraph_count = readability_stats['paragraphCount']

                        if ai_score <= 0.10:
                            category = "Written by Human"
                        elif ai_score <= 0.30:
                            category = "Most Probably written by Human"
                        elif ai_score <= 0.70:
                            category = "Either written by Human/AI"
                        elif ai_score <= 0.90:
                            category = "Most Probably written by AI"
                        else:
                            category = "Written by AI"

                        return Response({
                            "success": True,
                            "message": "The test was successful",
                            "Confidence level created by AI": f"{ai_score_percent:.2f}%",
                            "Confidence level created by Human": f"{originality_score_percent:.2f}%",
                            "AI Check": "{}".format(category),
                            "Plagiarised": "{:.2f}%".format(plagiarism_text_score),
                            "Creative": "{:.2f}%".format(creative),
                            "Total characters": letter_count,
                            "Total sentences": sentence_count,
                            "Total paragraphs": paragraph_count,
                            "credits": data_count['total_credits'],
                            "title": title,
                            "content": content,
                        }, status=status.HTTP_200_OK)
                    elif 'error' in parsed_data:
                        return Response({
                            "success": False,
                            "message": parsed_data['error']
                        })
                    else:
                        return Response({
                            "success": False,
                            "message": "The test was not successful",
                        }, status=status.HTTP_200_OK)
                else:
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
        else:
            return Response({
                "success": False,
                "message": serializer.errors,
            }, status=status.HTTP_200_OK)


@method_decorator(csrf_exempt, name='dispatch')
class originalAITestInternal(APIView):
    def post(self, request):
        api_key = ORIGINAL_API_KEY
        content = request.data.get('content')
        title = request.data.get('title')

        field = {
            "content": content,
            "title": title
        }

        serializer = APIInputCheckup(data=field)
        if serializer.is_valid():
            response = originalAI(api_key, content, title)
            parsed_data = json.loads(response)

            if 'success' in parsed_data and parsed_data['success']:
                originality_score = parsed_data['ai']['score']['original']
                ai_score = parsed_data['ai']['score']['ai']
                plagiarism_text_score = float(parsed_data['plagiarism']['total_text_score'].strip('%'))

                originality_score_percent = originality_score * 100
                ai_score_percent = ai_score * 100
                creative = 100 - plagiarism_text_score

                readability_stats = parsed_data['readability']['textStats']
                letter_count = readability_stats['letterCount']
                sentence_count = readability_stats['sentenceCount']
                paragraph_count = readability_stats['paragraphCount']

                if ai_score <= 0.10:
                    category = "Written by Human"
                elif ai_score <= 0.30:
                    category = "Most Probably written by Human"
                elif ai_score <= 0.70:
                    category = "Either written by Human/AI"
                elif ai_score <= 0.90:
                    category = "Most Probably written by AI"
                else:
                    category = "Written by AI"

                return Response({
                    "success": True,
                    "message": "The test was successful",
                    "Confidence level created by AI": f"{ai_score_percent:.2f}%",
                    "Confidence level created by Human": f"{originality_score_percent:.2f}%",
                    "AI Check": "{}".format(category),
                    "Plagiarised": "{:.2f}%".format(plagiarism_text_score),
                    "Creative": "{:.2f}%".format(creative),
                    "Total characters": letter_count,
                    "Total sentences": sentence_count,
                    "Total paragraphs": paragraph_count,
                    "title": title,
                    "content": content,
                }, status=status.HTTP_200_OK)
            elif 'error' in parsed_data:
                return Response({
                    "success": False,
                    "message": parsed_data['error']
                })
        return Response({
            "success": False,
            "message": serializer.errors,
        }, status=status.HTTP_200_OK)


@method_decorator(csrf_exempt, name='dispatch')
class originalityConentTest(APIView):
       def post(self, request, userapikey):
        api_key = ORIGINAL_API_KEY
        content = request.data.get('content')
        title = request.data.get('title')
        email = request.data.get('email')

        field = {
            "content": content,
            "title": title,
            "email": email
        }

        serializer = APIInputSerializerCheckup(data=field)
        if serializer.is_valid():
            
            validate_api_count = processApikey(userapikey)
            data_count = json.loads(validate_api_count)
            print("---data_count---", data_count)
            if data_count['success']:
                if data_count['total_credits'] >= 0:

                    print("---Data count is ok---") 
                  
                    response = originalAI(api_key, content, title)
                    parsed_data = json.loads(response)
                    print("---parsed_data---", parsed_data)

                    if 'success' in parsed_data and parsed_data['success']:
                        originality_score = parsed_data['ai']['score']['original']
                        ai_score = parsed_data['ai']['score']['ai']
                        plagiarism_text_score = float(parsed_data['plagiarism']['total_text_score'].strip('%'))

                        originality_score_percent = originality_score * 100
                        ai_score_percent = ai_score * 100
                        creative = 100 - plagiarism_text_score

                        readability_stats = parsed_data['readability']['textStats']
                        letter_count = readability_stats['letterCount']
                        sentence_count = readability_stats['sentenceCount']
                        paragraph_count = readability_stats['paragraphCount']

                        if ai_score <= 0.10:
                            category = "Written by Human"
                        elif ai_score <= 0.30:
                            category = "Most Probably written by Human"
                        elif ai_score <= 0.70:
                            category = "Either written by Human/AI"
                        elif ai_score <= 0.90:
                            category = "Most Probably written by AI"
                        else:
                            category = "Written by AI"

                        Confidence_level_created_by_AI= f"{ai_score_percent:.2f}%",
                        Confidence_level_created_by_Human= f"{originality_score_percent:.2f}%"
                        AI_Check = "{}".format(category)
                        Plagiarised = "{:.2f}%".format(plagiarism_text_score)
                        Creative = "{:.2f}%".format(creative)
                        Total_characters= letter_count
                        Total_sentences= sentence_count
                        Total_paragraphs= paragraph_count
                        date_time = datetime.datetime.now().strftime('%Y-%m-%d')
                        subject = f"{email} ,result from Samanta content evaluator on {date_time}"
                        email_content = EMAIL_FROM_WEBSITE.format(email,title,content,Confidence_level_created_by_AI,Confidence_level_created_by_Human,AI_Check,Plagiarised,Creative,Total_characters,Total_sentences,Total_paragraphs)
                        send_content_email = send_email("Dowell UX Living Lab", "dowell@dowellresearch.uk", subject,email_content)

                        return Response({
                            "success": True,
                            "message": "The test was successful",
                            "Confidence level created by AI": f"{ai_score_percent:.2f}%",
                            "Confidence level created by Human": f"{originality_score_percent:.2f}%",
                            "AI Check": "{}".format(category),
                            "Plagiarised": "{:.2f}%".format(plagiarism_text_score),
                            "Creative": "{:.2f}%".format(creative),
                            "Total characters": letter_count,
                            "Total sentences": sentence_count,
                            "Total paragraphs": paragraph_count,
                            "credits": data_count['total_credits'],
                            "title": title,
                            "content": content,
                        }, status=status.HTTP_200_OK)
                    elif 'error' in parsed_data:
                        return Response({
                            "success": False,
                            "message": parsed_data['error']
                        })
                    else:
                        return Response({
                            "success": False,
                            "message": "The test was not successful",
                        }, status=status.HTTP_200_OK)
                else:
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
        else:
            date_time = datetime.datetime.now().strftime('%Y-%m-%d')
            subject = f"{email} , result from Samanta content evaluator on {date_time}"
            email_content = EMAIL_FROM_WEBSITE_FAILED.format(email,title,content,serializer.errors["content"][0])
            send_content_email = send_email("Dowell UX Living Lab", "dowell@dowellresearch.uk", subject,email_content)
            return Response({
                "success": False,
                "message": serializer.errors,
            }, status=status.HTTP_200_OK)

@method_decorator(csrf_exempt, name='dispatch')
class originalityContentTestSaveToDB(APIView):
    def post(self, request, userapikey):
        api_key = ORIGINAL_API_KEY
        data = request.data
        content = data.get('content')
        title = data.get('title')
        email = data.get('email')
        occurrences = data.get('occurrences')

        occurrences = int(occurrences)
        print("-------------------------------1")
        print("-------------api key used------------------",userapikey)
        serializer = APIInputDataSerializerCheckup(data={"content": content, "title": title, "email": email, "occurrences": occurrences})
        if not serializer.is_valid():
            return Response({
                "success": False,
                "message": "Posting wrong data to API",
                "error": serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)
        
        print(occurrences)
        print("-------------------------------2")
        experience_database_service_response = json.loads(experience_database_services(email, occurrences))
        if not experience_database_service_response.get("success"):
            return Response({
                "success": False,
                "message": experience_database_service_response.get("message", "Content could not be evaluated")
            }, status=status.HTTP_400_BAD_REQUEST)

        occurrences += 1
        response = json.loads(originalAI(api_key, content, title))
        print("-------------------------------3")
        if 'success' in response and response['success']:
            print("-------------------------------")
            originality_score = response['ai']['score']['original']
            ai_score = response['ai']['score']['ai']
            plagiarism_text_score = float(response['plagiarism']['total_text_score'].strip('%'))

            originality_score_percent = originality_score * 100
            ai_score_percent = ai_score * 100
            creative = 100 - plagiarism_text_score

            readability_stats = response['readability']['textStats']
            letter_count = readability_stats['letterCount']
            sentence_count = readability_stats['sentenceCount']
            paragraph_count = readability_stats['paragraphCount']

            if ai_score <= 0.10:
                category = "Written by Human"
            elif ai_score <= 0.30:
                category = "Most Probably written by Human"
            elif ai_score <= 0.70:
                category = "Either written by Human/AI"
            elif ai_score <= 0.90:
                category = "Most Probably written by AI"
            else:
                category = "Written by AI"
            print("-------------------------------4")
            response_data = {
                "success": True,
                "message": "The test was successful",
                "Confidence level created by AI": f"{ai_score_percent:.2f}%",
                "Confidence level created by Human": f"{originality_score_percent:.2f}%",
                "AI Check": f"{category}",
                "Plagiarised": f"{plagiarism_text_score:.2f}%",
                "Creative": f"{creative:.2f}%",
                "Total characters": letter_count,
                "Total sentences": sentence_count,
                "Total paragraphs": paragraph_count,
                "title": title,
                "content": content
            }
            print("-------------------------------5")
            def save_experienced_data():
                save_experienced_product_data(
                    "SAMANTA CONTENT EVALUATOR",
                    email,
                    {
                        "Confidence level created by AI": f"{ai_score_percent:.2f}%",
                        "Confidence level created by Human": f"{originality_score_percent:.2f}%",
                        "AI Check": f"{category}",
                        "Plagiarised": f"{plagiarism_text_score:.2f}%",
                        "Creative": f"{creative:.2f}%",
                        "Total characters": letter_count,
                        "Total sentences": sentence_count,
                        "Total paragraphs": paragraph_count,
                        "title": title,
                        "content": content
                    }
                )
            print("-------------------------------6")
            def reduce_experienced_counts():
                update_user_usage(email, occurrences)

            print("-------------------------------7",)
            experienced_date = Thread(target=save_experienced_data)
            experienced_date.daemon = True
            experienced_date.start()

            experienced_reduce = Thread(target=reduce_experienced_counts)
            experienced_reduce.daemon = True
            experienced_reduce.start()

            print("-------------------------------8",)
            date_time = datetime.datetime.now().strftime('%Y-%m-%d')
            subject = f"{email} , result from Samanta content evaluator on {date_time}"
            email_content = EMAIL_FROM_WEBSITE.format(email, title, content, ai_score_percent, originality_score_percent, category, plagiarism_text_score, creative, letter_count, sentence_count, paragraph_count)
            send_content_email = send_email("Dowell UX Living Lab", "dowell@dowellresearch.uk", subject, email_content)
            return Response({
                "success": True,
                "message": "Content was successfully evaluated",
                "response": response_data
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                "success": False,
                "message": "Content could not be evaluated"
            }, status=status.HTTP_400_BAD_REQUEST)

    

    