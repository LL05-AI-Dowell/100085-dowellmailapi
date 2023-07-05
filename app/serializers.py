from rest_framework import serializers
from .models import ApiKey

class ApiKeySerializer(serializers.ModelSerializer):
    class Meta:
        model = ApiKey
        fields = '__all__'

class APIInputCheckup(serializers.Serializer):
    content = serializers.CharField(allow_null=False, allow_blank=False)
    title = serializers.CharField(allow_null=False, allow_blank=False)