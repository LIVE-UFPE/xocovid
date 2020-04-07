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
    COVID_Train = pd.read_csv(os.path.join(os.path.dirname(__file__))+'/interpolado/predicao_covid19_08-03.csv', encoding='ISO-8859-1', sep=',')
    COVID_Train = COVID_Train.drop('Unnamed: 0', axis=1).to_numpy()
    for index in range(9,20):#TODO: ajeitar o range (Qual intervalo de dias analisar?)
        print(index)
        if(index < 10):
            a = pd.read_csv(os.path.join(os.path.dirname(__file__))+'/interpolado/predicao_covid19_0'+str(index)+'-03.csv', encoding='ISO-8859-1', sep=',')
        else:
            a = pd.read_csv(os.path.join(os.path.dirname(__file__))+'/interpolado/predicao_covid19_'+str(index)+'-03.csv', encoding='ISO-8859-1', sep=',')

    a = a.drop('Unnamed: 0', axis=1) 
    COVID_Train = np.concatenate((COVID_Train, a), axis=0)

    COVID_Test = pd.read_csv(os.path.join(os.path.dirname(__file__))+'/interpolado/predicao_covid19_20-03.csv', encoding='ISO-8859-1', sep=',')
    COVID_Test = COVID_Test.drop('Unnamed: 0', axis=1).to_numpy()
    for index in range(21,24):
        print(index)
        a = pd.read_csv(os.path.join(os.path.dirname(__file__))+'/interpolado/predicao_covid19_'+str(index)+'-03.csv', encoding='ISO-8859-1', sep=',')
        a = a.drop('Unnamed: 0', axis=1) 
        COVID_Test = np.concatenate((COVID_Test, a), axis=0)
    print(COVID_Train.shape)
    print(COVID_Test.shape)


    x_import = pd.read_csv(os.path.join(os.path.dirname(__file__))+'/interpolado/predicao_covid19_23-03.csv', encoding='ISO-8859-1', sep=',')
    x_import = x_import.drop('Unnamed: 0', axis=1)
    print(x_import.head())

    #Aplicando IA
    #dividindo o dataset
    X_train = COVID_Train[:,:-1]
    y_train = COVID_Train[:,-1:]
    X_test = COVID_Test[:,:-1]
    y_test = COVID_Test[:,-1:]

    

    
    ##GradientBosstingRegressor
    est = GradientBoostingRegressor(n_estimators=50, learning_rate=0.1,
        max_depth=1, random_state=0, loss='ls').fit(X_train, y_train)
    mean_squared_error(y_test, est.predict(X_test))
    y_pred = est.predict(X_test)
    avaliando(y_test, y_pred)

    df2 = pd.DataFrame(COVID_Test,columns=['lat', 'lng', 'd1','d2','d3','prediction'])
    df2 = df2[['lat','lng','prediction']]
    df2['prediction'] = y_pred
    df2.to_csv('saida3.csv')

    
    # ### LinearRegression
    # linear_regression = LinearRegression()
    # linear_regression.fit(X_train, y_train)
    # y_pred = linear_regression.predict(X_test)
    # avaliando(y_test, y_pred)

    # ### SVR Regression
    # svr_lin = SVR(kernel='linear', C=100, gamma='auto').fit(X_train, y_train)
    # y_pred = svr_lin.predict(X_test)
    # avaliando(y_test, y_pred)

    

    


    


