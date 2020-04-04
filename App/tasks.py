from .models import Listener, Notification
import json
import requests
import pandas
import numpy as np
from itertools import islice
from background_task import background
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import datetime

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

PATH_FILES = 'C:/Users/Gabriel Marques/Desktop/'
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
        
        df["Bairro"] = None
        df["Latitude"] = None
        df["Longitude"] = None

        df = df.replace({np.nan: None})
        
        for index, row in df.iterrows():
            if row['Data Atualização']:
                try:
                    df.at[index,'Data Atualização'] = datetime.datetime.strptime(row['Data Atualização'].split(' ')[0],'%Y-%m-%d')
                except ValueError:
                    df.at[index,'Data Atualização'] = datetime.datetime.strptime(row['Data Atualização'].split(' ')[0],'%m/%d/%y')

        for index, row in df.iterrows():
            try:
                notification = Notification.objects.get(id = int(row['ID']))
            except Notification.DoesNotExist:
                notification = Notification(id = int(row['ID']))
            print("Armazenando notificacao de ID: "+str(row['ID']))
            
            notification.data_atualizacao = row['Data Atualização']
            notification.data_notificacao = row['Data da notificação']
            notification.sexo = str(row['Sexo']).title()
            if row['Idade']:
                notification.idade = int(row['Idade'])
            notification.cep = str(row['CEP residência'])
            notification.pais_residencia = str(row['País de residência']).title()
            notification.estado_residencia = str(row['Estado de residência']).title()
            notification.municipio = str(row['Município']).title()
            notification.endereco = str(row['Endereço completo']).title()
            notification.paciente_hospitalizado = str(row['Paciente foi hospitalizado?']).title()
            notification.data_internacao = row['Data da internação hospitalar']
            notification.data_alta = row['Data da alta hospitalar']
            notification.ventilacao_mecanica = str(row['Paciente foi submetido a ventilação mecânica?']).title()
            notification.situacao_notificacao = str(row['Situação de saúde do paciente no momento da notificação']).title()
            notification.coleta_amostra = str(row['Foi realizada coleta de amostra do paciente?']).title()
            notification.coleta_exames = str(row['Coleta de exames']).title()
            notification.classificacao = str(row['Classificação final']).title()
            notification.resultado = str(row['Resultado']).title()
            notification.internado = str(row['INTERNADO']).title()
            notification.evolucao = str(row['EVOLUÇÃO']).title()
            notification.bairro = str(row['Bairro']).title()
            notification.latitude = row['Latitude']
            notification.longitude = row['Longitude']
            notification.save()

        for index, row in df.iterrows():
            address = str(row['Endereço completo'])+' '+str(row['Município'])+' '+str(row['Estado de residência'])+' '+str(row['País de residência'])
            addressJSON = requestData(request=address, type='google')
            if pandas.notnull(addressJSON):
                notification = Notification.objects.get(id = int(row['ID']))
                print("Pre processando notificacao de ID: "+str(row['ID']))

                country, state, city, neighborhood, cep, latitude, longitude = getDatas(json=addressJSON['results'])

                if pandas.notnull(country):
                    df.at[index,'País de residência'] = country
                    notification.pais_residencia = country
                if pandas.notnull(state):
                    df.at[index,'Estado de residência'] = state
                    notification.estado_residencia = state
                if pandas.notnull(city):
                    df.at[index,'Município'] = city
                    notification.pais_municipio = city

                df.at[index,'Bairro'] = neighborhood
                notification.bairro = neighborhood
                df.at[index,'Latitude'] = latitude
                notification.latitude = latitude
                df.at[index,'Longitude'] = longitude
                notification.longitude = longitude

                if pandas.notnull(cep):
                    df.at[index,'CEP residência'] = cep
                    notification.cep = cep
            else:
                print('Erro na busca do google maps')
            notification.save() 

        for index, row in df.iterrows():
            if (pandas.isnull(row['Município']) or pandas.isnull(row['Estado de residência']) or pandas.isnull(row['País de residência']) or pandas.isnull(row['Latitude']) or pandas.isnull(row['Bairro'])) and pandas.notnull(row['CEP residência']):
                notification = Notification.objects.get(id = int(row['ID']))
                print("Pre processando notificacao de ID: "+str(row['ID']))

                CEP = str(row['CEP residência'])+' '+str(row['Município'])+' '+str(row['Estado de residência'])+' '+str(row['País de residência'])
                addressJSON = requestData(request=CEP, type='google')
                if pandas.notnull(addressJSON):
                    country, state, city, neighborhood, cep, latitude, longitude = getDatas(json=addressJSON['results'])

                    if pandas.isnull(row['Bairro']):
                        addressJSON = requestData(request=str(row['CEP residência']), type='cep')
                        neighborhood = addressJSON['bairro']
                        df.at[index,'Bairro'] = neighborhood
                        notification.bairro = neighborhood

                    if pandas.isnull(row['Latitude']):
                        df.at[index,'Latitude'] = latitude
                        notification.latitude = latitude
                        df.at[index,'Longitude'] = longitude
                        notification.longitude = longitude
                    if pandas.notnull(country):
                        df.at[index,'País de residência'] = country
                        notification.pais_residencia = country
                    if pandas.notnull(state):
                        df.at[index,'Estado de residência'] = state
                        notification.estado_residencia = state
                    if pandas.notnull(city):
                        df.at[index,'Município'] = city
                        notification.municipio = city
                else:
                    print('Erro na busca do google maps')
            notification.save() 

        for index, row in df.iterrows():
            if pandas.notnull(row['País de residência']):
                df.at[index,'País de residência'] = str(row['País de residência']).title()
            if pandas.notnull(row['Estado de residência']):
                df.at[index,'Estado de residência'] = str(row['Estado de residência']).title()
            if pandas.notnull(row['Município']):
                df.at[index,'Município'] = str(row['Município']).title()
            if pandas.notnull(row['Endereço completo']):
                df.at[index,'Endereço completo'] = str(row['Endereço completo']).title()
            if pandas.notnull(row['Endereço completo']):
                df.at[index,'Endereço completo'] = str(row['Endereço completo']).title()
            if pandas.notnull(row['Situação de saúde do paciente no momento da notificação']):
                df.at[index,'Situação de saúde do paciente no momento da notificação'] = str(row['Situação de saúde do paciente no momento da notificação']).title()
            if pandas.notnull(row['Outro local de transmissão, descrever (cidade, região, país)']):
                df.at[index,'Outro local de transmissão, descrever (cidade, região, país)'] = str(row['Outro local de transmissão, descrever (cidade, região, país)']).title()
            if pandas.notnull(row['Estado de notificação (UF)']):
                df.at[index,'Estado de notificação (UF)'] = str(row['Estado de notificação (UF)']).title()
            if pandas.notnull(row['Município de notificação']):
                df.at[index,'Município de notificação'] = str(row['Município de notificação']).title()
            if pandas.notnull(row['Coleta de exames']):
                df.at[index,'Coleta de exames'] = str(row['Coleta de exames']).title()
            if pandas.notnull(row['Coleta de exames']):
                df.at[index,'Classificação final'] = str(row['Classificação final']).title()
            if pandas.notnull(row['Classificação final']):
                df.at[index,'Resultado'] = str(row['Resultado']).title()
            if pandas.notnull(row['INTERNADO']):
                df.at[index,'INTERNADO'] = str(row['INTERNADO']).title()
            if pandas.notnull(row['EVOLUÇÃO']):
                df.at[index,'EVOLUÇÃO'] = str(row['EVOLUÇÃO']).title()

        df = df.replace({None: np.nan})

        df.to_csv(PATH_FILES+'base_preprocessada.csv')
        os.rename(PATH_FILES+BASE_NAME,PATH_FILES+'ok'+BASE_NAME)
    except FileNotFoundError:
        print("Nenhuma base de dados para ser pre_processada")

    print("Listener parado")

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