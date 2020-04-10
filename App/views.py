from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from App.forms import UserForm
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from .models import Notification, Prediction, AccessKey
from django.contrib.staticfiles.storage import staticfiles_storage
from django.db.models import Manager
from django.db.models.query import QuerySet
from .tasks import listener
import json
import requests
from datetime import date
from django.conf import settings

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
    
    return render(request, 'base.html', {'bairros': bairros, 'estados':estados, 'cidades':cidades,'items_json':'1','predicts_json':'1'})

def graphs(request):
    if request.user.is_authenticated == False:
        return user_login(request)
    else:
        bairros = []
        cidades = []
        estados = []
        notifications = list(Notification.objects.all())
        # DEBUG counter for null types
        
        for notification in notifications:
            # if type(notification.data_notificacao) != type(NoneType()):
            try:
                if (type(notification.bairro) is not type(None)) and (notification.bairro is not 'None' or ''):
                    
                    if (notification.bairro not in bairros):
                        bairros.append(notification.municipio  + '/' + notification.estado_residencia + ' - ' + notification.bairro  )
                        cidades.append(notification.municipio)
                        estados.append(notification.estado_residencia)
                        
            except TypeError:
                print(notification.bairro)
                
        
        return render(request, 'graphs.html', {'bairros': bairros, 'estados':estados, 'cidades':cidades,'items_json':'1','predicts_json':'1'})

def home(request):
    if request.user.is_authenticated == False:
        return user_login(request)
    else:
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
                "intensidade": prediction.prediction1,
                "intensidade2": prediction.prediction2,
                "intensidade3": prediction.prediction3,
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
        accesskey = AccessKey.objects.filter(key=request.POST['id'])
        if user_form.is_valid() and accesskey:
            ''' Begin reCAPTCHA validation '''
            recaptcha_response = request.POST.get('g-recaptcha-response')
            data = {
                'secret': settings.GOOGLE_RECAPTCHA_SECRET_KEY,
                'response': recaptcha_response
            }
            r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data)
            result = r.json()
            ''' End reCAPTCHA validation '''

            if result['success']:
                if accesskey[0].used == False:
                    user = user_form.save()
                    user.set_password(user.password)
                    user.save()

                    accesskey[0].used = True
                    accesskey[0].save()

                    return HttpResponseRedirect(reverse('user_login'))
                        
        context['register_error'] = 'true'
    
    return render(request,'registration.html',context)

def user_login(request):
    if request.user.is_authenticated:
        return home(request)
    else:
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')
            if '@' in username:
                kwargs = {'email': username}
            else:
                kwargs = {'username': username}
            try:
                user = get_user_model().objects.get(**kwargs)
            except User.DoesNotExist:
                user = None
                
            if user:
                if user.is_active:
                    ''' Begin reCAPTCHA validation '''
                    recaptcha_response = request.POST.get('g-recaptcha-response')
                    data = {
                        'secret': settings.GOOGLE_RECAPTCHA_SECRET_KEY,
                        'response': recaptcha_response
                    }
                    r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data)
                    result = r.json()
                    ''' End reCAPTCHA validation '''
                    if result['success']:
                        login(request,user)
                        return HttpResponseRedirect(reverse('home'))
            
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

