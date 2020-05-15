import pandas as pd 
import numpy as np 
from datetime import datetime
import os

def main():

    # getting the date 
    now = datetime.now()

    # read dataframes
    casosCovidBR = pd.read_csv(os.path.join(os.path.dirname(__file__))+'/Casos por cidade 2020-05-06.csv', sep=',')
    cidades = pd.read_csv(os.path.join(os.path.dirname(__file__))+'/lista_municipios/latitude-longitude-cidades.csv', sep=';')

    # putting string data in the same case
    cidades.municipio = cidades.municipio.str.lower()
    casosCovidBR.city = casosCovidBR.city.str.lower()

    # sorting by date
    casosCovidBR = casosCovidBR[casosCovidBR['city'] != 'Importados/Indefinidos']
    casosCovidBR = casosCovidBR.sort_values(by=['date'])

    # couting cases by location in each day and saving datasets
    dias = casosCovidBR['date'].unique()
    casosAnt = len(cidades.municipio) * [0]
    for dia in dias:
        casos = len(cidades.municipio) * [0]
        temp = casosCovidBR[casosCovidBR['date'] == dia]
        for i, cidade in enumerate(cidades.municipio.values):
            if cidade in temp.city.values:
                aux = temp[temp['city'] == cidade]
                aux = aux[aux['date'] == dia]
                casos[i] = aux['confirmed'].values[0]
            else:
                casos[i] = casosAnt[i]
        cidades['casos'] = casos
        casosAnt = casos
        cidades.to_csv(os.path.join(os.path.dirname(__file__))+'/casos confirmados BR/covid19BR_'+dia[5:10] + '.csv')
        cidadesPE = cidades[cidades['uf'] == 'PE']
        cidadesPE.to_csv(os.path.join(os.path.dirname(__file__))+'/casos confirmados PE/covid19PE_'+dia[5:10] + '.csv')
