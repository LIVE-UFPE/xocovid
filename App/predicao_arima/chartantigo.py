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
    print(str(result).split(' ')[0])
    return str(result).split(' ')[0]




def main(estado):
    proj = pd.read_csv(os.path.join(os.path.dirname(__file__))+"/proj_.csv")
    proj = proj.rename(columns={"Unnamed: 0": "dt_notificacao"})
    pred = pd.read_csv(os.path.join(os.path.dirname(__file__))+"/pred_.csv")
    pred = pred.rename(columns={"Unnamed: 0": "dt_notificacao"})
    dados = pd.read_csv(os.path.join(os.path.dirname(__file__))+"/ts.csv", index_col=0)

    proj['dt_notificacao'] = list(map(convertDate, proj['dt_notificacao'].to_numpy()))
    pred['dt_notificacao'] = list(map(convertDate, pred['dt_notificacao'].to_numpy()))

    x = np.append(dados['dt_notificacao'].to_numpy(),proj['dt_notificacao'].to_numpy())
    y = np.append(dados['acumulado_confirmados'].to_numpy(),proj['Point.Forecast'].to_numpy())


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
    plt.figure(figsize=(15, 5),dpi=200)
    plt.title("Modelo Arima Projeção")
    plt.xlabel("Data")
    plt.ylabel("Casos confirmados")
    x_ticks = np.arange(0, len(x), int(len(x)/8))
    plt.xticks(x_ticks)
    plt.plot(x, y, '-', color='red')
    plt.fill_between(x_proj, y_proj_max80,y_proj_min80,color='blue', alpha=0.1)
    plt.fill_between(x_proj, y_proj_max95,y_proj_min95,color='green', alpha=0.1)
    plt.grid()
    plt.savefig(os.path.join(os.path.dirname(__file__))+'/SaidaArima/projecao'+ estado +'.png')



    # Predicao
    plt.figure(figsize=(15, 5),dpi=200)
    plt.title("Modelo Arima Predição")
    plt.xlabel("Data")
    plt.ylabel("Casos confirmados")
    x_ticks = np.arange(0, len(x), int(len(x)/8))
    plt.xticks(x_ticks)


    x = np.append(dados['dt_notificacao'].to_numpy()[:-pred.shape[0]],pred['dt_notificacao'].to_numpy())
    y = np.append(dados['acumulado_confirmados'].to_numpy()[:-pred.shape[0]],pred['Point.Forecast'].to_numpy())
    plt.plot(x, y, '-', color='blue', label='Casos previstos')

    plt.fill_between(x_pred, y_pred_max80,y_pred_min80,color='blue', alpha=0.1)
    plt.fill_between(x_pred, y_pred_max95,y_pred_min95,color='green', alpha=0.1)

    x = dados['dt_notificacao'].to_numpy()
    y = dados['acumulado_confirmados'].to_numpy()
    plt.plot(x, y, '-', color='red', label='Casos reais')

    plt.legend(loc="upper left")
    plt.grid()
    plt.savefig(os.path.join(os.path.dirname(__file__))+'/SaidaArima/predicao'+estado+'.png')



