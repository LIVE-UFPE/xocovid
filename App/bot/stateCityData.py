from urllib.request import Request, urlopen
import pandas as pd
import time
import os
import gzip
import shutil
import requests

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
    casesbycity = brasil_cases[brasil_cases['place_type'] == 'city']
    casesbycity = casesbycity.drop('place_type', axis=1).reset_index(drop=True)
    casesbycity.to_csv(os.path.join(os.path.dirname(__file__))+'/Ultimos Casos por cidade.csv')
    
    # Casos em PE por cidade
    #pernambuco_cases = brasil_cases[brasil_cases['state'] == 'PE']
    #pernambuco_cases = pernambuco_cases[pernambuco_cases['place_type'] == 'city']
    #pernambuco_cases = pernambuco_cases.drop('place_type', axis=1).reset_index(drop=True)
    #pernambuco_cases.to_csv('casos_pernambuco' + most_recent +'.csv')

    # Casos acumulados no país por cidade e por estado 
    acumulado_pais = brasil_cases[brasil_cases['is_last'] == True]
    acumulado_pais = acumulado_pais[acumulado_pais['place_type'] == 'state']
    # removendo colunas desnecessárias e salvando dataframe dos estados
    #acumulado_pais = acumulado_pais.drop(['place_type','city'], axis=1).reset_index(drop = True)
    acumulado_pais.to_csv(os.path.join(os.path.dirname(__file__))+'/Ultimos Casos por Estado.csv')
    casesbystate = pd.DataFrame(columns = ['date', 'state', 'city', 'confirmed', 'deaths', 'estimated_population_2019', 'confirmed_per_100k_inhabitants'])
    states = brasil_cases.state.unique()
    for state in states:
        temp = brasil_cases[brasil_cases['state'] == state]
        stateCases = temp[brasil_cases['city'].isnull()]
        casesbystate = pd.concat([stateCases, casesbystate], ignore_index=True)    
    casesbystate = casesbystate.drop('city', axis=1)
    casesbystate.to_csv(os.path.join(os.path.dirname(__file__))+'/Casos por Estado.csv')

    os.remove(os.path.join(os.path.dirname(__file__))+'/casos.csv')


# Pega a base de dados do Brasil.io e faz o processamento para extrair os casos por cidade e por estados
"""def processingData():
    
    req = Request('https://brasil.io/dataset/covid19/caso/?format=csv', headers={'User-Agent': 'Mozilla/5.0'})

    response = urlopen(req)

    brasil_cases = pd.read_csv(response, sep=',')

    brasil_cases = brasil_cases.drop(['place_type', 'death_rate', 'city_ibge_code'], axis=1)

    # Casos em PE por cidade
    pernambuco_cases = brasil_cases[brasil_cases['state'] == 'PE']
    pernambuco_cases = pernambuco_cases[pernambuco_cases['city'].notna()]

    states = brasil_cases.state.unique()

    most_recent = brasil_cases.date.unique()
    most_recent = sorted(most_recent)[-1]

    #pernambuco_cases.to_csv(os.path.join(os.path.dirname(__file__))+'/casos_pernambuco' + most_recent +'.csv')

    # Casos acumulados no país por cidade e por estado 
    acumulado_pais = brasil_cases
    casesbystate = pd.DataFrame(columns = ['date', 'state', 'city', 'confirmed', 'deaths', 'estimated_population_2019', 'confirmed_per_100k_inhabitants'])

    for state in states:
        temp = acumulado_pais[acumulado_pais['state'] == state]
        stateCases = temp[acumulado_pais['city'].isnull()]
        casesbystate = pd.concat([stateCases, casesbystate], ignore_index=True)

    casesbystate = casesbystate.drop('city', axis=1)
    casesbystate.to_csv(os.path.join(os.path.dirname(__file__))+'/Casos por Estado.csv')

    casesbycity = acumulado_pais[acumulado_pais['city'].notna()]
    casesbycity.to_csv(os.path.join(os.path.dirname(__file__))+'/Ultimos Casos por cidade.csv')

    casesbystate = casesbystate[casesbystate['is_last']==True]
    casesbystate.to_csv(os.path.join(os.path.dirname(__file__))+'/Ultimos Casos por Estado.csv')
"""