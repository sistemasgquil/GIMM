from django.db import models
class Profile(models.Model):
    phone = models.CharField(max_length=20)