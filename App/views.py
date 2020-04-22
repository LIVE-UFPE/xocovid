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
    bairros = []
    cidades = []
    estados = []
    notifications = list(Notification.objects.all())
    notificationsB = list(Notification.objects.filter(classificacao='Confirmado').values('bairro','data_notificacao').annotate(quantidade_casos=Count('data_notificacao')).order_by('data_notificacao'))
    notificationsE = list(Notification.objects.filter(classificacao='Confirmado').values('estado_residencia','data_notificacao').annotate(quantidade_casos=Count('data_notificacao')).order_by('data_notificacao'))
    notificationsC = list(Notification.objects.filter(classificacao='Confirmado').values('municipio','data_notificacao').annotate(quantidade_casos=Count('data_notificacao')).order_by('data_notificacao'))
    notificationsOB = list(Notification.objects.filter(Q(evolucao='Óbito') & Q(classificacao='Confirmado')).values('bairro','data_notificacao').annotate(quantidade_casos=Count('data_notificacao')).order_by('data_notificacao'))
    notificationsOE = list(Notification.objects.filter(Q(evolucao='Óbito') & Q(classificacao='Confirmado')).values('estado_residencia','data_notificacao').annotate(quantidade_casos=Count('data_notificacao')).order_by('data_notificacao'))
    notificationsOC = list(Notification.objects.filter(Q(evolucao='Óbito') & Q(classificacao='Confirmado')).values('municipio','data_notificacao').annotate(quantidade_casos=Count('data_notificacao')).order_by('data_notificacao'))
    notificationsRB = list(Notification.objects.filter(Q(evolucao='Recuperado') & Q(classificacao='Confirmado')).values('bairro','data_notificacao').annotate(quantidade_casos=Count('data_notificacao')).order_by('data_notificacao'))
    notificationsRE = list(Notification.objects.filter(Q(evolucao='Recuperado') & Q(classificacao='Confirmado')).values('estado_residencia','data_notificacao').annotate(quantidade_casos=Count('data_notificacao')).order_by('data_notificacao'))
    notificationsRC = list(Notification.objects.filter(Q(evolucao='Recuperado') & Q(classificacao='Confirmado')).values('municipio','data_notificacao').annotate(quantidade_casos=Count('data_notificacao')).order_by('data_notificacao'))
    notificationsES = list(Notification.objects.filter(classificacao='Em Investigação').values('estado_residencia','data_notificacao').annotate(quantidade_casos=Count('data_notificacao')).order_by('data_notificacao'))
    notificationsCS = list(Notification.objects.filter(classificacao='Em Investigação').values('municipio','data_notificacao').annotate(quantidade_casos=Count('data_notificacao')).order_by('data_notificacao'))
    notificationsBS = list(Notification.objects.filter(classificacao='Em Investigação').values('bairro','data_notificacao').annotate(quantidade_casos=Count('data_notificacao')).order_by('data_notificacao'))
    notificationsESA = list(Notification.objects.filter(classificacao='Em Investigação').values('estado_residencia','data_notificacao').annotate(quantidade_casos=Count('data_notificacao')).order_by('data_notificacao'))
    notificationsCSA = list(Notification.objects.filter(classificacao='Em Investigação').values('municipio','data_notificacao').annotate(quantidade_casos=Count('data_notificacao')).order_by('data_notificacao'))
    notificationsBSA = list(Notification.objects.filter(classificacao='Em Investigação').values('bairro','data_notificacao').annotate(quantidade_casos=Count('data_notificacao')).order_by('data_notificacao'))
    notificationsEA = list(Notification.objects.filter(classificacao='Confirmado').values('estado_residencia','data_notificacao').annotate(quantidade_casos=Count('data_notificacao')).order_by('data_notificacao'))
    notificationsCA = list(Notification.objects.filter(classificacao='Confirmado').values('municipio','data_notificacao').annotate(quantidade_casos=Count('data_notificacao')).order_by('data_notificacao'))
    notificationsBA = list(Notification.objects.filter(classificacao='Confirmado').values('bairro','data_notificacao').annotate(quantidade_casos=Count('data_notificacao')).order_by('data_notificacao'))
    notificationsOEA = list(Notification.objects.filter(Q(evolucao='Óbito') & Q(classificacao='Confirmado')).values('estado_residencia','data_notificacao').annotate(quantidade_casos=Count('data_notificacao')).order_by('data_notificacao'))
    notificationsOCA = list(Notification.objects.filter(Q(evolucao='Óbito') & Q(classificacao='Confirmado')).values('municipio','data_notificacao').annotate(quantidade_casos=Count('data_notificacao')).order_by('data_notificacao'))
    notificationsOBA = list(Notification.objects.filter(Q(evolucao='Óbito') & Q(classificacao='Confirmado')).values('bairro','data_notificacao').annotate(quantidade_casos=Count('data_notificacao')).order_by('data_notificacao'))
    notificationsREA = list(Notification.objects.filter(Q(evolucao='Recuperado') & Q(classificacao='Confirmado')).values('estado_residencia','data_notificacao').annotate(quantidade_casos=Count('data_notificacao')).order_by('data_notificacao'))
    notificationsRCA = list(Notification.objects.filter(Q(evolucao='Recuperado') & Q(classificacao='Confirmado')).values('municipio','data_notificacao').annotate(quantidade_casos=Count('data_notificacao')).order_by('data_notificacao'))
    notificationsRBA = list(Notification.objects.filter(Q(evolucao='Recuperado') & Q(classificacao='Confirmado')).values('bairro','data_notificacao').annotate(quantidade_casos=Count('data_notificacao')).order_by('data_notificacao'))
    notificationsEO = list(Notification.objects.filter(Q(evolucao='Óbito') & Q(classificacao='Confirmado')).values('estado_residencia','data_notificacao').annotate(quantidade_casos=Count('data_notificacao')).order_by('data_notificacao'))
    notificationsEOA = list(Notification.objects.filter(Q(evolucao='Óbito') & Q(classificacao='Confirmado')).values('estado_residencia','data_notificacao').annotate(quantidade_casos=Count('data_notificacao')).order_by('data_notificacao'))
    # DEBUG counter for null types
    soma = 0
    for notification in notificationsE:
        if notification['estado_residencia'] == 'Pernambuco':
            soma += notification['quantidade_casos']
            print(str(notification['data_notificacao'])+ ' ' + str(notification['quantidade_casos']))
    print(soma)

    for (index, notification) in enumerate(notificationsB):
        try:
            if type(notification['data_notificacao']) is not type(None):
                notificationsB[index]['data_notificacao'] = notification['data_notificacao'].strftime("%d-%m-%Y")
                notificationsBA[index]['data_notificacao'] = notificationsB[index]['data_notificacao']
                notificationsBA[index]['quantidade_casos'] = notificationsBA[index]['quantidade_casos'] 
        except TypeError:
            print("error")
    for (index, notification) in enumerate(notificationsE):
        try:
            if type(notification['data_notificacao']) is not type(None):
                notificationsE[index]['data_notificacao'] = notification['data_notificacao'].strftime("%d-%m-%Y")   
                notificationsEA[index]['data_notificacao'] = notificationsE[index]['data_notificacao']
                notificationsEA[index]['quantidade_casos'] =  notificationsE[index]['quantidade_casos']
        except TypeError:
            print("error")
    
    for (index, notification) in enumerate(notificationsC):
        try:
            if type(notification['data_notificacao']) is not type(None):
                notificationsC[index]['data_notificacao'] = notification['data_notificacao'].strftime("%d-%m-%Y")   
                notificationsCA[index]['data_notificacao'] = notificationsC[index]['data_notificacao']
                notificationsCA[index]['quantidade_casos'] = notificationsC[index]['quantidade_casos'] 
        except TypeError:
            print("error")

    for (index, notification) in enumerate(notificationsOB):
        try:
            if type(notification['data_notificacao']) is not type(None):
                notificationsOB[index]['data_notificacao'] = notification['data_notificacao'].strftime("%d-%m-%Y")
                notificationsOBA[index]['data_notificacao'] = notificationsOB[index]['data_notificacao']
                notificationsOBA[index]['quantidade_casos'] = notificationsOBA[index]['quantidade_casos']
        except TypeError:
            print("error")
    for (index, notification) in enumerate(notificationsOE):
        try:
            if type(notification['data_notificacao']) is not type(None):
                notificationsOE[index]['data_notificacao'] = notification['data_notificacao'].strftime("%d-%m-%Y")   
                notificationsOEA[index]['data_notificacao'] = notificationsOE[index]['data_notificacao']
                notificationsOEA[index]['quantidade_casos'] = notificationsOEA[index]['quantidade_casos'] 
        except TypeError:
            print("error")
    
    for (index, notification) in enumerate(notificationsOC):
        try:
            if type(notification['data_notificacao']) is not type(None):
                notificationsOC[index]['data_notificacao'] = notification['data_notificacao'].strftime("%d-%m-%Y")   
                notificationsOCA[index]['data_notificacao'] = notificationsOC[index]['data_notificacao']
                notificationsOCA[index]['quantidade_casos'] = notificationsOCA[index]['quantidade_casos'] 
        except TypeError:
            print("error")


    for (index, notification) in enumerate(notificationsRB):
        try:
            if type(notification['data_notificacao']) is not type(None):
                notificationsRB[index]['data_notificacao'] = notification['data_notificacao'].strftime("%d-%m-%Y")
                notificationsRBA[index]['data_notificacao'] = notificationsRB[index]['data_notificacao']
                notificationsRBA[index]['quantidade_casos'] = notificationsRBA[index]['quantidade_casos'] 
        except TypeError:
            print("error")
    for (index, notification) in enumerate(notificationsRE):
        try:
            if type(notification['data_notificacao']) is not type(None):
                notificationsRE[index]['data_notificacao'] = notification['data_notificacao'].strftime("%d-%m-%Y")   
                notificationsREA[index]['data_notificacao'] = notificationsRE[index]['data_notificacao']
                notificationsREA[index]['quantidade_casos'] = notificationsREA[index]['quantidade_casos'] 
        except TypeError:
            print("error")
    
    for (index, notification) in enumerate(notificationsRC):
        try:
            if type(notification['data_notificacao']) is not type(None):
                notificationsRC[index]['data_notificacao'] = notification['data_notificacao'].strftime("%d-%m-%Y")   
                notificationsRCA[index]['data_notificacao'] = notificationsRC[index]['data_notificacao']
                notificationsRCA[index]['quantidade_casos'] = notificationsRCA[index]['quantidade_casos'] 
        except TypeError:
            print("error")


    for (index, notification) in enumerate(notificationsBS):
        try:
            if type(notification['data_notificacao']) is not type(None):
                notificationsBS[index]['data_notificacao'] = notification['data_notificacao'].strftime("%d-%m-%Y")
                notificationsBSA[index]['data_notificacao'] = notificationsBS[index]['data_notificacao']
                notificationsBSA[index]['quantidade_casos'] = notificationsBSA[index]['quantidade_casos']

        except TypeError:
            print("error")

    for (index, notification) in enumerate(notificationsES):
        try:
            if type(notification['data_notificacao']) is not type(None):
                notificationsES[index]['data_notificacao'] = notification['data_notificacao'].strftime("%d-%m-%Y")
                notificationsESA[index]['data_notificacao'] = notificationsES[index]['data_notificacao'] 
                notificationsESA[index]['quantidade_casos'] = notificationsESA[index]['quantidade_casos']   
        except TypeError:
            print("error")
    
    for (index, notification) in enumerate(notificationsCS):
        try:
            if type(notification['data_notificacao']) is not type(None):
                notificationsCS[index]['data_notificacao'] = notification['data_notificacao'].strftime("%d-%m-%Y")   
                notificationsCSA[index]['data_notificacao'] = notificationsCS[index]['data_notificacao'] 
                notificationsCSA[index]['quantidade_casos'] = notificationsCSA[index]['quantidade_casos']
        except TypeError:
            print("error")
    # Óbitos e acumulados
    for (index, notification) in enumerate(notificationsEO): 
        try:
            if type(notification['data_notificacao']) is not type(None):
                notificationsEO[index]['data_notificacao'] = notification['data_notificacao'].strftime("%d-%m-%Y")   
                notificationsEOA[index]['data_notificacao'] = notificationsEO[index]['data_notificacao']
            
            if index != 0:
                notificationsEOA[index]['quantidade_casos'] += notificationsEOA[index-1]['quantidade_casos']
        except TypeError:
            print("error")
    notificationsB = json.dumps(notificationsB,indent=4, sort_keys=True, default=str)
    notificationsE = json.dumps(notificationsE,indent=4, sort_keys=True, default=str)
    notificationsC = json.dumps(notificationsC,indent=4, sort_keys=True, default=str)
    notificationsOB = json.dumps(notificationsOB,indent=4, sort_keys=True, default=str)
    notificationsOE = json.dumps(notificationsOE,indent=4, sort_keys=True, default=str)
    notificationsOC = json.dumps(notificationsOC,indent=4, sort_keys=True, default=str)
    notificationsRB = json.dumps(notificationsRB,indent=4, sort_keys=True, default=str)
    notificationsRE = json.dumps(notificationsRE,indent=4, sort_keys=True, default=str)
    notificationsRC = json.dumps(notificationsRC,indent=4, sort_keys=True, default=str)
    notificationsCS = json.dumps(notificationsCS,indent=4, sort_keys=True, default=str)
    notificationsES = json.dumps(notificationsES,indent=4, sort_keys=True, default=str)
    notificationsBS = json.dumps(notificationsBS,indent=4, sort_keys=True, default=str)
    notificationsCSA = json.dumps(notificationsCSA,indent=4, sort_keys=True, default=str)
    notificationsESA = json.dumps(notificationsESA,indent=4, sort_keys=True, default=str)
    notificationsBSA = json.dumps(notificationsBSA,indent=4, sort_keys=True, default=str)
    notificationsCA = json.dumps(notificationsCA,indent=4, sort_keys=True, default=str)
    notificationsEA = json.dumps(notificationsEA,indent=4, sort_keys=True, default=str)
    notificationsBA = json.dumps(notificationsBA,indent=4, sort_keys=True, default=str)
    notificationsOCA = json.dumps(notificationsOCA,indent=4, sort_keys=True, default=str)
    notificationsOEA = json.dumps(notificationsOEA,indent=4, sort_keys=True, default=str)
    notificationsOBA = json.dumps(notificationsOBA,indent=4, sort_keys=True, default=str)
    notificationsRCA = json.dumps(notificationsRCA,indent=4, sort_keys=True, default=str)
    notificationsREA = json.dumps(notificationsREA,indent=4, sort_keys=True, default=str)
    notificationsRBA = json.dumps(notificationsRBA,indent=4, sort_keys=True, default=str)
    notificationsEOA = json.dumps(notificationsEOA,indent=4, sort_keys=True, default=str)
    notificationsEO = json.dumps(notificationsEO,indent=4, sort_keys=True, default=str)
    
    return render(request, 'graphs.html', {'obitosBase':notificationsEO, 'obitosBaseA':notificationsEOA , 'bairroBaseRA':notificationsRBA,'cidadeBaseRA':notificationsRCA,'estadoBaseRA': notificationsREA, 'bairroBaseOA':notificationsOBA,'cidadeBaseOA':notificationsOCA,'estadoBaseOA': notificationsOEA, 'bairroBaseA':notificationsBA,'cidadeBaseA':notificationsCA,'estadoBaseA': notificationsEA,'bairroBaseSA':notificationsBSA,'cidadeBaseSA':notificationsCSA,'estadoBaseSA': notificationsESA,'bairroBaseS':notificationsBS,'cidadeBaseS':notificationsCS,'estadoBaseS': notificationsES, 'cidadeBaseR':notificationsRC,'estadoBaseR':notificationsRE,'bairroBaseR':notificationsRB, 'cidadeBaseO':notificationsOC,'estadoBaseO':notificationsOE,'bairroBaseO':notificationsOB, 'cidadeBase':notificationsC,'estadoBase':notificationsE,'bairroBase':notificationsB,'bairros': bairros, 'estados':estados, 'cidades':cidades,'items_json':'1','predicts_json':'1'})

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
    context = {'register_error':'false','items_json':'1','predicts_json':'1'}

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
                return render(request, 'login.html', {'login_error':'true','items_json':'1','predicts_json':'1'})
        else:
            return render(request, 'login.html', {'login_error':'false','items_json':'1','predicts_json':'1'})

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

