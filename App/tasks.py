from background_task import background
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from .models import Listener, Notification

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