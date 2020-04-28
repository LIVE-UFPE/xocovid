import pandas as pd
import time
import os

# Pega a base de dados do Brasil.io e faz o processamento para extrair os casos por cidade e por estados
# TODO: encontrar melhor forma de pegar os dados de estados (pegar dados do dia anterior ou pegar os dados após o horário de atualização)
def processingData():
    
    df = pd.read_csv('https://brasil.io/dataset/covid19/caso/?format=csv', sep=',')

    df = df.drop(['place_type', 'death_rate', 'is_last', 'city_ibge_code'], axis=1)

    states = df.state.unique()

    most_recent = df.date.unique()
    most_recent = sorted(most_recent)[-1]

    df2 = df[df['date'] == most_recent]
    casesbystate = pd.DataFrame(columns = ['date', 'state', 'city', 'confirmed', 'deaths', 'estimated_population_2019', 'confirmed_per_100k_inhabitants'])

    for state in states:
        temp = df2[df2['state'] == state]
        stateCases = temp[df2['city'].isnull()]
        casesbystate = pd.concat([stateCases, casesbystate], ignore_index=True)

    casesbystate = casesbystate.drop('city', axis=1)
    casesbystate.to_csv(os.path.join(os.path.dirname(__file__))+'/Casos por Estado.csv')

    casesbycity = df2[df2['city'].notna()]
    casesbycity.to_csv(os.path.join(os.path.dirname(__file__))+'/Casos por cidade.csv')

# roda o processamento em loop a cada 1 dia
"""def main():
    while(True):
        processingData()
        time.sleep(86400)

main()"""