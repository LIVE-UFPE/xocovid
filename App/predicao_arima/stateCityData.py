import pandas as pd
import time
from datetime import datetime, timedelta
import os
from urllib.request import Request, urlopen
import requests
import shutil
import gzip

def getYesterday(): 
	today=datetime.today() 
	oneday=timedelta(days=1) 
	yesterday=today-oneday  
	return yesterday

global ontem
ontem = getYesterday()
ontem = datetime(ontem.year,ontem.month, ontem.day,23,59)
# ontem = datetime(2020,5,9,23,59)

# função auxiliar para fazer download e extração dos dados do brasil.io
def getData():
    
    url = "https://data.brasil.io/dataset/covid19/caso.csv.gz"
    filename = url.split("/")[-1]
    # faz download do arquivo .gz e salva no diretório
    with open(os.path.join(os.path.dirname(__file__))+'/'+filename, "wb") as f:
        r = requests.get(url)
        f.write(r.content)
    # extrai arquivo e salva como csv
    with gzip.open(os.path.join(os.path.dirname(__file__))+'/caso.csv.gz', 'rb') as f_in:
        with open(os.path.join(os.path.dirname(__file__))+'/casos.csv', 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
    os.remove(os.path.join(os.path.dirname(__file__))+'/caso.csv.gz')

# Processamento para extrair os casos por cidade e por estados
def processingData():
    getData()
    brasil_cases = pd.read_csv(os.path.join(os.path.dirname(__file__))+'/casos.csv', sep=',')
    # retirando colunas desnecessárias
    brasil_cases = brasil_cases.drop(['death_rate', 'city_ibge_code', 'order_for_place'], axis=1)

    # data mais recente de atualização
    most_recent = brasil_cases.date.unique()
    most_recent = sorted(most_recent)[-1]

    # casos por cidades do BR
    #casesbycity = brasil_cases[brasil_cases['place_type'] == 'city']
    #casesbycity = casesbycity.drop('place_type', axis=1).reset_index(drop=True)
    #casesbycity.to_csv('Casos por cidade '+ most_recent + '.csv')
    
    # Casos em PE por cidade
    #pernambuco_cases = brasil_cases[brasil_cases['state'] == 'PE']
    #pernambuco_cases = pernambuco_cases[pernambuco_cases['place_type'] == 'city']
    #pernambuco_cases = pernambuco_cases.drop('place_type', axis=1).reset_index(drop=True)
    #pernambuco_cases.to_csv('casos_pernambuco' + most_recent +'.csv')

    states = brasil_cases.state.unique()

    # Casos acumulados no país por cidade e por estado 
    acumulado_pais = brasil_cases
    print(brasil_cases.columns)
    casesbystate = pd.DataFrame(columns = brasil_cases.columns)

    for state in states:
        temp = acumulado_pais[acumulado_pais['state'] == state]
        stateCases = temp[acumulado_pais['city'].isnull()]
        casesbystate = pd.concat([stateCases, casesbystate], ignore_index=True)

    casesbystate = casesbystate.drop('city', axis=1)
    
    casesbystate.to_csv(os.path.join(os.path.dirname(__file__))+'/dados/Casos por Estado '+ most_recent +'.csv')

    casesbycity = acumulado_pais[acumulado_pais['city'].notna()]

    os.remove(os.path.join(os.path.dirname(__file__))+'/casos.csv')

def brasilCases():
    global ontem
    req = Request("https://brasil.io/dataset/covid19/caso_full/?place_type=state&format=csv", headers={'User-Agent': 'Mozilla/5.0'})

    response = urlopen(req)

    casosBrasil = pd.read_csv(response)
    casosBrasil['date'] = casosBrasil['date'].astype('datetime64[D]')

    print('Dados coletados até: ',ontem)

    # ontem = datetime(ontem.year,ontem.month, ontem.day,23,59)
    
    casosBrasil = casosBrasil[casosBrasil['date'] < ontem]
    most_recent = str(casosBrasil['date'].max()).split(' ')[0]
    
    
    casosBrasil.rename(columns={'last_available_confirmed':'confirmed','last_available_deaths':'deaths'}, inplace=True)
    b = casosBrasil.groupby('date').sum()['confirmed']
    b.to_csv(os.path.join(os.path.dirname(__file__))+'/dados/ConfirmadosBrazil '+ most_recent + '.csv')
    b = casosBrasil.groupby('date').sum()['deaths']
    b.to_csv(os.path.join(os.path.dirname(__file__))+'/dados/MortesBrazil '+ most_recent + '.csv')
    

def main():
    processingData()
    brasilCases()

"""# Pega a base de dados do Brasil.io e faz o processamento para extrair os casos por cidade e por estados
def processingData():
    global ontem

    req = Request('https://brasil.io/dataset/covid19/caso/?format=csv', headers={'User-Agent': 'Mozilla/5.0'})

    response = urlopen(req)

    brasil_cases = pd.read_csv(response, sep=',')
    brasil_cases['date'] = brasil_cases['date'].astype('datetime64[D]')
    brasil_cases = brasil_cases[brasil_cases['date'] < ontem]

    most_recent = str(brasil_cases['date'].max()).split(' ')[0]

    brasil_cases = brasil_cases.drop(['place_type', 'death_rate', 'city_ibge_code'], axis=1)

    
    states = brasil_cases.state.unique()

    # Casos acumulados no país por cidade e por estado 
    acumulado_pais = brasil_cases
    print(brasil_cases.columns)
    casesbystate = pd.DataFrame(columns = brasil_cases.columns)

    for state in states:
        temp = acumulado_pais[acumulado_pais['state'] == state]
        stateCases = temp[acumulado_pais['city'].isnull()]
        casesbystate = pd.concat([stateCases, casesbystate], ignore_index=True)

    casesbystate = casesbystate.drop('city', axis=1)
    
    casesbystate.to_csv(os.path.join(os.path.dirname(__file__))+'/dados/Casos por Estado '+ most_recent +'.csv')

    casesbycity = acumulado_pais[acumulado_pais['city'].notna()]
"""