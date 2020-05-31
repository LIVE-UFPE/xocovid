from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from App.forms import UserForm
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from .models import UserProfileInfo, Notification, PredictionBR, InterpolationBR, PredictionPE, InterpolationPE, CasosEstado, CasosEstadoHistorico, CasosCidade, Projecao, CasosPernambuco
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
import os

stateName = {
    'AC': 'Acre',
    'AL': 'Alagoas',
    'AP': 'Amapá',
    'AM': 'Amazonas',
    'BA': 'Bahia',
    'CE': 'Ceará',
    'DF': 'Distrito Federal',
    'ES': 'Espírito Santo',
    'GO': 'Goiás',
    'MA': 'Maranhão',
    'MT': 'Mato Grosso',
    'MS': 'Mato Grosso do Sul',
    'MG': 'Minas Gerais',
    'PA': 'Pará',
    'PB': 'Paraíba',
    'PR': 'Paraná',
    'PE': 'Pernambuco',
    'PI': 'Piauí',
    'RJ': 'Rio de Janeiro',
    'RN': 'Rio Grande do Norte',
    'RS': 'Rio Grande do Sul',
    'RO': 'Rondônia',
    'RR': 'Roraima',
    'SC': 'Santa Catarina',
    'SP': 'São Paulo',
    'SE': 'Sergipe',
    'TO': 'Tocantins'
}

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
        with open(os.path.join(os.path.dirname(__file__))+'/static/filter/filter.json') as json_file:
            data = json.load(json_file)
        
        return render(request, 'graphs.html', {'template': "'graphs'", 'data': data})

def home(request):
    if request.user.is_authenticated == False and LIBERAR_ACESSO == False:
        return user_login(request)
    else:
        with open(os.path.join(os.path.dirname(__file__))+'/static/filter/filter.json') as json_file:
            data = json.load(json_file)
        context = {}
        predicts = []
        predictsPE = []
        notifications = []
        notificationsPE = []
        # ! inicialmente é BR
        predictions = list(PredictionBR.objects.all())
        predictionsPE = list(PredictionPE.objects.all())
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
        print('enviando',debug, 'pontos de predição do BR')
        debug = 0
        for prediction in predictionsPE:
            predictsPE.append({
                "latitude": prediction.latitude,
                "longitude": prediction.longitude,
                "intensidade": prediction.prediction1,
                "intensidade2": prediction.prediction2,
                "intensidade3": prediction.prediction3,
            })
            debug += 1
        print('enviando',debug, 'pontos de predição do PE')
        for note in InterpolationBR.objects.order_by('-date').values_list('date', flat=True).distinct():
            notifications.append(
                note.isoformat()
            )
        for note in InterpolationPE.objects.order_by('-date').values_list('date', flat=True).distinct():
            notificationsPE.append(
                note.isoformat()
            )
        # DEBUG datas com interpolacao
        # print('temos',len(notifications),'datas com interpolação:')
        # print(notifications)
        maior_int = InterpolationBR.objects.order_by('-prediction').first().prediction
        maior_int_PE = InterpolationPE.objects.order_by('-prediction').first().prediction
        print('maior int BR é',maior_int,'e maior int PE é',maior_int_PE)
        context['template'] = "'home'"
        context["maior_int"] = json.dumps(maior_int)
        context["maior_int_pe"] = json.dumps(maior_int_PE)
        context["items_json"] = json.dumps(notifications)
        context["items_json_pe"] = json.dumps(notificationsPE)
        context["predicts_json"] = json.dumps(predicts)
        context["predicts_pe_json"] = json.dumps(predictsPE)
        context["data"] = data
        return render(request, 'home.html', context)

def get_pins(request):
    # ! inicialmente é BR
    if request.is_ajax and request.method == "GET":
        day = request.GET.get("day")
        brasil_heat = request.GET.get("brasilheat")
        if brasil_heat == 'true': brasil_heat = True
        else: brasil_heat = False
        notifications = []
        print('day é', day, "e brasil_heat é", brasil_heat)

        if brasil_heat:
            for notification in InterpolationBR.objects.filter(date__exact= day):
                notifications.append({
                    "latitude": notification.latitude,
                    "longitude": notification.longitude,
                    "data_notificacao": notification.date.isoformat() if type(notification.date) is not type(None) else '2000-01-01',
                    "intensidade": notification.prediction
                })
        else:
            for notification in InterpolationPE.objects.filter(date__exact= day):
                notifications.append({
                    "latitude": notification.latitude,
                    "longitude": notification.longitude,
                    "data_notificacao": notification.date.isoformat() if type(notification.date) is not type(None) else '2000-01-01',
                    "intensidade": notification.prediction
                })

        print('enviando',len(notifications), 'pontos')
        
        return JsonResponse(notifications, safe=False)
    else: return JsonResponse({'error': "deu erro aí"})
    # # DEBUG type test
    # print("De",len(notifications),",",null_notes,"tem dados nulos")

