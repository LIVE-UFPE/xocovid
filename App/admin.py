from django.contrib import admin
from App.models import UserProfileInfo, User, Notification, Prediction, Interpolation, AccessKey, CasosEstado, CasosCidade, CasosEstadoHistorico

admin.site.register(UserProfileInfo)
admin.site.register(Notification)
admin.site.register(Prediction)
admin.site.register(Interpolation)
admin.site.register(CasosEstado)
admin.site.register(CasosEstadoHistorico)
admin.site.register(CasosCidade)
admin.site.register(AccessKey)