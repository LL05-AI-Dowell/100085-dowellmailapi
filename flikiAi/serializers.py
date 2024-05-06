from rest_framework import serializers


class VoiceListSerializer(serializers.Serializer):
    language_id = serializers.CharField(allow_null=False, allow_blank=False)
    dialect_id = serializers.CharField(allow_null=False, allow_blank=False)


class GenerateVideoVoiceoverSerializer(serializers.Serializer):
    FORMAT_TYPE = (
        ('video', 'video'),
        ('audio', 'audio'),
    )
    ASPECT_RATIO = {
        ('portrait','portrait'),
        ('square','square'),
        ('horizontal','horizontal')
    }
    BG_MUSIC_TYPE = {
        ('happy','happy'),
        ('lofi','lofi'),
        ('sad','sad'),
        ('cry','cry'),
        ('beats','beats')
    }

    format_type = serializers.ChoiceField(allow_null=False, allow_blank=False, choices=FORMAT_TYPE)
    scenes = serializers.ListField(child=serializers.JSONField())
    aspectRatio = serializers.ChoiceField(allow_null=False, allow_blank=False, choices=ASPECT_RATIO)
    background_music_keywords = serializers.ChoiceField(allow_null=False, allow_blank=False, choices=BG_MUSIC_TYPE)
    
    def validate_scenes(self, value):
        for scene in value:
            if not all(key in scene for key in ('content', 'voiceId')):
                raise serializers.ValidationError("Each scene should contain 'content' and 'voiceId' keys.")
        return value