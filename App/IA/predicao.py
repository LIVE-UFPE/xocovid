import pandas as pd
import numpy as np
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.svm import SVR
import os

def avaliando(y_test, y_pred):
    rmse = mean_squared_error(y_test, y_pred , squared = False)
    print("rmse",rmse)

    mse = mean_squared_error(y_test, y_pred , squared = True)
    print("mse",mse)

    r2 = r2_score(y_test, y_pred)
    print("r2",r2)

def main():
    # Divide o em trino e teste
    pasta = './bases predicao'            
    caminhos = [os.path.join(pasta, nome) for nome in os.listdir(pasta)]
    arquivos = [arq for arq in caminhos if os.path.isfile(arq)]

    arquivos.sort()

    COVID_Train = pd.read_csv(arquivos[0],  sep=',')
    for addressFile in arquivos[:int(0.7*len(arquivos))]:#TODO: ajeitar o range (Qual intervalo de dias analisar?)
        a = pd.read_csv(addressFile,sep=',')
        COVID_Train = np.concatenate((COVID_Train, a), axis=0)

    COVID_Test = pd.read_csv(arquivos[int(0.7*len(arquivos))], sep=',')
    for addressFile in arquivos[int(0.7*len(arquivos))+1:]:#TODO: ajeitar o range (Qual intervalo de dias analisar?)
        a = pd.read_csv(addressFile, sep=',')
        COVID_Test = np.concatenate((COVID_Test, a), axis=0)
    print(COVID_Train.shape)
    print(COVID_Test.shape)


    # x_import = pd.read_csv('./interpolado/predicao_covid19_23-03.csv', encoding='ISO-8859-1', sep=',')
    # x_import = x_import.drop('Unnamed: 0', axis=1)
    # print(x_import.head())

    #Aplicando IA
    #dividindo o dataset
    X_train = COVID_Train[:,:-1]
    y_train = COVID_Train[:,-1:]
    X_test = COVID_Test[:,:-1]
    y_test = COVID_Test[:,-1:]

    

    
    # ##GradientBosstingRegressor
    est = GradientBoostingRegressor(n_estimators=50, learning_rate=0.1,
        max_depth=1, random_state=0, loss='ls').fit(X_train, y_train)
    mean_squared_error(y_test, est.predict(X_test))
    y_pred = est.predict(X_test)
    avaliando(y_test, y_pred)

    
    
    # # ### LinearRegression
    linear_regression = LinearRegression()
    linear_regression.fit(X_train, y_train)
    y_pred = linear_regression.predict(X_test)
    avaliando(y_test, y_pred)

    for addressFile in arquivos[int(0.7*len(arquivos))+1:]:#TODO: ajeitar o range (Qual intervalo de dias analisar?)
        a = pd.read_csv(addressFile, sep=',')
        COVID_Test = np.concatenate((COVID_Test, a), axis=0)
    
    ultimoCSV = pd.read_csv(arquivos[-1], sep=',')
    print(ultimoCSV.columns)
    # dia 1
    day1_pred = linear_regression.predict(ultimoCSV[['longitude','latitude','day2','day3','prediction']].to_numpy())   
    
    ultimoCSV['prediction_day1'] = day1_pred

    # dia 2
    x2 = ultimoCSV.drop(['day1','day2'], axis=1)
    x2 = np.array(x2)
    day2_pred = linear_regression.predict(x2)

    ultimoCSV['prediction_day2'] = day2_pred

    # dia 3

    x3 = ultimoCSV.drop(['day1','day2', 'day3'], axis=1)
    x3 = np.array(x3)
    day3_pred = linear_regression.predict(x3)

    ultimoCSV['prediction_day3'] = day3_pred
    ultimoCSV = ultimoCSV.drop(['prediction','day1', 'day2', 'day3'], axis=1)

    ultimoCSV.to_csv('saidaFinal.csv', index = False)


    # # ### SVR Regression
    # # svr_lin = SVR(kernel='linear', C=100, gamma='auto').fit(X_train, y_train)
    # # y_pred = svr_lin.predict(X_test)
    # # avaliando(y_test, y_pred)
