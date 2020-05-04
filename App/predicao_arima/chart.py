# import numpy as np 
# import pandas as pd  
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import os



def convertDate(date):
    
    start = date
    year = int(start)
    rem = start - year
    base = datetime(year, 1, 1)
    result = base + timedelta(seconds=(base.replace(year=base.year + 1) - base).total_seconds() * rem)
    print(str(result).split(' ')[0][5:])
    return formatDate(str(result).split(' ')[0])

def formatDate(date):
    temp = date[5:].split('-')
    return '/'.join(temp[::-1])
    




def main(estado):

    proj = pd.read_csv(os.path.join(os.path.dirname(__file__))+"/proj_.csv")
    proj = proj.rename(columns={"Unnamed: 0": "dt_notificacao","Point.Forecast":"acumulado_confirmados"})
    pred = pd.read_csv(os.path.join(os.path.dirname(__file__))+"/pred_.csv")
    pred = pred.rename(columns={"Unnamed: 0": "dt_notificacao","Point.Forecast":"acumulado_confirmados"})
    dados = pd.read_csv(os.path.join(os.path.dirname(__file__))+"/ts.csv", index_col=0)


    dados['dt_notificacao'] = list(map(formatDate,dados['dt_notificacao'].to_numpy()))

    proj['dt_notificacao'] = list(map(convertDate, proj['dt_notificacao'].to_numpy()))
    pred['dt_notificacao'] = list(map(convertDate, pred['dt_notificacao'].to_numpy()))

    projecao = pd.concat([dados,proj]).drop_duplicates(['dt_notificacao'],keep='last')
    predicao = pd.concat([dados,pred]).drop_duplicates(['dt_notificacao'],keep='last')







    # x = np.array([1,2,3,4,5,6,7,8,9,10])
    # y = np.array([1,2,3,4,5,6,7,8,9,10])
    #projeçao
    y_proj_max80 = proj['Hi.80'].to_numpy()
    y_proj_min80 = proj['Lo.80'].to_numpy()
    x_proj = proj['dt_notificacao'].to_numpy()
    y_proj_max95 = proj['Hi.95'].to_numpy()
    y_proj_min95 = proj['Lo.95'].to_numpy()
    #pred
    y_pred_max80 = pred['Hi.80'].to_numpy()
    y_pred_min80 = pred['Lo.80'].to_numpy()
    x_pred = pred['dt_notificacao'].to_numpy()
    y_pred_max95 = pred['Hi.95'].to_numpy()
    y_pred_min95 = pred['Lo.95'].to_numpy()



    # Projeção
    # plt.figure(figsize=(15, 5),dpi=200)
    plt.figure(figsize=(20, 5),dpi=200)
    plt.title("Modelo Arima Projeção")
    plt.xlabel("Data")
    plt.ylabel("Casos confirmados")



    x_ticks = np.arange(0, len(projecao['dt_notificacao'].to_numpy()), int(len(projecao['dt_notificacao'].to_numpy())/20))
    plt.xticks(x_ticks)
    plt.plot(projecao['dt_notificacao'], projecao['acumulado_confirmados'], '-', color='red')

    plt.fill_between(x_proj, y_proj_max80,y_proj_min80,color='blue', alpha=0.1)
    plt.fill_between(x_proj, y_proj_max95,y_proj_min95,color='green', alpha=0.1)
    plt.grid()

    plt.savefig(os.path.join(os.path.dirname(__file__))+'/SaidaArima/projecao'+estado+'.png')
    projecao.to_csv(os.path.join(os.path.dirname(__file__))+'/SaidaArima/projecao'+estado+'.csv')



    # Predicao
    # plt.figure(figsize=(20, 5),dpi=200)
    # plt.title("Modelo Arima Predição")
    # plt.xlabel("Data")
    # plt.ylabel("Casos confirmados")



    # indexDataLimite = np.where(dados['dt_notificacao'].to_numpy() == pred['dt_notificacao'].to_numpy()[-1])[0][0]
    # x = np.append(dados['dt_notificacao'].to_numpy()[:indexDataLimite],pred['dt_notificacao'].to_numpy())
    # y = np.append(dados['acumulado_confirmados'].to_numpy()[:indexDataLimite],pred['acumulado_confirmados'].to_numpy())

    # plt.plot(x, y, '-', color='blue', label='Casos previstos')

    # plt.fill_between(x_pred, y_pred_max80,y_pred_min80,color='blue', alpha=0.1)
    # plt.fill_between(x_pred, y_pred_max95,y_pred_min95,color='green', alpha=0.1)

    # # x = dados['dt_notificacao'].to_numpy()[:indexDataLimite+1]
    # # y = dados['acumulado_confirmados'].to_numpy()[:indexDataLimite+1]
    # # plt.plot(x, y, '-', color='red', label='Casos reais')
    # x_ticks = np.arange(0, len(x), int(len(x)/20))
    # plt.xticks(x_ticks)

    # plt.legend(loc="upper left")
    # plt.grid()

    # plt.savefig('./SaidaArima/predicao'+estado+'.png')



