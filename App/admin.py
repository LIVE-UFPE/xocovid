from django.contrib import admin
from App.models import UserProfileInfo, User, Notification, Prediction

admin.site.register(UserProfileInfo)
admin.site.register(Notification)
admin.site.register(Prediction)