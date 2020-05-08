from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class UserProfileInfo(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    def __str__(self):
        return self.user.username

class Notification(models.Model):      
    data_atualizacao = models.DateField(null=True)
    data_notificacao = models.DateField(null=True)
    sexo = models.CharField(max_length = 150, null=True)
    idade = models.IntegerField(null=True)
    cep = models.CharField(max_length = 150, null=True)
    pais_residencia = models.CharField(max_length = 150, null=True)
    estado_residencia = models.CharField(max_length = 150, null=True)
    municipio = models.CharField(max_length = 150, null=True)
    endereco = models.CharField(max_length = 150, null=True)
    data_primeiros_sintomas = models.DateField(null=True)
    paciente_hospitalizado = models.CharField(max_length = 150, null=True)
    data_internacao = models.DateField(null=True)
    data_alta = models.DateField(null=True)
    data_isolamento = models.DateField(null=True)
    ventilacao_mecanica = models.CharField(max_length = 150, null=True)
    situacao_notificacao = models.CharField(max_length = 150, null=True)
    coleta_amostra = models.CharField(max_length = 150, null=True)
    foi_outro_local_transmissao = models.CharField(max_length = 150, null=True)
    outro_local_transmissao = models.CharField(max_length = 150, null=True)
    data_ida_outro_local_transmissao = models.DateField(null=True)
    data_volta_outro_local_transmissao = models.DateField(null=True)
    data_chegada_brasil = models.DateField(null=True)
    estado_notificacao = models.CharField(max_length = 150, null=True)
    municipio_notificacao = models.CharField(max_length = 150, null=True)
    coleta_exames = models.CharField(max_length = 150, null=True)
    classificacao = models.CharField(max_length = 150, null=True)
    resultado = models.CharField(max_length = 150, null=True)
    internado = models.CharField(max_length = 150, null=True)
    evolucao = models.CharField(max_length = 150, null=True)
    bairro = models.CharField(max_length = 150, null=True)
    latitude = models.FloatField(null=True)
    longitude = models.FloatField(null=True)

class Prediction(models.Model):
    latitude = models.FloatField(null=True)
    longitude = models.FloatField(null=True)
    prediction1 = models.FloatField(null=True)
    prediction2 = models.FloatField(null=True)
    prediction3 = models.FloatField(null=True)

class Interpolation(models.Model):
    latitude = models.FloatField(null=True)
    longitude = models.FloatField(null=True)
    prediction = models.FloatField(null=True)
    date = models.DateField(null=True)

class CasosEstado(models.Model):
    data_atualizacao = models.DateField(null=True)
    estado = models.CharField(max_length = 150, null=True)
    confirmados = models.IntegerField(null=True)
    obitos = models.IntegerField(null=True)
    populacao_estimada_2019 = models.IntegerField(null=True)
    confirmados_100k = models.FloatField(null=True)

class CasosEstadoHistorico(models.Model):
    data_notificacao = models.DateField(null=True)
    estado_residencia = models.CharField(max_length = 150, null=True)
    quantidade_casos = models.IntegerField(null=True)
    obitos = models.IntegerField(null=True)
    populacao_estimada_2019 = models.IntegerField(null=True)
    confirmados_100k = models.FloatField(null=True)

class CasosCidade(models.Model):
    data_notificacao = models.DateField(null=True)
    estado_residencia = models.CharField(max_length = 150, null=True)
    municipio = models.CharField(max_length = 150, null=True)
    quantidade_casos = models.IntegerField(null=True)
    obitos = models.IntegerField(null=True)
    populacao_estimada_2019 = models.IntegerField(null=True)
    confirmados_100k = models.FloatField(null=True)

class Projecao(models.Model):
    data_notificacao = models.DateField(null=True)
    quantidade_casos = models.IntegerField(null=True)
    estado_residencia = models.CharField(max_length = 150, null=True)
    lo80 = models.IntegerField(null=True)
    hi80 = models.IntegerField(null=True)
    lo95 = models.IntegerField(null=True)
    hi95 = models.IntegerField(null=True)

class AccessKey(models.Model):
    key = models.CharField(max_length = 20, unique=True)
    used = models.BooleanField(default=False)