from django.contrib import admin
from App.models import UserProfileInfo, User, Notification, PredictionBR, InterpolationBR, PredictionPE, InterpolationPE, AccessKey, CasosEstado, CasosCidade, CasosEstadoHistorico, Projecao, CasosPernambuco, statesData

admin.site.register(UserProfileInfo)
admin.site.register(Notification)
admin.site.register(PredictionBR)
admin.site.register(InterpolationBR)
admin.site.register(PredictionPE)
admin.site.register(InterpolationPE)
admin.site.register(CasosEstado)
admin.site.register(CasosEstadoHistorico)
admin.site.register(CasosCidade)
admin.site.register(Projecao)
admin.site.register(CasosPernambuco)
admin.site.register(AccessKey)
admin.site.register(statesData)