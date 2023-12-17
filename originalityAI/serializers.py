from rest_framework import serializers

class APIInputCheckup(serializers.Serializer):
    content = serializers.CharField(allow_null=False, allow_blank=False)
    title = serializers.CharField(allow_null=False, allow_blank=False)

class WordCountValidator:
    def __init__(self, min_words):
        self.min_words = min_words

    def __call__(self, value):
        words = value.split()
        if len(words) < self.min_words:
            raise serializers.ValidationError(
                f"Content must have at least {self.min_words} words."
            )

class APIInputSerializerCheckup(serializers.Serializer):
    content = serializers.CharField(allow_null=False, allow_blank=False)
    title = serializers.CharField(allow_null=False, allow_blank=False)
    email = serializers.EmailField(allow_null=False, allow_blank=False)

    def validate_content(self, value):
        min_words = 60
        WordCountValidator(min_words)(value)
        return value
class APIInputDataSerializerCheckup(serializers.Serializer):
    content = serializers.CharField(allow_null=False, allow_blank=False)
    title = serializers.CharField(allow_null=False, allow_blank=False)
    email = serializers.EmailField(allow_null=False, allow_blank=False)
    occurrences = serializers.IntegerField()

    def validate_content(self, value):
        min_words = 60
        WordCountValidator(min_words)(value)
        return value
