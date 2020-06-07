from .models import Notification, PredictionBR, InterpolationBR, PredictionPE, InterpolationPE, CasosEstado, CasosCidade, CasosEstadoHistorico, Projecao, CasosPernambuco
import json
import requests
import pandas
import numpy as np
from itertools import islice
from background_task import background
import os
from datetime import datetime, timedelta
# DEBUG comente para pegar no windows
import App.IA.pipeline as pipe
from django.utils import timezone
import App.bot.stateCityData as bot
import App.predicao_arima.stateCityData as stateCityData
import App.predicao_arima.pipelineArima as pipelineArima
from distutils.dir_util import copy_tree
from urllib.request import urlopen
from bs4 import BeautifulSoup

collum_names = [
  'ID',      
  'Data Atualização',
  'Data da notificação',
  'Sexo',
  'Idade',
  'CEP residência',
  #'País de residência',
  'Estado de residência',
  'Município',
  'Endereço completo',
  'Data dos primeiros sintomas',
  'Paciente foi hospitalizado?',
  #'Data da internação hospitalar',
  #'Data da alta hospitalar',
  #'Data do isolamento',
  #'Paciente foi submetido a ventilação mecânica?',
  #'Situação de saúde do paciente no momento da notificação',
  #'Foi realizada coleta de amostra do paciente?',
  #'Foi para outro local de transmissão?',
  #'Outro local de transmissão, descrever (cidade, região, país)',
  #'Data da viagem de ida para outro local transmissão',
  #'Data da viagem de volta do outro local transmissão',
  #'Data da chegada no Brasil',
  #'Estado de notificação (UF)',
  #'Município de notificação',
  'Coleta de exames',
  'Classificação final',
  'Resultado',
  'INTERNADO',
  'EVOLUÇÃO',
  #MODIFICACAO
  #'Bairro',
  #'Latitude',
  #'Longitude'
]

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

PATH_FILES = os.path.join(os.path.dirname(__file__))+'/IA/'
BASE_NAME = 'base_original.csv'
#BASE_NAME = 'base_preprocessada.csv'

APIKEY = 'AIzaSyA9py_5Ave_r37HxH4694TpCHQJC6B63HI'

@background(schedule=None)
def listener():
    print("Executando listener")
    
    print("Extraindo informações de outras bases")
    bot.processingData()
    storeBot()
    
    print("Executando predicoes do Arima")
    stateCityData.main()
    pipelineArima.main()
    saveImages()
    storeProjections()

    getCasosPernambuco()

    prediction()
    store_base()
    send_prediction_to_db()
    
    print("Listener parado")

def getCasosPernambuco():
    print("Extraindo casos de Pernambuco")
    content = urlopen("https://dados.seplag.pe.gov.br/apps/corona_dados.html")
    res = BeautifulSoup(content.read(), "html.parser")
    tags = res.findAll("script")

    casos = str(tags[21])
    inicio = casos.index('{')
    casos = casos[inicio:]
    casos = casos.replace("</script>", "")

    casos_dict = json.loads(casos)

    casos_data = pandas.DataFrame()

    cols = ['dt_referencia', 'dt_atualizacao','confirmados','obitos','tx_obitos','recuperados', 
    'tx_recuperados','isolamento','tx_isolamento','enfermaria','tx_enfermaria','uti','tx_uti',
    'testes_novos','testes_acumulados','tx_testes','leitos_uti','tx_oc_uti','leitos_enf','tc_oc_enf']


    data = casos_dict["x"]["data"]


    for i, coluna in enumerate(data):
        casos_data[cols[i]] = coluna

    print('Armazenando casos')
    
    CasosPernambuco.objects.all().delete()
    casoPernambuco = CasosPernambuco(
        data_atualizacao = casos_data.iloc[0]['dt_atualizacao'], 
        obitos = casos_data.iloc[0]['obitos'], 
        recuperados = casos_data.iloc[0]['recuperados'], 
        isolamento = casos_data.iloc[0]['isolamento'],
        internados = casos_data.iloc[0]['enfermaria']+casos_data.iloc[-1]['uti'])
    casoPernambuco.save()

