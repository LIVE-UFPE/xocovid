from .models import Notification, Prediction
import json
import requests
import pandas
import numpy as np
from itertools import islice
from background_task import background
import os
from datetime import datetime, timedelta
# TODO tirar ao jogar na master
# import App.IA.pipeline as pipe

collum_names = [
  'ID',              
  'Data Atualização',
  'Data da notificação',
  'Sexo',
  'Idade',
  'CEP residência',
  'País de residência',
  'Estado de residência',
  'Município',
  'Endereço completo',
  'Data dos primeiros sintomas',
  'Paciente foi hospitalizado?',
  'Data da internação hospitalar',
  'Data da alta hospitalar',
  'Data do isolamento',
  'Paciente foi submetido a ventilação mecânica?',
  'Situação de saúde do paciente no momento da notificação',
  'Foi realizada coleta de amostra do paciente?',
  'Foi para outro local de transmissão?',
  'Outro local de transmissão, descrever (cidade, região, país)',
  'Data da viagem de ida para outro local transmissão',
  'Data da viagem de volta do outro local transmissão',
  'Data da chegada no Brasil',
  'Estado de notificação (UF)',
  'Município de notificação',
  'Coleta de exames',
  'Classificação final',
  'Resultado',
  'INTERNADO',
  'EVOLUÇÃO'
]

parse_dates = [
  'Data Atualização',
  'Data da notificação',
  'Data dos primeiros sintomas',
  'Data da internação hospitalar',
  'Data da alta hospitalar',
  'Data do isolamento',
  'Data da viagem de ida para outro local transmissão',
  'Data da viagem de volta do outro local transmissão',
  'Data da chegada no Brasil'
]

PATH_FILES = os.path.join(os.path.dirname(__file__))+'/IA/'
BASE_NAME = 'base.csv'

APIKEY = 'AIzaSyA9py_5Ave_r37HxH4694TpCHQJC6B63HI'

@background(schedule=None)
def listener():
    print("Executando listener")
    
    try:
        df = pandas.read_csv(
            PATH_FILES+BASE_NAME,
            header = 0,
            names=collum_names,
            parse_dates=parse_dates,
        )

        df = pre_processing(df)

        store_base(df)

        build_IAbase()

        prediction()

        send_prediction_to_db()
    except FileNotFoundError:
        print("Nenhuma base de dados para ser pre_processada")

    print("Listener parado")

def send_prediction_to_db():
    df = pandas.read_csv(
        PATH_FILES+'saida3.csv',
        header = 0
    )
    print("Armazenando predicoes")

    data = Notification.objects.order_by('-data_notificacao')[0].data_notificacao + timedelta(days=1)

    predictions = []
    for index, row in df.iterrows():
        predictions.append([row['lat'], row['lng'], row['prediction'], data])

    objs = [
        Prediction(
            latitude=m[0],
            longitude=m[1],
            prediction=m[2],
            data=m[3]
        )
        for m in predictions
    ]
    Prediction.objects.bulk_create(objs=objs)

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
        'Bairro': [],
        'Latitude': [],
        'Longitude': []
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
        data['Bairro'].append(notification.bairro)
        data['Latitude'].append(notification.latitude)
        data['Longitude'].append(notification.longitude)

    df = pandas.DataFrame(data, columns=collum_names)
    df.to_csv(PATH_FILES+'base_preprocessada.csv')
    os.rename(PATH_FILES+BASE_NAME,PATH_FILES+'entrada.csv')

def store_base(df):
    for index, row in df.iterrows():
        try:
            notification = Notification.objects.get(id = int(row['ID']))
        except Notification.DoesNotExist:
            notification = Notification(id = int(row['ID']))
        print("Armazenando notificacao de ID: "+str(row['ID']))
        
        if row['Data Atualização']:
            try:
                df.at[index,'Data Atualização'] = datetime.datetime.strptime(row['Data Atualização'].split(' ')[0],'%Y-%m-%d')
            except ValueError:
                df.at[index,'Data Atualização'] = datetime.datetime.strptime(row['Data Atualização'].split(' ')[0],'%m/%d/%y')
        notification.data_notificacao = row['Data da notificação']
        notification.sexo = str(row['Sexo']).title()
        if pandas.notnull(row['Idade']):
            notification.idade = int(row['Idade'])
        notification.cep = str(row['CEP residência'])
        notification.pais_residencia = str(row['País de residência']).title()
        notification.estado_residencia = str(row['Estado de residência']).title()
        notification.municipio = str(row['Município']).title()
        notification.endereco = str(row['Endereço completo']).title()
        if row['Data dos primeiros sintomas']:
            try:
                notification.data_primeiros_sintomas = datetime.datetime.strptime(row['Data dos primeiros sintomas'].split(' ')[0],'%m/%d/%Y')
            except ValueError:
                try:
                    notification.data_primeiros_sintomas = datetime.datetime.strptime(row['Data dos primeiros sintomas'].split(' ')[0],'%m/%d/%y')
                except ValueError:
                    notification.data_primeiros_sintomas = None
        notification.paciente_hospitalizado = str(row['Paciente foi hospitalizado?']).title()
        notification.data_internacao = row['Data da internação hospitalar']
        notification.data_alta = row['Data da alta hospitalar']
        notification.data_isolamento = row['Data do isolamento']
        notification.ventilacao_mecanica = str(row['Paciente foi submetido a ventilação mecânica?']).title()
        notification.situacao_notificacao = str(row['Situação de saúde do paciente no momento da notificação']).title()
        notification.coleta_amostra = str(row['Foi realizada coleta de amostra do paciente?']).title()
        notification.foi_outro_local_transmissao = str(row['Foi para outro local de transmissão?']).title()
        notification.outro_local_transmissao = str(row['Outro local de transmissão, descrever (cidade, região, país)']).title()
        notification.data_ida_outro_local_transmissao = row['Data da viagem de ida para outro local transmissão']
        notification.data_volta_outro_local_transmissao = row['Data da viagem de volta do outro local transmissão']
        if row['Data da chegada no Brasil']:
            try:
                notification.data_chegada_brasil = datetime.datetime.strptime(row['Data da chegada no Brasil'].split(' ')[0],'%d/%m/%Y')
            except ValueError:
                try:
                    notification.data_chegada_brasil = datetime.datetime.strptime(row['Data da chegada no Brasil'].split(' ')[0],'%d/%m/%y')
                except ValueError:
                    notification.data_chegada_brasil = None
        notification.estado_notificacao = str(row['Estado de notificação (UF)']).title()
        notification.municipio_notificacao = str(row['Município de notificação']).title()
        notification.coleta_exames = str(row['Coleta de exames']).title()
        notification.classificacao = str(row['Classificação final']).title()
        notification.resultado = str(row['Resultado']).title()
        notification.internado = str(row['INTERNADO']).title()
        notification.evolucao = str(row['EVOLUÇÃO']).title()
        notification.bairro = str(row['Bairro']).title()
        notification.latitude = row['Latitude']
        notification.longitude = row['Longitude']
        notification.save()

