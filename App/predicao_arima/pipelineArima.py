import pandas as pd
import App.predicao_arima.chart as chart
import App.predicao_arima.arima as arima
import numpy as np
import os

def main():
    estado_casos = pd.read_csv(os.path.join(os.path.dirname(__file__))+'/Casos por Estado.csv', sep=',',index_col = 0)
    estado_casos.groupby('date').sum()['confirmed'][:-1].to_csv(os.path.join(os.path.dirname(__file__))+'/Brasil.csv')
    brasil = pd.read_csv(os.path.join(os.path.dirname(__file__))+'/Casos por Estado.csv', sep=',')
    tabelaTemp = pd.DataFrame()
    tabelaTemp['dt_notificacao'] = np.flip(brasil['date'].to_numpy())
    tabelaTemp['acumulado_confirmados'] = np.flip(brasil['confirmed'].to_numpy())
    tabelaTemp.to_csv(os.path.join(os.path.dirname(__file__))+'/baseARIMA.csv',index = False)

    arima.main('Brasil')
    chart.main('Brasil')
    for estado in estado_casos['state'].unique():
        
        casosSelecionados = estado_casos[estado_casos['state'] == estado]
        
        tabelaTemp = pd.DataFrame()
        tabelaTemp['dt_notificacao'] = np.flip(casosSelecionados['date'].to_numpy())
        tabelaTemp['acumulado_confirmados'] = np.flip(casosSelecionados['confirmed'].to_numpy())
        tabelaTemp.to_csv(os.path.join(os.path.dirname(__file__))+'/baseARIMA.csv',index = False)

        arima.main(estado)
        chart.main(estado)

    

