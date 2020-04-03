from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from App.forms import UserForm
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from .models import Notification, Listener
from background_task import background
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from django.contrib.staticfiles.storage import staticfiles_storage
import json
import requests
from django.db.models import Manager
from django.db.models.query import QuerySet

APIKEY = 'AIzaSyA9py_5Ave_r37HxH4694TpCHQJC6B63HI'

#! Todas as views que só podem ser mostradas se o usuário estiver logado, devem ter o @login_required
# ? index é uma function view. uma função que retorna a view requisitada
def index(request):
    return render(request, 'index.html')

@login_required
def home(request):
    context = {}
    pins = []
    notifications = list(Notification.objects.all())
    for notification in notifications:
        pins.append({
            "latitude": notification.latitude,
            "longitude": notification.longitude
        })
    # print(type(pins[0]))

    context["items_json"] = json.dumps(pins)
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
        return render(request, 'home.html')
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

@background(schedule=None)
def listener():
    print("Executando listener")

    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)    
    client = gspread.authorize(creds)
    sheet = client.open_by_url("https://docs.google.com/spreadsheets/d/1WzjB9vKSRvEBPBMYt6IZKitn4Na6NMI9OXCgaMGmlWw/edit?usp=sharing").sheet1

    lastId = Listener.objects.get(id=1).lastId
    nextId = lastId + 1

    try: 
        id = int(sheet.cell(4 + nextId, 1).value)
        if id != None:
            lastId+=1
            endereco = sheet.cell(4 + nextId, 17).value
            municipio = sheet.cell(4 + nextId, 16).value
            estado = sheet.cell(4 + nextId, 14).value
            pais = sheet.cell(4 + nextId, 13).value

            endereco_completo = endereco + ' ' + municipio + ' ' + estado + ' ' + pais
            enderecoJSON = requestData(request=endereco_completo, type='google')
            if enderecoJSON:
                country, state, city, neighborhood, cep, latitude, longitude = getDatas(json=enderecoJSON['results'])
                try:
                    if latitude:
                        newNotification = Notification.objects.get(id = nextId)
                        newNotification.latitude = float(latitude)
                        newNotification.longitude = float(longitude)
                        newNotification.save()
                except:
                    if latitude:
                        n = Notification(id = nextId, latitude = float(latitude), longitude = float(longitude))
                        n.save()

            newListener = Listener.objects.get(id=1)
            newListener.lastId = nextId
            newListener.save()
    except:
        print('Nenhum dado disponível')

    print("Listener parado")

def requestData(request=None, type='google'):
	if type=='google':
		url_api = ('https://maps.googleapis.com/maps/api/geocode/json?address='+request+'&key='+APIKEY)
	elif type=='cep':
		url_api = ('http://cep.republicavirtual.com.br/web_cep.php?cep='+request+'&formato=json')

	req = requests.get(url_api)
	if req.status_code == 200:
		dados_json = json.loads(req.text)
		return dados_json

def getDatas(json):
	country = None
	state = None
	city = None
	neighborhood = None
	cep = None
	latitude = None
	longitude = None	

	try:
		for data in json[0]['address_components']:
			if 'country' in data['types']:
				country = data['long_name']

			if 'administrative_area_level_1' in data['types']:
				state = data['long_name']

			if 'administrative_area_level_2' in data['types']:
				city = data['long_name']

			if 'sublocality' in data['types']:
				neighborhood = data['long_name']

			if 'postal_code' in data['types']:
				cep = data['long_name']

		latitude = json[0]['geometry']['location']['lat']
		longitude = json[0]['geometry']['location']['lng']
	except:
		print('Erro na busca do google maps')
	
	return country, state, city, neighborhood, cep, latitude, longitude

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