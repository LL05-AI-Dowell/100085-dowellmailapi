from django.db import models

class ApiKey(models.Model):
    uuid = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_valid = models.IntegerField(default=25)
    is_paid = models.BooleanField(default=False)

    def __str__(self):
        return str(self.uuid)
