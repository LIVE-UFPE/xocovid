from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class UserProfileInfo(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    def __str__(self):
        return self.user.username

#MUDA ISSOOOOO
class Notification(models.Model):      
    data_atualizacao = models.DateField(null=True)
    data_notificacao = models.DateField(null=True)
    sexo = models.CharField(max_length = 50, null=True)
    idade = models.IntegerField(null=True)
    cep = models.CharField(max_length = 50, null=True)
    pais_residencia = models.CharField(max_length = 50, null=True)
    estado_residencia = models.CharField(max_length = 50, null=True)
    municipio = models.CharField(max_length = 50, null=True)
    endereco = models.CharField(max_length = 50, null=True)
    data_primeiros_sintomas = models.DateField(null=True)
    paciente_hospitalizado = models.CharField(max_length = 50, null=True)
    data_internacao = models.DateField(null=True)
    data_alta = models.DateField(null=True)
    data_isolamento = models.DateField(null=True)
    ventilacao_mecanica = models.CharField(max_length = 50, null=True)
    situacao_notificacao = models.CharField(max_length = 50, null=True)
    coleta_amostra = models.CharField(max_length = 50, null=True)
    foi_outro_local_transmissao = models.CharField(max_length = 50, null=True)
    outro_local_transmissao = models.CharField(max_length = 50, null=True)
    data_ida_outro_local_transmissao = models.DateField(null=True)
    data_volta_outro_local_transmissao = models.DateField(null=True)
    data_chegada_brasil = models.DateField(null=True)
    estado_notificacao = models.CharField(max_length = 50, null=True)
    municipio_notificacao = models.CharField(max_length = 50, null=True)
    coleta_exames = models.CharField(max_length = 50, null=True)
    classificacao = models.CharField(max_length = 50, null=True)
    resultado = models.CharField(max_length = 50, null=True)
    internado = models.CharField(max_length = 50, null=True)
    evolucao = models.CharField(max_length = 50, null=True)
    bairro = models.CharField(max_length = 50, null=True)
    latitude = models.FloatField(null=True)
    longitude = models.FloatField(null=True)

class Prediction(models.Model):
    latitude = models.FloatField(null=True)
    longitude = models.FloatField(null=True)
    prediction1 = models.FloatField(null=True)
    prediction2 = models.FloatField(null=True)
    prediction3 = models.FloatField(null=True)

class AccessKey(models.Model):
    key = models.CharField(max_length = 20, unique=True)
    used = models.BooleanField(default=False)