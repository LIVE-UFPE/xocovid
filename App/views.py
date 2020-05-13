from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from App.forms import UserForm
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from .models import UserProfileInfo, Notification, Prediction, Interpolation, CasosEstado, CasosEstadoHistorico, CasosCidade, Projecao, CasosPernambuco
from django.contrib.staticfiles.storage import staticfiles_storage
from django.db.models import Manager, Q, F
from django.db.models.query import QuerySet
from .tasks import listener
import json
import requests
from datetime import date, datetime
from django.db.models import Count, Sum
from django.conf import settings
from App import views
from django.contrib.auth.models import User

LIBERAR_ACESSO = True

#! Todas as views que só podem ser mostradas se o usuário estiver logado, devem ter o @login_required
# ? index é uma function view. uma função que retorna a view requisitada
def index(request):
    return render(request, 'index.html')

def base(request):
    return render(request, 'base.html')

def graphs(request):
    if request.user.is_authenticated == False and LIBERAR_ACESSO == False:
        return user_login(request)
    else:
        buscas = {
            'PieChartData': list(CasosPernambuco.objects.all().values('data_atualizacao', 'obitos', 'recuperados', 'isolamento', 'internados')),
            'Casos Estado' : list(CasosEstado.objects.all().values('estado','data_atualizacao', 'obitos', 'confirmados', 'confirmados_100k', 'populacao_estimada_2019')),
            'Projeção média esperada': {
                'estados2': list(Projecao.objects.all().values('estado_residencia', 'data_notificacao', 'quantidade_casos').order_by('data_notificacao'))
            },
            'lo80': {
                'estados2': list(Projecao.objects.all().values('estado_residencia', 'data_notificacao', 'lo80').annotate(quantidade_casos=F('lo80')).order_by('data_notificacao'))
            },
            'hi80': {
                'estados2': list(Projecao.objects.all().values('estado_residencia', 'data_notificacao', 'hi80').annotate(quantidade_casos=F('hi80')).order_by('data_notificacao'))
            },
            'Melhor cenário': {
                'estados2': list(Projecao.objects.all().values('estado_residencia', 'data_notificacao', 'lo95').annotate(quantidade_casos=F('lo95')).order_by('data_notificacao'))
            },
            'Pior cenário': {
                'estados2': list(Projecao.objects.all().values('estado_residencia', 'data_notificacao', 'hi95').annotate(quantidade_casos=F('hi95')).order_by('data_notificacao'))
            },
            'Casos Confirmados' : {
                'brasil'  : list(CasosEstadoHistorico.objects.values('data_notificacao').annotate(quantidade_casos=Sum('quantidade_casos')).order_by('data_notificacao')),
                'estados' : list(Notification.objects.filter(classificacao='Confirmado').values('estado_residencia','data_notificacao').annotate(quantidade_casos=Count('data_notificacao')).order_by('data_notificacao')),
                'estados2': list(CasosEstadoHistorico.objects.all().values('estado_residencia', 'data_notificacao', 'quantidade_casos').order_by('data_notificacao')),
                'cidades' : list(Notification.objects.filter(classificacao='Confirmado').values('municipio','data_notificacao', 'estado_residencia').annotate(quantidade_casos=Count('data_notificacao')).order_by('data_notificacao')),
                'cidades2': list(CasosCidade.objects.all().values('municipio', 'data_notificacao', 'quantidade_casos', 'estado_residencia').order_by('data_notificacao')),
                'bairros' : list(Notification.objects.filter(classificacao='Confirmado').values('bairro','data_notificacao', 'estado_residencia', 'municipio').annotate(quantidade_casos=Count('data_notificacao')).order_by('data_notificacao')),
            },
            'Casos Suspeitos' : {
                'estados' : list(Notification.objects.filter(classificacao='Em Investigação').values('estado_residencia','data_notificacao').annotate(quantidade_casos=Count('data_notificacao')).order_by('data_notificacao')),
                'cidades' : list(Notification.objects.filter(classificacao='Em Investigação').values('municipio','data_notificacao', 'estado_residencia').annotate(quantidade_casos=Count('data_notificacao')).order_by('data_notificacao')),
                'bairros' : list(Notification.objects.filter(classificacao='Em Investigação').values('bairro','data_notificacao', 'estado_residencia', 'municipio').annotate(quantidade_casos=Count('data_notificacao')).order_by('data_notificacao')),
            },
            'Óbitos' : {
                'brasil'  : list(CasosEstadoHistorico.objects.values('data_notificacao').annotate(quantidade_casos=Sum('obitos')).order_by('data_notificacao')),
                'estados' : list(Notification.objects.filter(Q(evolucao='Óbito') & Q(classificacao='Confirmado')).values('estado_residencia','data_notificacao').annotate(quantidade_casos=Count('data_notificacao')).order_by('data_notificacao')),
                'estados2' : list(CasosEstadoHistorico.objects.all().values('estado_residencia', 'data_notificacao', 'obitos').annotate(quantidade_casos=F('obitos')).order_by('data_notificacao')),
                'cidades' : list(Notification.objects.filter(Q(evolucao='Óbito') & Q(classificacao='Confirmado')).values('municipio','data_notificacao', 'estado_residencia').annotate(quantidade_casos=Count('data_notificacao')).order_by('data_notificacao')),
                'cidades2' : list(CasosCidade.objects.all().values('municipio', 'data_notificacao', 'obitos', 'estado_residencia').annotate(quantidade_casos=F('obitos')).order_by('data_notificacao')),
                'bairros' : list(Notification.objects.filter(Q(evolucao='Óbito') & Q(classificacao='Confirmado')).values('bairro','data_notificacao', 'estado_residencia', 'municipio').annotate(quantidade_casos=Count('data_notificacao')).order_by('data_notificacao')),
            },
            'Recuperados' : {
                'estados' : list(Notification.objects.filter(Q(evolucao='Recuperado') & Q(classificacao='Confirmado')).values('estado_residencia','data_notificacao').annotate(quantidade_casos=Count('data_notificacao')).order_by('data_notificacao')),
                'cidades' : list(Notification.objects.filter(Q(evolucao='Recuperado') & Q(classificacao='Confirmado')).values('municipio','data_notificacao', 'estado_residencia').annotate(quantidade_casos=Count('data_notificacao')).order_by('data_notificacao')),
                'bairros' : list(Notification.objects.filter(Q(evolucao='Recuperado') & Q(classificacao='Confirmado')).values('bairro','data_notificacao', 'estado_residencia', 'municipio').annotate(quantidade_casos=Count('data_notificacao')).order_by('data_notificacao')),
            },
            'Isolamento Domiciliar' : {
                'estados' : list(Notification.objects.filter(~Q(internado='Sim') & Q(classificacao='Confirmado') & ~Q(evolucao='Óbito') & ~Q(evolucao='Recuperado')).values('estado_residencia','data_notificacao').annotate(quantidade_casos=Count('data_notificacao')).order_by('data_notificacao')),
                'cidades' : list(Notification.objects.filter(~Q(internado='Sim') & Q(classificacao='Confirmado') & ~Q(evolucao='Óbito') & ~Q(evolucao='Recuperado')).values('municipio','data_notificacao', 'estado_residencia').annotate(quantidade_casos=Count('data_notificacao')).order_by('data_notificacao')),
                'bairros' : list(Notification.objects.filter(~Q(internado='Sim') & Q(classificacao='Confirmado') & ~Q(evolucao='Óbito') & ~Q(evolucao='Recuperado')).values('bairro','data_notificacao', 'estado_residencia', 'municipio').annotate(quantidade_casos=Count('data_notificacao')).order_by('data_notificacao')),
            },
            'Internado' : {
                'estados' : list(Notification.objects.filter(Q(internado='Sim') & Q(classificacao='Confirmado') & ~Q(evolucao='Óbito') & ~Q(evolucao='Recuperado')).values('estado_residencia','data_notificacao').annotate(quantidade_casos=Count('data_notificacao')).order_by('data_notificacao')),
                'cidades' : list(Notification.objects.filter(Q(internado='Sim') & Q(classificacao='Confirmado') & ~Q(evolucao='Óbito') & ~Q(evolucao='Recuperado')).values('municipio','data_notificacao', 'estado_residencia').annotate(quantidade_casos=Count('data_notificacao')).order_by('data_notificacao')),
                'bairros' : list(Notification.objects.filter(Q(internado='Sim') & Q(classificacao='Confirmado') & ~Q(evolucao='Óbito') & ~Q(evolucao='Recuperado')).values('bairro','data_notificacao', 'estado_residencia', 'municipio'    ).annotate(quantidade_casos=Count('data_notificacao')).order_by('data_notificacao')),
            },
        }

        buscas = json.dumps(buscas, indent=4, sort_keys=True, default=str)
        
        return render(request, 'graphs.html', {'buscas': buscas})