def storeProjections():
    print("Armazenando projecoes")

    last_date = datetime(1990, 1, 1)
    for fileName in os.listdir(os.path.join(os.path.dirname(__file__))+'/predicao_arima/SaidaArima'):
        try:
            if(datetime.strptime(fileName, '%Y-%m-%d') > last_date):
                last_date = datetime.strptime(fileName, '%Y-%m-%d')
        except:
            pass

    pasta = os.path.join(os.path.dirname(__file__))+'/predicao_arima/SaidaArima/'+str(last_date).split(' ')[0]+'/'
    Projecao.objects.all().delete()
    for fileName in os.listdir(pasta):
        if fileName.find('.png') == -1:
            a = pandas.read_csv(pasta+fileName, sep=',')
            a = a.replace({np.nan: None})

            fileEstadoNome = fileName.split('projecao')[1].split('.csv')[0].split(str(last_date).split(' ')[0])[0]
            
            if  fileEstadoNome != 'BrasilConfirmados' and fileEstadoNome != 'BrasilMortes':
                nomeEstado = stateName[fileName.split('projecao')[1].split('.csv')[0].split(str(last_date).split(' ')[0])[0]]
            elif fileEstadoNome == 'BrasilConfirmados':
                nomeEstado = 'Projecao de Confirmados no Brasil'
            else:
                nomeEstado = 'Projecao de Óbitos no Brasil'

            print('Armazenando projecoes de ' + nomeEstado)
                
            projections = []
            for index, row in a.iterrows():
                data_notificacao = buildDate(row['dt_notificacao'])

                if pandas.notnull(row['acumulado_confirmados']):
                    quantidade_casos = round(row['acumulado_confirmados'])
                else:
                    quantidade_casos = None

                if pandas.notnull(row['Lo.80']):
                    lo80 = round(row['Lo.80'])
                else:
                    lo80 = None
                
                if pandas.notnull(row['Hi.80']):
                    hi80 = round(row['Hi.80'])
                else:
                    hi80 = None

                if pandas.notnull(row['Lo.95']):
                    lo95 = round(row['Lo.95'])
                else:
                    lo95 = None
                
                if pandas.notnull(row['Hi.95']):
                    hi95 = round(row['Hi.95'])
                else:
                    hi95 = None
                
                projecao = Projecao(data_notificacao=data_notificacao, quantidade_casos=quantidade_casos, lo80=lo80, hi80=hi80, lo95=lo95, hi95=hi95, estado_residencia=nomeEstado)

                projecao.save()

def saveImages():
    print("Salvando Imagens no database")

    original = os.path.join(os.path.dirname(__file__))+"/predicao_arima/grafico modelo"
    target = os.path.join(os.path.dirname(__file__))+"/static/graficos/modelos"
    copy_tree(original, target)
    

    original = os.path.join(os.path.dirname(__file__))+"/predicao_arima/grafico predicao"
    target = os.path.join(os.path.dirname(__file__))+"/static/graficos/predicoes"
    copy_tree(original, target)

    last_date = datetime(1990, 1, 1)
    for fileName in os.listdir(os.path.join(os.path.dirname(__file__))+'/predicao_arima/SaidaArima'):
        try:
            if(datetime.strptime(fileName, '%Y-%m-%d') > last_date):
                last_date = datetime.strptime(fileName, '%Y-%m-%d')
        except:
            pass
    
    original = os.path.join(os.path.dirname(__file__))+"/predicao_arima/SaidaArima/"+str(last_date).split(' ')[0]
    target = os.path.join(os.path.dirname(__file__))+"/static/graficos/projecoes"
    copy_tree(original, target)

