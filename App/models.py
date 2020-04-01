from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class UserProfileInfo(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    def __str__(self):
        return self.user.username

class Notification(models.Model):      
    latitude = models.FloatField(default=0.0)
    longitude = models.FloatField(default=0.0)

class Listener(models.Model):
    lastId = models.IntegerField()