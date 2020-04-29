from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from App.forms import UserForm
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from .models import Notification
from .models import Prediction
from django.contrib.staticfiles.storage import staticfiles_storage
from django.db.models import Manager, Q
from django.db.models.query import QuerySet
from .tasks import listener
import json
import requests
from datetime import date, datetime
from django.db.models import Count

APIKEY = 'AIzaSyA9py_5Ave_r37HxH4694TpCHQJC6B63HI'

#! Todas as views que só podem ser mostradas se o usuário estiver logado, devem ter o @login_required
# ? index é uma function view. uma função que retorna a view requisitada
def index(request):
    return render(request, 'index.html')

def base(request):
    bairros = []
    cidades = []
    estados = []
    notifications = list(Notification.objects.all())
    # DEBUG counter for null types
    notificationsB = list(Notification.objects.filter(classificacao='Confirmado').values('bairro','data_notificacao').annotate(quantidade_casos=Count('data_notificacao')))
    
    for notification in notifications:
        # if type(notification.data_notificacao) != type(NoneType()):
        try:
            if (type(notification.bairro) is not type(None)) and (notification.bairro is not 'None' or ''):
                
                if (notification.bairro not in bairros):
                    bairros.append([notification.bairro])
                    cidades.append(notification.municipio)
                    estados.append(notification.estado_residencia)
        except TypeError:
            print(notification.bairro)
    
    return render(request, 'base.html', {"bairroBase":notificationsB,'bairros': bairros, 'estados':estados, 'cidades':cidades,'items_json':'1','predicts_json':'1'})

def graphs(request):
    buscas = {
        'Casos Confirmados' : {
            'estados' : list(Notification.objects.filter(classificacao='Confirmado').values('estado_residencia','data_notificacao').annotate(quantidade_casos=Count('data_notificacao')).order_by('data_notificacao')),
            'cidades' : list(Notification.objects.filter(classificacao='Confirmado').values('municipio','data_notificacao').annotate(quantidade_casos=Count('data_notificacao')).order_by('data_notificacao')),
            'bairros' : list(Notification.objects.filter(classificacao='Confirmado').values('bairro','data_notificacao').annotate(quantidade_casos=Count('data_notificacao')).order_by('data_notificacao')),
        },
        'Casos Suspeitos' : {
            'estados' : list(Notification.objects.filter(classificacao='Em Investigação').values('estado_residencia','data_notificacao').annotate(quantidade_casos=Count('data_notificacao')).order_by('data_notificacao')),
            'cidades' : list(Notification.objects.filter(classificacao='Em Investigação').values('municipio','data_notificacao').annotate(quantidade_casos=Count('data_notificacao')).order_by('data_notificacao')),
            'bairros' : list(Notification.objects.filter(classificacao='Em Investigação').values('bairro','data_notificacao').annotate(quantidade_casos=Count('data_notificacao')).order_by('data_notificacao')),
        },
        'Óbitos' : {
            'estados' : list(Notification.objects.filter(Q(evolucao='Óbito') & Q(classificacao='Confirmado')).values('estado_residencia','data_notificacao').annotate(quantidade_casos=Count('data_notificacao')).order_by('data_notificacao')),
            'cidades' : list(Notification.objects.filter(Q(evolucao='Óbito') & Q(classificacao='Confirmado')).values('municipio','data_notificacao').annotate(quantidade_casos=Count('data_notificacao')).order_by('data_notificacao')),
            'bairros' : list(Notification.objects.filter(Q(evolucao='Óbito') & Q(classificacao='Confirmado')).values('bairro','data_notificacao').annotate(quantidade_casos=Count('data_notificacao')).order_by('data_notificacao')),
        },
        'Recuperados' : {
            'estados' : list(Notification.objects.filter(Q(evolucao='Recuperado') & Q(classificacao='Confirmado')).values('estado_residencia','data_notificacao').annotate(quantidade_casos=Count('data_notificacao')).order_by('data_notificacao')),
            'cidades' : list(Notification.objects.filter(Q(evolucao='Recuperado') & Q(classificacao='Confirmado')).values('municipio','data_notificacao').annotate(quantidade_casos=Count('data_notificacao')).order_by('data_notificacao')),
            'bairros' : list(Notification.objects.filter(Q(evolucao='Recuperado') & Q(classificacao='Confirmado')).values('bairro','data_notificacao').annotate(quantidade_casos=Count('data_notificacao')).order_by('data_notificacao')),
        },
        'Isolamento Domiciliar' : {
           'estados' : list(Notification.objects.filter(Q(evolucao='Isolamento Domiciliar') & Q(classificacao='Confirmado')).values('estado_residencia','data_notificacao').annotate(quantidade_casos=Count('data_notificacao')).order_by('data_notificacao')),
            'cidades' : list(Notification.objects.filter(Q(evolucao='Isolamento Domiciliar') & Q(classificacao='Confirmado')).values('municipio','data_notificacao').annotate(quantidade_casos=Count('data_notificacao')).order_by('data_notificacao')),
            'bairros' : list(Notification.objects.filter(Q(evolucao='Isolamento Domiciliar') & Q(classificacao='Confirmado')).values('bairro','data_notificacao').annotate(quantidade_casos=Count('data_notificacao')).order_by('data_notificacao')),
        },
        'Internado' : {
           'estados' : list(Notification.objects.filter(Q(internado='Sim') & Q(classificacao='Confirmado')).values('estado_residencia','data_notificacao').annotate(quantidade_casos=Count('data_notificacao')).order_by('data_notificacao')),
            'cidades' : list(Notification.objects.filter(Q(internado='Sim') & Q(classificacao='Confirmado')).values('municipio','data_notificacao').annotate(quantidade_casos=Count('data_notificacao')).order_by('data_notificacao')),
            'bairros' : list(Notification.objects.filter(Q(internado='Sim') & Q(classificacao='Confirmado')).values('bairro','data_notificacao').annotate(quantidade_casos=Count('data_notificacao')).order_by('data_notificacao')),
        },
    }
    
    buscas = json.dumps(buscas, indent=4, sort_keys=True, default=str)
    
    return render(request, 'graphs.html', {'buscas': buscas})