def storeBot():
    print("Armazenando extrações")

    dfEstados = pandas.read_csv(os.path.join(os.path.dirname(__file__))+'/bot/Ultimos Casos por Estado.csv', sep=',')
    dfEstadosHistorico = pandas.read_csv(os.path.join(os.path.dirname(__file__))+'/bot/Casos por Estado.csv', sep=',')
    dfCidades = pandas.read_csv(os.path.join(os.path.dirname(__file__))+'/bot/Ultimos Casos por cidade.csv', sep=',')

    estados = []
    for index, row in dfEstados.iterrows():
            estados.append([row['date'], row['state'], row['confirmed'], row['deaths'], row['estimated_population_2019'], row['confirmed_per_100k_inhabitants']])

    estadosHistorico = []
    for index, row in dfEstadosHistorico.iterrows():
            estadosHistorico.append([row['date'], stateName[row['state']], row['confirmed'], row['deaths'], row['estimated_population_2019'], row['confirmed_per_100k_inhabitants']])

    cidades = []
    for index, row in dfCidades.iterrows():
        if pandas.notnull(row['estimated_population_2019']):
            cidades.append([row['date'], stateName[row['state']], row['city'], row['confirmed'], row['deaths'], row['estimated_population_2019'], row['confirmed_per_100k_inhabitants']])

    CasosEstado.objects.all().delete()
    CasosEstadoHistorico.objects.all().delete()
    CasosCidade.objects.all().delete()

    objs = [
        CasosEstado(
            data_atualizacao=m[0],
            estado=m[1],
            confirmados=m[2],
            obitos=m[3],
            populacao_estimada_2019 = m[4],
            confirmados_100k = m[5],
        )
        for m in estados
    ]
    CasosEstado.objects.bulk_create(objs=objs)

    objs = [
        CasosEstadoHistorico(
            data_notificacao=m[0],
            estado_residencia=m[1],
            quantidade_casos=m[2],
            obitos=m[3],
            populacao_estimada_2019 = m[4],
            confirmados_100k = m[5],
        )
        for m in estadosHistorico
    ]
    CasosEstadoHistorico.objects.bulk_create(objs=objs)

    objs = [
        CasosCidade(
            data_notificacao=m[0],
            estado_residencia=m[1],
            municipio = m[2],
            quantidade_casos=m[3],
            obitos=m[4],
            populacao_estimada_2019 = m[5],
            confirmados_100k = m[6],
        )
        for m in cidades
    ]
    CasosCidade.objects.bulk_create(objs=objs)

def send_prediction_to_db():
    PredictionBR.objects.all().delete()

    df = pandas.read_csv(
        PATH_FILES+'saidaFinalBR.csv',
        header = 0
    )
    print("Armazenando predicoes do BR")

    #maxPredction = df['prediction'].max()

    predictions = []
    for index, row in df.iterrows():
        predictions.append([index, row['latitude'], row['longitude'], row['prediction_day1'], row['prediction_day2'], row['prediction_day3']])

    objs = [
        PredictionBR(
            id=m[0],
            latitude=m[1],
            longitude=m[2],
            prediction1=m[3],
            prediction2=m[4],
            prediction3=m[5],
        )
        for m in predictions
    ]
    PredictionBR.objects.bulk_create(objs=objs)


    PredictionPE.objects.all().delete()

    df = pandas.read_csv(
        PATH_FILES+'saidaFinalPE.csv',
        header = 0
    )
    print("Armazenando predicoes do PE")

    #maxPredction = df['prediction'].max()

    predictions = []
    for index, row in df.iterrows():
        predictions.append([index, row['latitude'], row['longitude'], row['prediction_day1'], row['prediction_day2'], row['prediction_day3']])

    objs = [
        PredictionPE(
            id=m[0],
            latitude=m[1],
            longitude=m[2],
            prediction1=m[3],
            prediction2=m[4],
            prediction3=m[5],
        )
        for m in predictions
    ]
    PredictionPE.objects.bulk_create(objs=objs)

def prediction():
    print('Chamando IA')
    pipe.main()

