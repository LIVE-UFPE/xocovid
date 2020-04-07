import os
import pandas
def main():   
    df = pandas.read_csv(os.path.join(os.path.dirname(__file__))+'/saida1.csv')
    #interpolacao
    df1 = pandas.read_csv(os.path.join(os.path.dirname(__file__))+'/predicao_covid19_13-03.csv')

    df1.to_csv(os.path.join(os.path.dirname(__file__))+'/saida2.csv')
