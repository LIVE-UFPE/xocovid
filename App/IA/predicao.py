import pandas as pd
import numpy as np
# from sklearn.metrics import mean_squared_error, r2_score
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
#from sklearn.svm import SVR
from sklearn.ensemble import RandomForestRegressor
import os

def main():
    
    print('Início das predições')

    regions = ['PE','BR']

    for region in regions:

        pasta = './bases predicao ' + region            
        caminhos = [os.path.join(pasta, nome) for nome in os.listdir(pasta)]
        arquivos = [arq for arq in caminhos if os.path.isfile(arq)]

        arquivos.sort()
        
    ##========================##===========================================##

        dados = pd.read_csv(arquivos[-1], sep=',')

        X_train = dados[['longitude','latitude','day1','day2','day3']]
        y_train = dados['prediction']


        # # ### LinearRegression
        rd = RandomForestRegressor()
        print(rd)
        rd.fit(X_train, y_train)
        
        ultimoCSV = pd.read_csv(arquivos[-1], sep=',')
        print(arquivos[-1])
        print(ultimoCSV.columns)
        # dia 1
        day1_pred = rd.predict(ultimoCSV[['longitude','latitude','day2','day3','prediction']].to_numpy())   
        
        ultimoCSV['prediction_day1'] = day1_pred

        # dia 2
        x2 = ultimoCSV.drop(['day1','day2'], axis=1)
        x2 = np.array(x2)
        day2_pred = rd.predict(x2)

        ultimoCSV['prediction_day2'] = day2_pred

        # dia 3

        x3 = ultimoCSV.drop(['day1','day2', 'day3'], axis=1)
        x3 = np.array(x3)
        day3_pred = rd.predict(x3)

        ultimoCSV['prediction_day3'] = day3_pred
        ultimoCSV = ultimoCSV.drop(['prediction','day1', 'day2', 'day3'], axis=1)

        ultimoCSV.to_csv('saidaFinal' + region + '.csv', index = False)