def build_IAbase():
    data = {
        'ID': [],
        'Data Atualização': [],
        'Data da notificação': [],
        'Sexo': [],
        'Idade': [],
        'CEP residência': [],
        'País de residência': [],
        'Estado de residência': [],
        'Município': [],
        'Endereço completo': [],
        'Data dos primeiros sintomas': [],
        'Paciente foi hospitalizado?': [],
        'Data da internação hospitalar': [],
        'Data da alta hospitalar': [],
        'Data do isolamento': [],
        'Paciente foi submetido a ventilação mecânica?': [],
        'Situação de saúde do paciente no momento da notificação': [],
        'Foi realizada coleta de amostra do paciente?': [],
        'Foi para outro local de transmissão?': [],
        'Outro local de transmissão, descrever (cidade, região, país)': [],
        'Data da viagem de ida para outro local transmissão': [],
        'Data da viagem de volta do outro local transmissão': [],
        'Data da chegada no Brasil': [],
        'Estado de notificação (UF)': [],
        'Município de notificação': [],
        'Coleta de exames': [],
        'Classificação final': [],
        'Resultado': [],
        'INTERNADO': [],
        'EVOLUÇÃO': [],
    }

    print("Desenvolvendo base da IA")
    notifications = list(Notification.objects.all())
    for notification in notifications:
        data['ID'].append(notification.id)
        if notification.data_atualizacao:
            data['Data Atualização'].append(notification.data_atualizacao.isoformat())
        else:
            data['Data Atualização'].append(notification.data_atualizacao)
        if notification.data_notificacao:
            data['Data da notificação'].append(notification.data_notificacao.isoformat())
        else:
            data['Data da notificação'].append(notification.data_notificacao)
        data['Sexo'].append(notification.sexo)
        data['Idade'].append(notification.idade)
        data['CEP residência'].append(notification.cep)
        data['País de residência'].append(notification.pais_residencia)
        data['Estado de residência'].append(notification.estado_residencia)
        data['Município'].append(notification.municipio)
        data['Endereço completo'].append(notification.endereco)
        if notification.data_primeiros_sintomas:
            data['Data dos primeiros sintomas'].append(notification.data_primeiros_sintomas.isoformat())
        else:
            data['Data dos primeiros sintomas'].append(notification.data_primeiros_sintomas)
        data['Paciente foi hospitalizado?'].append(notification.paciente_hospitalizado)
        if notification.data_internacao:
            data['Data da internação hospitalar'].append(notification.data_internacao.isoformat())
        else:
            data['Data da internação hospitalar'].append(notification.data_internacao)
        if notification.data_alta:
            data['Data da alta hospitalar'].append(notification.data_alta.isoformat())
        else:
            data['Data da alta hospitalar'].append(notification.data_alta)
        if notification.data_isolamento:
            data['Data do isolamento'].append(notification.data_isolamento.isoformat())
        else:
            data['Data do isolamento'].append(notification.data_isolamento)
        data['Paciente foi submetido a ventilação mecânica?'].append(notification.ventilacao_mecanica)
        data['Situação de saúde do paciente no momento da notificação'].append(notification.situacao_notificacao)
        data['Foi realizada coleta de amostra do paciente?'].append(notification.coleta_amostra)
        data['Foi para outro local de transmissão?'].append(notification.foi_outro_local_transmissao)
        data['Outro local de transmissão, descrever (cidade, região, país)'].append(notification.outro_local_transmissao)
        if notification.data_ida_outro_local_transmissao:
            data['Data da viagem de ida para outro local transmissão'].append(notification.data_ida_outro_local_transmissao.isoformat())
        else:
            data['Data da viagem de ida para outro local transmissão'].append(notification.data_ida_outro_local_transmissao)
        if notification.data_volta_outro_local_transmissao:
            data['Data da viagem de volta do outro local transmissão'].append(notification.data_volta_outro_local_transmissao.isoformat())
        else:
            data['Data da viagem de volta do outro local transmissão'].append(notification.data_volta_outro_local_transmissao)
        if notification.data_chegada_brasil:
            data['Data da chegada no Brasil'].append(notification.data_chegada_brasil.isoformat())
        else:
            data['Data da chegada no Brasil'].append(notification.data_chegada_brasil)
        data['Estado de notificação (UF)'].append(notification.estado_notificacao)
        data['Município de notificação'].append(notification.municipio_notificacao)
        data['Coleta de exames'].append(notification.coleta_exames)
        data['Classificação final'].append(notification.classificacao)
        data['Resultado'].append(notification.resultado)
        data['INTERNADO'].append(notification.internado)
        data['EVOLUÇÃO'].append(notification.evolucao)

    df = pandas.DataFrame(data)
    df.to_csv(PATH_FILES+'entradaPreProcessada.csv')
    os.rename(PATH_FILES+BASE_NAME,PATH_FILES+'ok '+str(timezone.now().date())+' '+BASE_NAME)

