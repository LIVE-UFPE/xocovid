import pandas as pd
import App.predicao_arima.chart as chart
import App.predicao_arima.arima as arima
import numpy as np
from datetime import datetime, timedelta
import App.predicao_arima.cumulativeSum as cumulativeSum
import os

def getYesterday():
    last_date = datetime(1990, 1, 1)
    for fileName in os.listdir(os.path.join(os.path.dirname(__file__))+'/dados'):
        try:
            fileName = fileName.split("Casos por Estado ")[1].split(".csv")[0]
        
            if(datetime.strptime(fileName, '%Y-%m-%d') > last_date):
                last_date = datetime.strptime(fileName, '%Y-%m-%d')
        except:
            pass
    return last_date
"""today=datetime.today() 
oneday=timedelta(days=1) 
yesterday=today-oneday  
return yesterday"""



# ontem = str(getYesterday()).split(' ')[0]
# ontem = str(datetime.today()).split(' ')[0]
diasAnalizados  = [
    # str(datetime(2020,4,30)).split(' ')[0],
    # str(datetime(2020,5,1)).split(' ')[0],
    # str(datetime(2020,5,2)).split(' ')[0],
    # str(datetime(2020,5,3)).split(' ')[0],
    # str(datetime(2020,5,4)).split(' ')[0],
    # str(datetime(2020,5,5)).split(' ')[0],
    # str(datetime(2020,5,6)).split(' ')[0],
    # str(datetime(2020,5,7)).split(' ')[0],
    # str(datetime(2020,5,8)).split(' ')[0],
    # str(datetime(2020,5,9)).split(' ')[0],
    # str(datetime(2020,5,10)).split(' ')[0],
    #str(datetime(2020,5,11)).split(' ')[0],
    #str(datetime(2020,5,12)).split(' ')[0],
    #str(datetime(2020,5,13)).split(' ')[0],
    #str(datetime(2020,5,14)).split(' ')[0],
    str(datetime(2020,5,15)).split(' ')[0],
    str(datetime(2020,5,16)).split(' ')[0],
    str(datetime(2020,5,17)).split(' ')[0],
    str(datetime(2020,5,18)).split(' ')[0],
    str(datetime(2020,5,19)).split(' ')[0]
    
    


]
# ontem = str(datetime(2020,30,1)).split(' ')[0]
# ontem = str(datetime(2020,5,1)).split(' ')[0]
# ontem = str(datetime(2020,5,2)).split(' ')[0]
# ontem = str(datetime(2020,5,3)).split(' ')[0]
# ontem = str(datetime(2020,5,4)).split(' ')[0]

# cumulativeSum.main(ontem)
def main():
    for ontem in [str(getYesterday()).split(" ")[0]]:
        cumulativeSum.main(ontem)
        estado_casos = pd.read_csv(os.path.join(os.path.dirname(__file__))+'/dados/Casos por Estado '+ontem +'.csv', sep=',',index_col = 0)

        for tipo in ['Confirmados','Mortes']:
            confirmadosBrasil = pd.read_csv(os.path.join(os.path.dirname(__file__))+'/dados/'+tipo+'Brazil '+ontem +'.csv')

            tabelaTemp = pd.DataFrame()
            tabelaTemp['dt_notificacao'] = confirmadosBrasil['date'].to_numpy()
            if(tipo == 'Confirmados'):
                tabelaTemp['acumulado_confirmados'] = confirmadosBrasil['confirmed'].to_numpy()
            else:
                tabelaTemp['acumulado_confirmados'] = confirmadosBrasil['deaths'].to_numpy()
            tabelaTemp.to_csv(os.path.join(os.path.dirname(__file__))+'/baseARIMA.csv',index = False)
            arima.main('Brasil')
            chart.main('Brasil'+ tipo,ontem)


        for estado in estado_casos['state'].unique():
            casosSelecionados = pd.read_csv(os.path.join(os.path.dirname(__file__))+'/dados/confirmados/'+ontem +estado+'.csv', sep=',')    
            
            tabelaTemp = pd.DataFrame()
            tabelaTemp['dt_notificacao'] = casosSelecionados['dt_notificacao'].to_numpy()
            tabelaTemp['acumulado_confirmados'] = casosSelecionados['acumulado_confirmados'].to_numpy()
            tabelaTemp.to_csv(os.path.join(os.path.dirname(__file__))+'/baseARIMA.csv',index = False)

            arima.main(estado)
            chart.main(estado,ontem)

        

