import pandas as pd
import numpy as np
from datetime import timedelta
import os


def formatData(a):
    # função retirada do código countbyday.py para ajustar as datas
    retorno = a
    b = a.split('-')
    #print('entrada',retorno)
    try:
        if(int(b[2]) <= 12 and int(b[1]) <= 12):
            b[1], b[2] = b[2], b[1]
            #print('aaa')
            retorno = '-'.join(b)
    except:
        print("An exception occurred")
    retorno = retorno.replace(' 00:00:00','')
    #print('saida',retorno)
    return retorno

def date_array(dataframe):
    start_date = dataframe["Data da notificação"].min().to_pydatetime()
    end_date = dataframe["Data da notificação"].max().to_pydatetime()
    end_date = end_date + timedelta(days=1)
    array_dates = np.arange(start_date, end_date, dtype='datetime64[D]')
    return array_dates

def accumulate(datas, datas_confirmacoes, dataframe):
    v_acumulado = np.array([])
    for i in range(0, len(datas)):
        if (i == 0) & (datas[i] not in datas_confirmacoes):
            n_casos = 0
            v_acumulado = np.append(v_acumulado, [[n_casos]])
        else:
            if datas[i] not in datas_confirmacoes:
                n_casos = v_acumulado[i-1]
                v_acumulado = np.append(v_acumulado, [[n_casos]])
            if datas[i] in datas_confirmacoes:
                for j in range(0, len(datas_confirmacoes)):
                    if datas[i] == datas_confirmacoes[j]:
                        n_casos = v_acumulado[i-1] + dataframe["Classificação final"][j]
                        v_acumulado = np.append(v_acumulado, [[n_casos]])
                        break
    return(v_acumulado)

def main():
    #loading the database
    dados_PE = pd.read_csv(os.path.join(os.path.dirname(__file__))+"/entradaPreProcessada.csv", delimiter=',')

    #Sorting the dataset by date
    dados_PE['Data da notificação'] = list(map(formatData, dados_PE['Data da notificação']))
    dados_PE = dados_PE.sort_values(by=['Data da notificação'])
    dados_PE['Data da notificação'] = pd.to_datetime(dados_PE["Data da notificação"])

    # Selecting the covid-19 confirmed cases in Recife
    casosConfirmados = dados_PE[(dados_PE['Município'] == 'Recife') & (dados_PE['Classificação final'].str.lower() == 'confirmado')]

    # counting the number of cases for each day
    casosConfirmados = casosConfirmados.groupby("Data da notificação")["Classificação final"].count().reset_index()

    # calculating the cumulative sum of the confirmed cases in Recife-PE
    dates = date_array(dados_PE)
    datas_confirmados = casosConfirmados["Data da notificação"].values.astype('datetime64[D]')
    casos = accumulate(dates, datas_confirmados, casosConfirmados)

    # exporting to a csv file
    df2 = pd.DataFrame({'dt_notificacao': dates, 'acumulado_confirmados': casos})
    df2.to_csv(os.path.join(os.path.dirname(__file__))+"/baseARIMA_" + str(dates[-1]) + ".csv", index=False)


main()