def store_base():
    pasta = PATH_FILES+'bases predicao BR/'

    InterpolationBR.objects.all().delete()

    for fileName in os.listdir(pasta):
        a = pandas.read_csv(pasta+fileName, sep=',')

        interporlations = []
        date = datetime.strptime(fileName.split('predicao_covid19BR_')[1].split('.csv')[0]+'-20', '%m-%d-%y')
        print('Armazenando Interpolacoes do BR do dia ' + str(date))
        for index, row in a.iterrows():
            interporlations.append([row['latitude'], row['longitude'], row['prediction'], date])
        
        objs = [
            InterpolationBR(
                latitude=m[0],
                longitude=m[1],
                prediction=m[2],
                date=m[3],
            )
            for m in interporlations
        ]
        InterpolationBR.objects.bulk_create(objs=objs)


    pasta = PATH_FILES+'bases predicao PE/'

    InterpolationPE.objects.all().delete()

    for fileName in os.listdir(pasta):
        a = pandas.read_csv(pasta+fileName, sep=',')

        interporlations = []
        date = datetime.strptime(fileName.split('predicao_covid19PE_')[1].split('.csv')[0]+'-20', '%m-%d-%y')
        print('Armazenando Interpolacoes de PE do dia ' + str(date))
        for index, row in a.iterrows():
            interporlations.append([row['latitude'], row['longitude'], row['prediction'], date])
        
        objs = [
            InterpolationPE(
                latitude=m[0],
                longitude=m[1],
                prediction=m[2],
                date=m[3],
            )
            for m in interporlations
        ]
        InterpolationPE.objects.bulk_create(objs=objs)

    """df = df.replace({np.nan: None})
    for index, row in df.iterrows():
        try:
            notification = Notification.objects.get(id = int(row['ID']))
        except Notification.DoesNotExist:
            notification = Notification(id = int(row['ID']))
        print("Armazenando notificacao de ID: "+str(row['ID']))
        
        notification.data_atualizacao = buildDate(row['Data AtualizaÃ§Ã£o'])
        notification.data_notificacao = buildDate(row['Data da notificaÃ§Ã£o'])
        notification.sexo = str(row['Sexo']).title()
        if pandas.notnull(row['Idade']):
            try:
                notification.idade = int(row['Idade'])
            except:
                notification.idade = 0
        notification.cep = str(row['CEP residÃªncia'])
        #notification.pais_residencia = str(row['PaÃ­s de residÃªncia']).title()
        notification.estado_residencia = str(row['Estado de residÃªncia']).title()
        notification.municipio = str(row['MunicÃ­pio']).title()
        notification.endereco = str(row['EndereÃ§o completo']).title()
        notification.data_primeiros_sintomas = buildDate(row['Data dos primeiros sintomas'])
        notification.paciente_hospitalizado = str(row['Paciente foi hospitalizado?']).title()
        #notification.data_internacao = row['Data da internaÃ§Ã£o hospitalar']
        #notification.data_alta = row['Data da alta hospitalar']
        #notification.data_isolamento = row['Data do isolamento']
        #notification.ventilacao_mecanica = str(row['Paciente foi submetido a ventilaÃ§Ã£o mecÃ¢nica?']).title()
        #notification.situacao_notificacao = str(row['SituaÃ§Ã£o de saÃºde do paciente no momento da notificaÃ§Ã£o']).title()
        #notification.coleta_amostra = str(row['Foi realizada coleta de amostra do paciente?']).title()
        #notification.foi_outro_local_transmissao = str(row['Foi para outro local de transmissÃ£o?']).title()
        #notification.outro_local_transmissao = str(row['Outro local de transmissÃ£o, descrever (cidade, regiÃ£o, paÃ­s)']).title()
        #notification.data_ida_outro_local_transmissao = row['Data da viagem de ida para outro local transmissÃ£o']
        #notification.data_volta_outro_local_transmissao = row['Data da viagem de volta do outro local transmissÃ£o']
        #if row['Data da chegada no Brasil']:
        #    try:
        #        notification.data_chegada_brasil = datetime.strptime(row['Data da chegada no Brasil'].split(' ')[0],'%d/%m/%Y')
        #    except ValueError:
        #        try:
        #            notification.data_chegada_brasil = datetime.strptime(row['Data da chegada no Brasil'].split(' ')[0],'%d/%m/%y')
        #        except ValueError:
        #            notification.data_chegada_brasil = None
        #notification.estado_notificacao = str(row['Estado de notificaÃ§Ã£o (UF)']).title()
        #notification.municipio_notificacao = str(row['MunicÃ­pio de notificaÃ§Ã£o']).title()
        notification.coleta_exames = str(row['Coleta de exames']).title()
        notification.classificacao = str(row['ClassificaÃ§Ã£o final']).title()
        notification.resultado = str(row['Resultado']).title()
        notification.internado = str(row['INTERNADO']).title()
        notification.evolucao = str(row['EVOLUÃ‡ÃƒO']).title()
        notification.bairro = str(row['Bairro']).title()
        notification.latitude = row['Latitude']
        notification.longitude = row['Longitude']

        if notification.estado_residencia != 'Pernambuco':
            notification.estado_residencia = 'Pernambuco'
            notification.municipio = 'Recife'
            notification.bairro = 'Boa Viagem'

        notification.save()"""

