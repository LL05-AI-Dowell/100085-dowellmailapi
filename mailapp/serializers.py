from rest_framework import serializers

class EmailListField(serializers.ListField):
    def to_internal_value(self, data):
        if not isinstance(data, list):
            raise serializers.ValidationError("Invalid email list format. Expected a list.")
        
        email_list = []
        for item in data:
            if not isinstance(item, dict) or 'email' not in item:
                raise serializers.ValidationError("Invalid email list format. Each item should be a dictionary with an 'email' field.")
            email_list.append(item)
        return email_list

    def to_representation(self, value):
        return value

class BulkEmailSenderSerializer(serializers.Serializer):
    email_content = serializers.CharField(allow_null=False, allow_blank=False)
    to_email_list = EmailListField(allow_empty=False)
    fromname = serializers.CharField(allow_null=False, allow_blank=False)
    fromemail = serializers.CharField(allow_null=False, allow_blank=False)
    subject = serializers.CharField(allow_null=False, allow_blank=False)
