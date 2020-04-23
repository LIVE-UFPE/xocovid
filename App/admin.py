from django.contrib import admin
from App.models import UserProfileInfo, User, Notification, Prediction, Interpolation, AccessKey

admin.site.register(UserProfileInfo)
admin.site.register(Notification)
admin.site.register(Prediction)
admin.site.register(Interpolation)
admin.site.register(AccessKey)