def pre_processing(df):
    df["Bairro"] = None
    df["Latitude"] = None
    df["Longitude"] = None

    df = df.replace({np.nan: None})

    for index, row in df.iterrows():
        address = str(row['Endereço completo'])+' '+str(row['Município'])+' '+str(row['Estado de residência'])+' '+str('Brasil'"""row['País de residência']""")
        addressJSON = requestData(request=address, type='google')
        if pandas.notnull(addressJSON):
            print("Pre processando notificacao de ID: "+str(row['ID']))

            country, state, city, neighborhood, cep, latitude, longitude = getDatas(json=addressJSON['results'])

            #if pandas.notnull(country):
            #    df.at[index,'País de residência'] = country
            if pandas.notnull(state):
                df.at[index,'Estado de residência'] = state
            if pandas.notnull(city):
                df.at[index,'Município'] = city

            df.at[index,'Bairro'] = neighborhood
            df.at[index,'Latitude'] = latitude
            df.at[index,'Longitude'] = longitude

            if pandas.notnull(cep):
                df.at[index,'CEP residência'] = cep
        else:
            print('Erro na busca do google maps')

    for index, row in df.iterrows():
        if (pandas.isnull(row['Município']) or pandas.isnull(row['Estado de residência']) or pandas.isnull('Brasil'"""row['País de residência']""") or pandas.isnull(row['Latitude']) or pandas.isnull(row['Bairro'])) and pandas.notnull(row['CEP residência']):
            print("Pre processando notificacao de ID: "+str(row['ID']))

            CEP = str(row['CEP residência'])+' '+str(row['Município'])+' '+str(row['Estado de residência'])+' '+str('Brasil'"""row['País de residência']""")
            addressJSON = requestData(request=CEP, type='google')
            if pandas.notnull(addressJSON):
                country, state, city, neighborhood, cep, latitude, longitude = getDatas(json=addressJSON['results'])

                if pandas.isnull(row['Bairro']):
                    addressJSON = requestData(request=str(row['CEP residência']), type='cep')
                    neighborhood = addressJSON['bairro']
                    df.at[index,'Bairro'] = neighborhood

                if pandas.isnull(row['Latitude']):
                    df.at[index,'Latitude'] = latitude
                    df.at[index,'Longitude'] = longitude
                #if pandas.notnull(country):
                #    df.at[index,'País de residência'] = country
                if pandas.notnull(state):
                    df.at[index,'Estado de residência'] = state
                if pandas.notnull(city):
                    df.at[index,'Município'] = city
            else:
                print('Erro na busca do google maps')

    for index, row in df.iterrows():
        if pandas.notnull(row['Sexo']):
            df.at[index,'Sexo'] = str(row['Sexo']).title()
        #if pandas.notnull(row['País de residência']):
        #    df.at[index,'País de residência'] = str(row['País de residência']).title()
        if pandas.notnull(row['Estado de residência']):
            df.at[index,'Estado de residência'] = str(row['Estado de residência']).title()
        if pandas.notnull(row['Município']):
            df.at[index,'Município'] = str(row['Município']).title()
        if pandas.notnull(row['Endereço completo']):
            df.at[index,'Endereço completo'] = str(row['Endereço completo']).title()
        if pandas.notnull(row['Paciente foi hospitalizado?']):
            df.at[index,'Paciente foi hospitalizado?'] = str(row['Paciente foi hospitalizado?']).title()
        #if pandas.notnull(row['Paciente foi submetido a ventilação mecânica?']):
        #    df.at[index,'Paciente foi submetido a ventilação mecânica?'] = str(row['Paciente foi submetido a ventilação mecânica?']).title()    
        #if pandas.notnull(row['Situação de saúde do paciente no momento da notificação']):
        #    df.at[index,'Situação de saúde do paciente no momento da notificação'] = str(row['Situação de saúde do paciente no momento da notificação']).title()
        #if pandas.notnull(row['Foi realizada coleta de amostra do paciente?']):
        #    df.at[index,'Foi realizada coleta de amostra do paciente?'] = str(row['Foi realizada coleta de amostra do paciente?']).title()    
        #if pandas.notnull(row['Foi para outro local de transmissão?']):
        #    df.at[index,'Foi para outro local de transmissão?'] = str(row['Foi para outro local de transmissão?']).title()    
        #if pandas.notnull(row['Outro local de transmissão, descrever (cidade, região, país)']):
        #    df.at[index,'Outro local de transmissão, descrever (cidade, região, país)'] = str(row['Outro local de transmissão, descrever (cidade, região, país)']).title()
        #if pandas.notnull(row['Estado de notificação (UF)']):
        #    df.at[index,'Estado de notificação (UF)'] = str(row['Estado de notificação (UF)']).title()
        #if pandas.notnull(row['Município de notificação']):
        #    df.at[index,'Município de notificação'] = str(row['Município de notificação']).title()
        if pandas.notnull(row['Coleta de exames']):
            df.at[index,'Coleta de exames'] = str(row['Coleta de exames']).title()
        if pandas.notnull(row['Classificação final']):
            df.at[index,'Classificação final'] = str(row['Classificação final']).title()
        if pandas.notnull(row['Resultado']):
            df.at[index,'Resultado'] = str(row['Resultado']).title()
        if pandas.notnull(row['INTERNADO']):
            df.at[index,'INTERNADO'] = str(row['INTERNADO']).title()
        if pandas.notnull(row['EVOLUÇÃO']):
            df.at[index,'EVOLUÇÃO'] = str(row['EVOLUÇÃO']).title()
        if pandas.notnull(row['Bairro']):
            df.at[index,'Bairro'] = str(row['Bairro']).title()
    
    df = df.replace({np.nan: None})

    df.to_csv(PATH_FILES+'base_preprocessada.csv')

    return df

