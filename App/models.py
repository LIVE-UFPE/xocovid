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
    sexo = models.CharField(max_length = 10, null=True)
    idade = models.IntegerField(null=True)
    cep = models.CharField(max_length = 10, null=True)
    pais_residencia = models.CharField(max_length = 20, null=True)
    estado_residencia = models.CharField(max_length = 20, null=True)
    municipio = models.CharField(max_length = 20, null=True)
    endereco = models.CharField(max_length = 50, null=True)
    paciente_hospitalizado = models.CharField(max_length = 10, null=True)
    data_internacao = models.DateField(null=True)
    data_alta = models.DateField(null=True)
    ventilacao_mecanica = models.CharField(max_length = 10, null=True)
    situacao_notificacao = models.CharField(max_length = 20, null=True)
    coleta_amostra = models.CharField(max_length = 10, null=True)
    coleta_exames = models.CharField(max_length = 10, null=True)
    classificacao = models.CharField(max_length = 20, null=True)
    resultado = models.CharField(max_length = 50, null=True)
    internado = models.CharField(max_length = 10, null=True)
    evolucao = models.CharField(max_length = 20, null=True)
    bairro = models.CharField(max_length = 20, null=True)
    latitude = models.FloatField(null=True)
    longitude = models.FloatField(null=True)