def home(request):
    if request.user.is_authenticated == False and LIBERAR_ACESSO == False:
        return user_login(request)
    else:
        context = {}
        predicts = []
        notifications = []
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
        for note in Interpolation.objects.order_by('-date').values_list('date', flat=True).distinct():
            notifications.append(
                note.isoformat()
            )
        # DEBUG datas com interpolacao
        # print('temos',len(notifications),'datas com interpolação:')
        # print(notifications)
        maior_int = Interpolation.objects.order_by('-prediction').first().prediction
        print('maior int é',maior_int)
        context["maior_int"] = json.dumps(maior_int)
        context["items_json"] = json.dumps(notifications)
        context["predicts_json"] = json.dumps(predicts)
        return render(request, 'home.html', context)

def get_pins(request):
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

def user_logout(request):
    if request.user.is_authenticated:
        logout(request)

    return HttpResponseRedirect(reverse('user_login'))

def register(request):
    context = {'register_error':'false'}

    if request.method == 'POST':
        user_form = UserForm(data=request.POST)
        #accesskey = AccessKey.objects.filter(key=request.POST['id'])
        
        #if user_form.is_valid() and accesskey:
        if user_form.is_valid():
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
                #if accesskey[0].used == False:
                user = user_form.save()
                user.set_password(user.password)    
                user.save()

                UserProfileInfo(user=user, email=request.POST['email'], instituicao=request.POST['instituicao']).save()

                #accesskey[0].used = True
                #accesskey[0].save()

                return HttpResponseRedirect(reverse('user_login'))
                        
        context['register_error'] = 'true'
    
    return render(request,'registration.html',context)

def user_login(request):
    if request.user.is_authenticated or LIBERAR_ACESSO == True:
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
                username = get_user_model().objects.get(**kwargs)
            except User.DoesNotExist:
                username = None

            user = authenticate(username=username, password=password)

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

