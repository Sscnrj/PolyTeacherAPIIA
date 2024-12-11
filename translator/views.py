from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from translator.models import Translation
from translator.serializers import TranslationSerializer
from drf_yasg.utils import swagger_auto_schema
import google.generativeai as genai
from drf_yasg import openapi
from dotenv import load_dotenv
import os

# Charger les variables d'environnement
load_dotenv()

# Lire la clé API
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY is not set in the .env file.")

# Utilisation de la clé API
genai.configure(api_key=GEMINI_API_KEY)


class AllTranslations(APIView):
        
    #fonction pour traduction
    def translate(self, source_text, source_language, target_language):
            prompt = f"Traduis '{source_text}' en {target_language}."
            genai.configure(api_key=GEMINI_API_KEY)
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(prompt)
            target_text = response.text.strip()
            
            print(f"Translated text: {target_text}")
            return target_text
        


    @swagger_auto_schema(
        manual_parameters=[
                openapi.Parameter('source_text', openapi.IN_QUERY, type=openapi.TYPE_STRING, description="source_text"),
                openapi.Parameter('source_language', openapi.IN_QUERY, type=openapi.TYPE_STRING, description="source_language"),
                openapi.Parameter('target_language', openapi.IN_QUERY, type=openapi.TYPE_STRING, description="target_language"),
            ]
    )
    def get(self, request):
        print(f"GEMINI_API_KEY: {GEMINI_API_KEY}")
        try:
            translations = Translation.objects.all()
            serializer = TranslationSerializer(translations, many=True)
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(data={'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)



    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'source_text': openapi.Schema(type=openapi.TYPE_STRING, description='Text to translate'),
                'source_language': openapi.Schema(type=openapi.TYPE_STRING, description='Source language'),
                'target_language': openapi.Schema(type=openapi.TYPE_STRING, description='Target language'),
                },
            required=['source_text', 'source_language', 'target_language']
        )
    )
    def post(self, request):
            # Récupération des paramètres via request.GET
        source_language = request.GET.get('source_language')
        source_text = request.GET.get('source_text')
        target_language = request.GET.get('target_language')

        if not source_language or not source_text or not target_language:
            return Response({'error': 'Missing required parameters'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            target_text = self.translate(source_text, source_language, target_language)

            translation = Translation.objects.create(
                source_language=source_language,
                source_text=source_text,
                target_language=target_language,
                target_text=target_text
            )

            return Response({
                    'Translation': TranslationSerializer(translation).data
                }, status=status.HTTP_201_CREATED)
        except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)