from django.db import models

class ApiKey(models.Model):
    uuid = models.CharField(max_length=255, unique=True)
    is_active = models.BooleanField(default=True)
    is_valid = models.IntegerField(default=14)

    def __str__(self):
        return str(self.uuid)
    
class SendEmail(models.Model):
    uuid = models.CharField(max_length=255)
    topic = models.CharField(max_length=255)
    toEmail = models.CharField(max_length=255)
    toName = models.CharField(max_length=255)
    fromName = models.CharField(max_length=255)
    fromEmail = models.CharField(max_length=255)
    subject = models.CharField(max_length=255)
    email_body = models.CharField(max_length=255)

    def __str__(self):
        return str(self.fromName)