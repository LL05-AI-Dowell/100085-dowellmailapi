from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from .helper import *
import json
from dotenv import load_dotenv
import os 
from .serializers import *

"""for linux server"""
load_dotenv("/home/100085/100085-dowellmailapi/.env")
if os.getenv('API_KEY'):
    API_KEY = str(os.getenv('API_KEY'))
if os.getenv('FLIKI_API_KEY'):
    FLIKI_API_KEY = str(os.getenv('FLIKI_API_KEY'))
else:
    """for windows local"""
    load_dotenv(f"{os.getcwd()}/.env")
    API_KEY = str(os.getenv('API_KEY'))
    FLIKI_API_KEY = str(os.getenv('FLIKI_API_KEY'))


@method_decorator(csrf_exempt, name='dispatch')
class health_check(APIView):
    def get(self, request ):
        return Response({
            "success": True,
            "message":"Fliki AI servering is running fine"
        },status=status.HTTP_200_OK)

@method_decorator(csrf_exempt, name='dispatch')
class process_fliki_ai(APIView):

    def post(self, request):
        type_request = request.GET.get('type')

        if type_request == "generate_video_voiceover":
            return self.generate_video_voiceover(request)
        else:
            return self.handle_error(request)
    def get(self, request):
        type_request = request.GET.get('type')

        if type_request == "get_language_list":
            return self.get_language_list(request)
        if type_request == "get_dialect_list":
            return self.get_dialect_list(request)
        if type_request == "get_voice_list":
            return self.get_voice_list(request)
        if type_request == "get_generated_video_voiceover_link":
            return self.get_generated_video_voiceover_link(request)
        else:
            return self.handle_error(request)

    """Language list from Fliki API"""
    def get_language_list(self, request):
        respsone = json.loads(get_supported_utils(FLIKI_API_KEY, "languages"))
        if not respsone["success"]:
            return Response({
                "success": True,
                "message": "Failed to get the List of languages",
                "response": respsone["data"]
            }, status=status.HTTP_400_BAD_REQUEST) 
        
        return Response({
            "success": True,
            "message": "The list of languages supported",
            "response": respsone["data"]
        }, status=status.HTTP_200_OK)
        
    """Dialect list from Fliki API"""
    def get_dialect_list(self, request):
        respsone = json.loads(get_supported_utils(FLIKI_API_KEY, "dialects"))
        if not respsone["success"]:
            return Response({
                "success": True,
                "message": "Failed to get the List of dialects",
                "response": respsone["data"]
            }, status=status.HTTP_400_BAD_REQUEST) 
        
        return Response({
            "success": True,
            "message": "The list of Dialects supported",
            "response": respsone["data"]
        }, status=status.HTTP_200_OK)

    """Voice list from Fliki API"""
    def get_voice_list(self, request):
        language_id = request.GET.get("language_id")
        dialect_id = request.GET.get("dialect_id")

        data = {
            "language_id": language_id,
            "dialect_id": dialect_id
        }

        serializer = VoiceListSerializer(data=data)
        if not serializer.is_valid():
            return Response({
                "success": False,
                "message": "Posting wrong data",
                "error": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        respsone = json.loads(get_voices(FLIKI_API_KEY, language_id, dialect_id))
        if not respsone["success"]:
            return Response({
                "success": True,
                "message": "Failed to get the List of voices",
                "response": respsone["data"]
            }, status=status.HTTP_400_BAD_REQUEST) 
        
        return Response({
            "success": True,
            "message": "The list of Voices supported",
            "response": respsone["data"]
        }, status=status.HTTP_200_OK) 
        
    """Generate video / voiceover"""
    def generate_video_voiceover(self, request):
        format_type = request.data.get("format_type")
        scenes = request.data.get("scenes")
        aspectRatio = request.data.get("aspectRatio")
        background_music_keywords = request.data.get("background_music_keywords")

        data= {
            "format_type": format_type,
            "scenes": scenes,
            "background_music_keywords": background_music_keywords,
            "aspectRatio": aspectRatio
        }

        serializer = GenerateVideoVoiceoverSerializer(data=data)
        if not serializer.is_valid():
            return Response({
                "success": False,
                "message": "Posting wrong data",
                "error": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        aspectRatio = {
            "aspectRatio": aspectRatio
        }

        response = json.loads(generate_video_or_voiceover(FLIKI_API_KEY, format_type, scenes, aspectRatio , background_music_keywords))
        if not response["success"]:
            return Response({
                "success": False,
                "message": "The requested process was failed to run successfully",
                "response": response["data"]
            }, status=status.HTTP_400_BAD_REQUEST) 
        
        return Response({
            "success": True,
            "message": "The requested process started successfully",
            "data": response["data"]
        })

    """Get generated video or voiceover """
    def get_generated_video_voiceover_link(self,request):
        generate_id = request.GET.get('generate_id')
        if not generate_id:
            return Response({
                "success": False,
                "message": "Please provide generated ID"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        respsone = json.loads(check_generation_status(FLIKI_API_KEY,generate_id))
        if not respsone["success"]:
            return Response({
                "success": False,
                "message": "Failed to generate video",
                "response": respsone["data"]
            }, status=status.HTTP_400_BAD_REQUEST) 
        
        return Response({
            "success": True,
            "message": "The video/voiceover response status",
            "response": respsone["data"]
        }, status=status.HTTP_200_OK)
    
    """HANDLE ERROR"""
    def handle_error(self, request): 
        return Response({
            "success": False,
            "message": "Invalid request type"
        }, status=status.HTTP_400_BAD_REQUEST)
    