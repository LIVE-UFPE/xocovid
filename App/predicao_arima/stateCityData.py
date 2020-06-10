import pandas as pd
import time
from datetime import datetime, timedelta
import os
from urllib.request import Request, urlopen


def getYesterday(): 
	today=datetime.today() 
	oneday=timedelta(days=1) 
	yesterday=today-oneday  
	return yesterday

global ontem
ontem = getYesterday()
ontem = datetime(ontem.year,ontem.month, ontem.day,23,59)

# ontem = datetime(2020,5,9,23,59)


# Pega a base de dados do Brasil.io e faz o processamento para extrair os casos por cidade e por estados
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