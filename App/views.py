from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from App.forms import UserForm
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from .models import Notification, Prediction, AccessKey, Interpolation
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
    
    return render(request, 'base.html', {'bairros': bairros, 'estados':estados, 'cidades':cidades})

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
                
        
        return render(request, 'graphs.html', {'bairros': bairros, 'estados':estados, 'cidades':cidades})

def home(request):
    if request.user.is_authenticated == False:
        return user_login(request)
    else:
        context = {}
        predicts = []
        notification = Interpolation.objects.order_by('-date').first()
        print('ultima interpolação é de',notification.date)
        predictions = list(Prediction.objects.all())
        debug = 0
        for prediction in predictions:
            predicts.append({
                "latitude": prediction.latitude,
                "longitude": prediction.longitude,
                "intensidade": prediction.prediction1,
                "intensidade2": prediction.prediction2,
                "intensidade3": prediction.prediction3,
            })
            debug += 1
        print('enviando',debug, 'pontos de predição')

        context["items_json"] = json.dumps(notification.date.isoformat())
        context["predicts_json"] = json.dumps(predicts)
        return render(request, 'home.html',context)

def get_pins(request):
    if request.user.is_authenticated == False:
        return user_login(request)
    else:
        # ? starting trial to use AJAX
        if request.is_ajax and request.method == "GET":
            day = request.GET.get("day")
            notifications = []
            print('day é', day)
                        
            for notification in Interpolation.objects.filter(date__exact= day):
                notifications.append({
                    "latitude": notification.latitude,
                    "longitude": notification.longitude,
                    "data_notificacao": notification.date.isoformat() if type(notification.date) is not type(None) else '2000-01-01',
                    "intensidade": notification.prediction
                })
            print('enviando',len(notifications), 'pontos')
            
            return JsonResponse(notifications, safe=False)
            # TODO get predictions
        else: return JsonResponse({error: "deu erro aí"})
        # # DEBUG type test
        # print("De",len(notifications),",",null_notes,"tem dados nulos")

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

