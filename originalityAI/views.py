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
                            category = "Most Probably by Human"
                        elif ai_score <= 0.70:
                            category = "Either by Human/AI"
                        elif ai_score <= 0.90:
                            category = "Most Probably by AI"
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
                    category = "Most Probably by Human"
                elif ai_score <= 0.70:
                    category = "Either by Human/AI"
                elif ai_score <= 0.90:
                    category = "Most Probably by AI"
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
                            category = "Most Probably by Human"
                        elif ai_score <= 0.70:
                            category = "Either by Human/AI"
                        elif ai_score <= 0.90:
                            category = "Most Probably by AI"
                        else:
                            category = "Written by AI"

                        subject = "Samanta campaign was used in uxlivinglab.org"
                        email_content = EMAIL_FROM_WEBSITE.format(email,title,content)
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
            subject = "Samanta campaign was used in uxlivinglab.org , but there was an issue with it"
            email_content = EMAIL_FROM_WEBSITE_FAILED.format(email,title,content,serializer.errors["content"][0])
            send_content_email = send_email("Dowell UX Living Lab", "dowell@dowellresearch.uk", subject,email_content)
            return Response({
                "success": False,
                "message": serializer.errors,
            }, status=status.HTTP_200_OK)