@login_required
def home(request):
    context = {}
    pins = []
    predicts = []
    notifications = list(Notification.objects.all())
    predictions = list(Prediction.objects.all())
    
    # DEBUG counter for null types
    null_notes = 0
    for notification in notifications:
        try:
            if type(notification.latitude) is type(None) or type(notification.longitude) is type(None) or type(notification.bairro) is type(None):
                null_notes += 1
                raise TypeError('')
        except TypeError:
            print('error pegando Notificação, algum dado é Null')
        else:
            if notification.classificacao == "Confirmado":
                pins.append({
                    "latitude": notification.latitude,
                    "longitude": notification.longitude,
                    "data_notificacao": notification.data_notificacao.isoformat() if type(notification.data_notificacao) is not type(None) else '2000-01-01',
                    "bairro": notification.bairro,
                    # TODO adicionar entradas futuramente relevantes
                })

    # DEBUG type test
    print("De",len(notifications),",",null_notes,"tem dados nulos")

    for prediction in predictions:
        predicts.append({
            "latitude": prediction.latitude,
            "longitude": prediction.longitude,
            "intensidade": prediction.prediction,
        })

    context["items_json"] = json.dumps(pins)
    context["predicts_json"] = json.dumps(predicts)
    
    
    return render(request, 'home.html',context)

@login_required
def tela_exemplo(request, id):
    return render(request, 'exemplo/tela_exemplo.html', {'id':id,})

@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('user_login'))

def register(request):
    context = {'register_error':'false'}

    if request.method == 'POST':
        user_form = UserForm(data=request.POST)
        if user_form.is_valid():
            user = user_form.save()
            user.set_password(user.password)
            user.save()
            return HttpResponseRedirect(reverse('user_login'))
        else:
            context['register_error'] = 'true'
    
    return render(request,'registration.html',context)

def user_login(request):
    if request.user.is_authenticated:
        return home(request)
    else:
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(username=username, password=password)
            if user:
                if user.is_active:
                    login(request,user)
                    return HttpResponseRedirect(reverse('home'))
                else:
                    return HttpResponse("Your account was inactive.")
            else:
                print("Someone tried to login and failed.")
                print("They used username: {} and password: {}".format(username,password))
                return render(request, 'login.html', {'login_error':'true'})
        else:
            return render(request, 'login.html', {'login_error':'false'})

"""
! Funcionamento das views

Views nada mais é que um módulo python que agrupa um conjunto de ações.
views em django são divididas em dois tipos: views baseadas em FUNCTION e views baseadas em CLASS

* Function based View
views baseadas em funções sao feitas usando uma função em python:
    1. função recebe como argumento um objeto HttpRequest
    2. função retorna um objeto HttpResponse

são divididas em 4 estratégias básicas (CRUD):
? Create // Retrieve // Update // Delete
CRUD é a base de qualquer framework

! Só que tem mais um detalhe!!!
para acessar essa função, devemos especificar uma rota através do sistema de rotas do Django.
"""

