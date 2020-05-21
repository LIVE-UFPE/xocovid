import pandas as pd
import time
import os

# Pega a base de dados do Brasil.io e faz o processamento para extrair os casos por cidade e por estados
def processingData():
    
    brasil_cases = pd.read_csv('https://brasil.io/dataset/covid19/caso/?format=csv', sep=',')

    brasil_cases = brasil_cases.drop(['place_type', 'death_rate', 'city_ibge_code'], axis=1)

    # Casos em PE por cidade
    pernambuco_cases = brasil_cases[brasil_cases['state'] == 'PE']
    pernambuco_cases = pernambuco_cases[pernambuco_cases['city'].notna()]

    states = brasil_cases.state.unique()

    most_recent = brasil_cases.date.unique()
    most_recent = sorted(most_recent)[-1]

    pernambuco_cases.to_csv(os.path.join(os.path.dirname(__file__))+'/casos_pernambuco' + most_recent +'.csv')

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