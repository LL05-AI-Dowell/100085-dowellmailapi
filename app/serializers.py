from rest_framework import serializers
from .models import ApiKey , SendEmail

class ApiKeySerializer(serializers.ModelSerializer):
    class Meta:
        model = ApiKey
        fields = '__all__'


class SendMailSerializer(serializers.ModelSerializer):
    class Meta:
        model = SendEmail
        fields = '__all__'