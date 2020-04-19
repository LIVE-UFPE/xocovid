import pandas as pd 
import numpy as np 
from datetime import datetime
import os

def formatData(a):
    retorno = a
    b = a.split('-')
    print('entrada',retorno)
    try:
        if(int(b[2]) <= 12 and int(b[1]) <= 12):
            b[1] ,b[2] = b[2],b[1]
            print('aaa')
            retorno = '-'.join(b)
    except:
        print("An exception occurred")
    retorno = retorno.replace(' 00:00:00','')
    print('saida',retorno)
    return retorno

def main():

    # getting the date 
    now = datetime.now()

    # creating a new directory
    # caminho = str(now.day) + '-'+ str(now.month)
    # os.mkdir(caminho)

    # read dataframes
    casosCovidPE = pd.read_csv('saidaPreProcessada.csv', sep=',')
    bairros = pd.read_csv('listaBairros.csv', sep=',')

    # putting string data in the same case
    bairros.Bairro = bairros.Bairro.str.lower()
    casosCovidPE.Bairro = casosCovidPE.Bairro.str.lower()

    # getting only confirmed cases
    casosRecife = casosCovidPE[(casosCovidPE['Município'] == 'Recife') & (casosCovidPE['Classificação final'].str.lower() == 'confirmado')]


    # dropping uneeded data
    casosRecife = casosRecife.drop(['ID','Data Atualização', 'Data dos primeiros sintomas', 'Paciente foi hospitalizado?',
                  'Data da internação hospitalar', 'Data da alta hospitalar', 'Data do isolamento','Paciente foi submetido a ventilação mecânica?',
                  'Situação de saúde do paciente no momento da notificação','Sexo', 'Idade', 'CEP residência', 'País de residência', 
                  'Estado de residência', 'Município', 'Endereço completo', 'Estado de notificação (UF)', 'Município de notificação', 
                  'Coleta de exames', 'Foi realizada coleta de amostra do paciente?','Foi para outro local de transmissão?', 'Data da viagem de ida para outro local transmissão','Data da viagem de volta do outro local transmissão',
                  'Data da chegada no Brasil','Classificação final','Resultado', 'INTERNADO', 'EVOLUÇÃO', 'Outro local de transmissão, descrever (cidade, região, país)', 'Latitude', 'Longitude'], axis=1)

    # sorting by date
    casosRecife['Data da notificação'] = list(map(formatData, casosRecife['Data da notificação']))
    casosRecife = casosRecife.sort_values(by=['Data da notificação'])
    
    dias = casosRecife['Data da notificação'].unique()
    print(dias)
    dias = np.insert(dias,1,'2020-03-06')
    dias = np.insert(dias,2,'2020-03-07')
    dias = np.insert(dias,3,'2020-03-08')
    dias = np.insert(dias,4,'2020-03-09')
    dias = np.insert(dias,5,'2020-03-10')
    dias = np.insert(dias,5,'2020-03-11')
    print(dias)

    # couting cases by location in each day and saving datasets
    casosAnt = len(bairros.Bairro) * [0]
    for dia in dias:
        casos = len(bairros.Bairro) * [0]
        temp = casosRecife[casosRecife['Data da notificação'] == dia]
        aux = temp.groupby('Bairro').count()
        for i, bairro in enumerate(bairros.Bairro.values):
            if bairro in temp.Bairro.values:
                casos[i] += aux['Data da notificação'][bairro] + casosAnt[i]
            else:
                casos[i] = casosAnt[i]
        casosBairro = bairros.drop(['Y', 'X', 'latitude-WGS84', 'longitude-WGS84'], axis=1)
        casosBairro['latitude'] = bairros['latitude-WGS84']
        casosBairro['longitude'] = bairros['longitude-WGS84']
        casosBairro['casos'] = casos
        casosAnt = casos
        casosBairro.to_csv('casos confirmados/covid19_'+dia[5:10] + '.csv')