def get_data(request):
    if request.is_ajax and request.method == "GET":
        informacao = request.GET['informacao']
        keyBusca = request.GET['keyBusca']
        estado = request.GET['estado']
        cidade = request.GET['cidade']
        bairro = request.GET['bairro']
        response = []
        if informacao == 'PieChartData':
            response = list(CasosPernambuco.objects.all().values('data_atualizacao', 'obitos', 'recuperados', 'isolamento', 'internados'))
        elif informacao == 'Casos Estado':
            if estado == '':
                response = list(CasosEstado.objects.all().values('estado', 'data_atualizacao', 'obitos', 'confirmados', 'confirmados_100k', 'populacao_estimada_2019'))
            else:
                response = list(CasosEstado.objects.filter(estado=estado).values('data_atualizacao', 'obitos', 'confirmados', 'confirmados_100k', 'populacao_estimada_2019'))
        elif informacao == 'Projeção média esperada':
            response = list(Projecao.objects.filter(estado_residencia=estado).values('data_notificacao', 'quantidade_casos').order_by('data_notificacao'))
        elif informacao == 'lo80':
            response = list(Projecao.objects.filter(estado_residencia=estado).values('data_notificacao', 'lo80').annotate(quantidade_casos=F('lo80')).order_by('data_notificacao'))
        elif informacao == 'hi80':
            response = list(Projecao.objects.filter(estado_residencia=estado).values('data_notificacao', 'hi80').annotate(quantidade_casos=F('hi80')).order_by('data_notificacao'))
        elif informacao == 'Melhor cenário':
            response = list(Projecao.objects.filter(estado_residencia=estado).values('data_notificacao', 'lo95').annotate(quantidade_casos=F('lo95')).order_by('data_notificacao'))
        elif informacao == 'Pior cenário':
            response = list(Projecao.objects.filter(estado_residencia=estado).values('data_notificacao', 'hi95').annotate(quantidade_casos=F('hi95')).order_by('data_notificacao'))
        elif informacao == 'Casos Confirmados':
            if keyBusca == 'brasil':
                response = list(CasosEstadoHistorico.objects.values('data_notificacao').annotate(quantidade_casos=Sum('quantidade_casos')).order_by('data_notificacao'))
            elif keyBusca == 'estados':
                response = list(Notification.objects.filter(Q(classificacao='Confirmado')&Q(estado_residencia=estado)).values('data_notificacao').annotate(quantidade_casos=Count('data_notificacao')).order_by('data_notificacao'))
            elif keyBusca == 'estados2':
                response = list(CasosEstadoHistorico.objects.filter(estado_residencia=estado).values('data_notificacao', 'quantidade_casos').filter(estado_residencia=estado).order_by('data_notificacao'))
            elif keyBusca == 'cidades':
                response = list(Notification.objects.filter(Q(classificacao='Confirmado')&Q(municipio=cidade)).values('data_notificacao').annotate(quantidade_casos=Count('data_notificacao')).order_by('data_notificacao'))
            elif keyBusca == 'cidades2':
                response = list(CasosCidade.objects.filter(municipio=cidade).values('data_notificacao', 'quantidade_casos').order_by('data_notificacao'))
            elif keyBusca == 'bairros':
                response = list(Notification.objects.filter(Q(classificacao='Confirmado')&Q(bairro=bairro)).values('data_notificacao').annotate(quantidade_casos=Count('data_notificacao')).order_by('data_notificacao'))
            
            # ? pega dados de todos os estados, dado o dia!
            elif keyBusca == 'estadosdia':
                dia = request.GET['dia']
                response = list(CasosEstadoHistorico.objects.filter(data_notificacao=datetime.strptime(dia, '%Y-%m-%d')).values('estado_residencia','quantidade_casos','obitos').order_by('-quantidade_casos'))

            elif keyBusca == 'cidadesdia':
                dia = request.GET['dia']
                response = list(CasosCidade.objects.filter(Q(municipio=cidade)&Q(data_notificacao=datetime.strptime(dia, '%Y-%m-%d'))).values('estado_residencia','quantidade_casos','obitos').order_by('-quantidade_casos'))
        
        elif informacao == 'Casos Suspeitos':
            if keyBusca == 'estados':
                response = list(Notification.objects.filter(Q(classificacao='Em Investigação')&Q(estado_notificacao=estado)).values('data_notificacao').annotate(quantidade_casos=Count('data_notificacao')).order_by('data_notificacao'))
            elif keyBusca == 'cidades':
                response = list(Notification.objects.filter(Q(classificacao='Em Investigação')&Q(municipio=cidade)).values('data_notificacao').annotate(quantidade_casos=Count('data_notificacao')).order_by('data_notificacao'))
            elif keyBusca == 'bairros':
                response = list(Notification.objects.filter(Q(classificacao='Em Investigação')&Q(bairro=bairro)).values('data_notificacao').annotate(quantidade_casos=Count('data_notificacao')).order_by('data_notificacao'))
        elif informacao == 'Óbitos':
            if keyBusca == 'brasil':
                response = list(CasosEstadoHistorico.objects.values('data_notificacao').annotate(quantidade_casos=Sum('obitos')).order_by('data_notificacao'))
            elif keyBusca == 'estados':
                response = list(Notification.objects.filter(Q(evolucao='Óbito')&Q(classificacao='Confirmado')&Q(estado_residencia=estado)).values('data_notificacao').annotate(quantidade_casos=Count('data_notificacao')).order_by('data_notificacao'))
            elif keyBusca == 'estados2':
                response = list(CasosEstadoHistorico.objects.filter(estado_residencia=estado).values('data_notificacao', 'obitos').annotate(quantidade_casos=F('obitos')).order_by('data_notificacao'))
            elif keyBusca == 'cidades':
                response = list(Notification.objects.filter(Q(evolucao='Óbito')&Q(classificacao='Confirmado')&Q(municipio=cidade)).values('data_notificacao').annotate(quantidade_casos=Count('data_notificacao')).order_by('data_notificacao'))
            elif keyBusca == 'cidades2':
                response = list(CasosCidade.objects.filter(municipio=cidade).values('data_notificacao', 'obitos').annotate(quantidade_casos=F('obitos')).order_by('data_notificacao'))
            elif keyBusca == 'bairros':
                response = list(Notification.objects.filter(Q(evolucao='Óbito')&Q(classificacao='Confirmado')&Q(bairro=bairro)).values('data_notificacao').annotate(quantidade_casos=Count('data_notificacao')).order_by('data_notificacao'))
        elif informacao == 'Recuperados':
            if keyBusca == 'estados':
                response = list(Notification.objects.filter(Q(evolucao='Recuperado')&Q(classificacao='Confirmado')&Q(estado_notificacao=estado)).values('data_notificacao').annotate(quantidade_casos=Count('data_notificacao')).order_by('data_notificacao'))
            elif keyBusca == 'cidades':
                response = list(Notification.objects.filter(Q(evolucao='Recuperado')&Q(classificacao='Confirmado')&Q(municipio=cidade)).values('data_notificacao').annotate(quantidade_casos=Count('data_notificacao')).order_by('data_notificacao'))
            elif keyBusca == 'bairros':
                response = list(Notification.objects.filter(Q(evolucao='Recuperado')&Q(classificacao='Confirmado')&Q(bairro=bairro)).values('data_notificacao').annotate(quantidade_casos=Count('data_notificacao')).order_by('data_notificacao'))
        elif informacao == 'Isolamento Domiciliar':
            if keyBusca == 'estados':
                response = list(Notification.objects.filter(~Q(internado='Sim')&Q(classificacao='Confirmado')&~Q(evolucao='Óbito')&~Q(evolucao='Recuperado')&Q(estado_notificacao=estado)).values('data_notificacao').annotate(quantidade_casos=Count('data_notificacao')).order_by('data_notificacao'))
            elif keyBusca == 'cidades':
                response = list(Notification.objects.filter(~Q(internado='Sim')&Q(classificacao='Confirmado')&~Q(evolucao='Óbito')&~Q(evolucao='Recuperado')&Q(municipio=cidade)).values('data_notificacao').annotate(quantidade_casos=Count('data_notificacao')).order_by('data_notificacao'))
            elif keyBusca == 'bairros':
                response = list(Notification.objects.filter(Q(internado='Sim')&Q(classificacao='Confirmado')&~Q(evolucao='Óbito')&~Q(evolucao='Recuperado')&Q(bairro=bairro)).values('data_notificacao').annotate(quantidade_casos=Count('data_notificacao')).order_by('data_notificacao'))
        elif informacao == 'Internado':
            if keyBusca == 'estados':
                response = list(Notification.objects.filter(Q(internado='Sim')&Q(classificacao='Confirmado')&~Q(evolucao='Óbito')&~Q(evolucao='Recuperado')&Q(estado_notificacao=estado)).values('data_notificacao').annotate(quantidade_casos=Count('data_notificacao')).order_by('data_notificacao'))
            elif keyBusca == 'cidades':
                response = list(Notification.objects.filter(Q(internado='Sim')&Q(classificacao='Confirmado')&~Q(evolucao='Óbito')&~Q(evolucao='Recuperado')&Q(municipio=cidade)).values('data_notificacao').annotate(quantidade_casos=Count('data_notificacao')).order_by('data_notificacao'))
            elif keyBusca == 'bairros':
                response = list(Notification.objects.filter(Q(internado='Sim')&Q(classificacao='Confirmado')&~Q(evolucao='Óbito')&~Q(evolucao='Recuperado')&Q(bairro=bairro)).values('data_notificacao').annotate(quantidade_casos=Count('data_notificacao')).order_by('data_notificacao'))

        response = json.dumps(response, indent=4, sort_keys=True, default=str)
        
        return JsonResponse(response, safe=False)
    else:
        return JsonResponse({'error': "deu erro aí"})

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

        context['template']: "'register'"
    
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
            return render(request, 'login.html', {'template': "'login'", 'login_error':'true'})
        else:
            return render(request, 'login.html', {'template': "'login'", 'login_error':'false'})

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