def requestData(request=None, type='google'):
    if type=='google':
        url_api = ('https://maps.googleapis.com/maps/api/geocode/json?address='+request+'&key='+APIKEY+'&language=pt&region=BR')
    elif type=='cep':
        url_api = ('http://cep.republicavirtual.com.br/web_cep.php?cep='+request+'&formato=json')

    try:
        req = requests.get(url_api)

        if req.status_code == 200:
            dados_json = json.loads(req.text)
            return dados_json
        else:
            return None
    except:
        return None

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

def buildDate(original_date):
    dateBuilded = False
    result_date = None

    if original_date:
        try:
            result_date = datetime.strptime(str(original_date).split(' ')[0],'%m/%d/%Y')
            dateBuilded = True
        except ValueError:
            pass

        if dateBuilded == False:
            try:
                result_date = datetime.strptime(str(original_date).split(' ')[0],'%m/%d/%y')
                dateBuilded = True
            except ValueError:
                pass
        
        if dateBuilded == False:
            try:
                result_date = datetime.strptime(str(original_date).split(' ')[0],'%d/%m/%Y')
                dateBuilded = True
            except ValueError:
                pass
        
        if dateBuilded == False:
            try:
                result_date = datetime.strptime(str(original_date).split(' ')[0],'%d/%m/%y')
                dateBuilded = True
            except ValueError:
                pass
        
        if dateBuilded == False:
            try:
                result_date = datetime.strptime(str(original_date).split(' ')[0],'%y/%d/%m')
                dateBuilded = True
            except ValueError:
                pass
        
        if dateBuilded == False:
            try:
                result_date = datetime.strptime(str(original_date).split(' ')[0],'%Y/%d/%m')
                dateBuilded = True
            except ValueError:
                pass
        
        if dateBuilded == False:
            try:
                result_date = datetime.strptime(str(original_date).split(' ')[0],'%y/%m/%d')
                dateBuilded = True
            except ValueError:
                pass

        if dateBuilded == False:
            try:
                result_date = datetime.strptime(str(original_date).split(' ')[0],'%Y/%m/%d')
                dateBuilded = True
            except ValueError:
                pass

        if dateBuilded == False:
            try:
                result_date = datetime.strptime(str(original_date).split(' ')[0],'%m-%d-%Y')
                dateBuilded = True
            except ValueError:
                pass

        if dateBuilded == False:
            try:
                result_date = datetime.strptime(str(original_date).split(' ')[0],'%m-%d-%y')
                dateBuilded = True
            except ValueError:
                pass
        
        if dateBuilded == False:
            try:
                result_date = datetime.strptime(str(original_date).split(' ')[0],'%d-%m-%Y')
                dateBuilded = True
            except ValueError:
                pass
        
        if dateBuilded == False:
            try:
                result_date = datetime.strptime(str(original_date).split(' ')[0],'%d-%m-%y')
                dateBuilded = True
            except ValueError:
                pass
        
        if dateBuilded == False:
            try:
                result_date = datetime.strptime(str(original_date).split(' ')[0],'%y-%d-%m')
                dateBuilded = True
            except ValueError:
                pass
        
        if dateBuilded == False:
            try:
                result_date = datetime.strptime(str(original_date).split(' ')[0],'%Y-%d-%m')
                dateBuilded = True
            except ValueError:
                pass
        
        if dateBuilded == False:
            try:
                result_date = datetime.strptime(str(original_date).split(' ')[0],'%y-%m-%d')
                dateBuilded = True
            except ValueError:
                pass

        if dateBuilded == False:
            try:
                result_date = datetime.strptime(str(original_date).split(' ')[0],'%Y-%m-%d')
                dateBuilded = True
            except ValueError:
                pass

        if dateBuilded == False:
            try:
                result_date = datetime.strptime(str(original_date).split(' ')[0]+'/2020','%d/%m/%Y')
                dateBuilded = True
            except ValueError:
                pass
    
    return result_date
