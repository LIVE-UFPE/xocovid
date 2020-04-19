import pandas
import numpy as np
import json
import requests
from itertools import islice

def requestData(request=None, type='google'):
	APIKEY = 'AIzaSyA9py_5Ave_r37HxH4694TpCHQJC6B63HI' # ESSA KEY É A MINHA (GABRIEL MARQUES) KEY DA  API DO GOOGLE MAPS
													# ESTOU DEIXANDO ELA AQUI PQ SOU UMA PESSOA LEGAL
													# MAS O IDEAL É QUE TU USE A SUA =)

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
def main():

	PATH_BASE = './entradaPreProcessada.csv'
	
	df = pandas.read_csv(PATH_BASE)
	df = df[df['Classificação final'].str.lower() == 'confirmado']
	df = df[df['Município'].str.lower() == 'recife']
	
	print('Casos confirmados em Recife',df.shape)

	#MODIFICAÇÃO
	df["Bairro"] = None
	df["Latitude"] = None
	df["Longitude"] = None
	for index, row in df.iterrows():
		print("Geocodificando a linha "+str(index))

		address = str(row['Endereço completo'])+' '+str(row['Município'])+' '+str(row['Estado de residência'])+' '+str(row['País de residência'])
		addressJSON = requestData(request=address, type='google')
		if pandas.notnull(addressJSON):
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
			print("Geocodificando a linha "+str(index))

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

	df = df.replace({np.nan: None})
	df.to_csv('saidaPreProcessada.csv',index ='False')
	# df[['Data Atualização','Bairro','Latitude','Longitude']].to_csv('saida1.csv',index ='False')
	df = df[['Data Atualização','Bairro','Latitude','Longitude']]
	