def pre_processing(df):
    df["Bairro"] = None
    df["Latitude"] = None
    df["Longitude"] = None

    df = df.replace({np.nan: None})

    for index, row in df.iterrows():
        address = str(row['Endereço completo'])+' '+str(row['Município'])+' '+str(row['Estado de residência'])+' '+str(row['País de residência'])
        addressJSON = requestData(request=address, type='google')
        if pandas.notnull(addressJSON):
            print("Pre processando notificacao de ID: "+str(row['ID']))

            country, state, city, neighborhood, cep, latitude, longitude = getDatas(json=addressJSON['results'])

            if pandas.notnull(country):
                df.at[index,'País de residência'] = country
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
        if (pandas.isnull(row['Município']) or pandas.isnull(row['Estado de residência']) or pandas.isnull(row['País de residência']) or pandas.isnull(row['Latitude']) or pandas.isnull(row['Bairro'])) and pandas.notnull(row['CEP residência']):
            print("Pre processando notificacao de ID: "+str(row['ID']))

            CEP = str(row['CEP residência'])+' '+str(row['Município'])+' '+str(row['Estado de residência'])+' '+str(row['País de residência'])
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
                if pandas.notnull(country):
                    df.at[index,'País de residência'] = country
                if pandas.notnull(state):
                    df.at[index,'Estado de residência'] = state
                if pandas.notnull(city):
                    df.at[index,'Município'] = city
            else:
                print('Erro na busca do google maps')

    for index, row in df.iterrows():
        if pandas.notnull(row['Sexo']):
            df.at[index,'Sexo'] = str(row['Sexo']).title()
        if pandas.notnull(row['País de residência']):
            df.at[index,'País de residência'] = str(row['País de residência']).title()
        if pandas.notnull(row['Estado de residência']):
            df.at[index,'Estado de residência'] = str(row['Estado de residência']).title()
        if pandas.notnull(row['Município']):
            df.at[index,'Município'] = str(row['Município']).title()
        if pandas.notnull(row['Endereço completo']):
            df.at[index,'Endereço completo'] = str(row['Endereço completo']).title()
        if pandas.notnull(row['Paciente foi hospitalizado?']):
            df.at[index,'Paciente foi hospitalizado?'] = str(row['Paciente foi hospitalizado?']).title()
        if pandas.notnull(row['Paciente foi submetido a ventilação mecânica?']):
            df.at[index,'Paciente foi submetido a ventilação mecânica?'] = str(row['Paciente foi submetido a ventilação mecânica?']).title()    
        if pandas.notnull(row['Situação de saúde do paciente no momento da notificação']):
            df.at[index,'Situação de saúde do paciente no momento da notificação'] = str(row['Situação de saúde do paciente no momento da notificação']).title()
        if pandas.notnull(row['Foi realizada coleta de amostra do paciente?']):
            df.at[index,'Foi realizada coleta de amostra do paciente?'] = str(row['Foi realizada coleta de amostra do paciente?']).title()    
        if pandas.notnull(row['Foi para outro local de transmissão?']):
            df.at[index,'Foi para outro local de transmissão?'] = str(row['Foi para outro local de transmissão?']).title()    
        if pandas.notnull(row['Outro local de transmissão, descrever (cidade, região, país)']):
            df.at[index,'Outro local de transmissão, descrever (cidade, região, país)'] = str(row['Outro local de transmissão, descrever (cidade, região, país)']).title()
        if pandas.notnull(row['Estado de notificação (UF)']):
            df.at[index,'Estado de notificação (UF)'] = str(row['Estado de notificação (UF)']).title()
        if pandas.notnull(row['Município de notificação']):
            df.at[index,'Município de notificação'] = str(row['Município de notificação']).title()
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

    return df

def requestData(request=None, type='google'):
	if type=='google':
		url_api = ('https://maps.googleapis.com/maps/api/geocode/json?address='+request+'&key='+APIKEY+'&language=pt&region=BR')
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
