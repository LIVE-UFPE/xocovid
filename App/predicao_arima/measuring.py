import pandas as pd
import chart
import arima
import numpy as np
from datetime import datetime, timedelta
import math
import os

def getYesterday(): 
	today=datetime.today() 
	oneday=timedelta(days=1) 
	yesterday=today-oneday  
	return yesterday



ontem = str(getYesterday()).split(' ')[0]
# ontem = str(datetime.today()).split(' ')[0]
ontem = str(datetime(2020,5,14)).split(' ')[0]





# dataAnalisada = str(datetime(2020,4,30)).split(' ')[0]
# dataAnalisada = str(datetime(2020,5,1)).split(' ')[0]
# dataAnalisada = str(datetime(2020,5,2)).split(' ')[0]
# dataAnalisada = str(datetime(2020,5,3)).split(' ')[0]
# dataAnalisada = str(datetime(2020,5,6)).split(' ')[0]
dias = [
    str(datetime(2020,4,30)).split(' ')[0],
    str(datetime(2020,5,1)).split(' ')[0],
    str(datetime(2020,5,2)).split(' ')[0],
    str(datetime(2020,5,3)).split(' ')[0],
    str(datetime(2020,5,4)).split(' ')[0],
    str(datetime(2020,5,5)).split(' ')[0],
    str(datetime(2020,5,6)).split(' ')[0],
    str(datetime(2020,5,7)).split(' ')[0],
    str(datetime(2020,5,8)).split(' ')[0],
    str(datetime(2020,5,9)).split(' ')[0],
]
for dataAnalisada in dias:
    f = open('relatorio '+ dataAnalisada +  '.txt', "w")
    f.write("Dados até : " + ontem + '\n')
    print("Dados até : " + ontem + '\n')
    f.write("Data analisada: " + dataAnalisada + '\n')
    ("Data analisada: " + dataAnalisada + '\n')


    print(dataAnalisada,ontem)

    estado_casos = pd.read_csv('./dados/Casos por Estado '+ontem+'.csv', sep=',',index_col = 0)
    ##############################
    casosBrasil = pd.read_csv('./dados/ConfirmadosBrazil '+ontem+'.csv', sep=',',index_col = 0)





    diasPrevistos = 7




    erros = []
    totalDiasEstado = []
    margem95 = []
    margem80 = []
    Estados = np.append(estado_casos['state'].unique(),['BrasilConfirmados'])

    for estado in Estados:
        # casosSelecionados = pd.read_csv('./backup/SaidaArima/projecao'+estado+hoje+'.csv', sep=',',index_col = 0)
        
        casosSelecionados = pd.read_csv('./SaidaArima/'+dataAnalisada+'/projecao'+estado+dataAnalisada+'.csv', sep=',',index_col = 0)
        
        
        totalDiasEstado.append(casosSelecionados.shape[0])
        casosSelecionados = casosSelecionados.tail(diasPrevistos)
        
        f.write("----------------------------------------------------------------------------- + '\n'")
        f.write("Estado analisado: " + estado + '\n')
        estadoTemp = 0
        if(estado != 'BrasilConfirmados'):
            estadoTemp = estado_casos[estado_casos['state']==estado]
        else:
            estadoTemp = pd.read_csv('./dados/ConfirmadosBrazil ' +ontem +'.csv', sep=',',index_col = 0)
        
        
        
        erroPercentual = np.ones(diasPrevistos)*(math.nan)
        
        
        for data,index in zip(casosSelecionados['dt_notificacao'],range(diasPrevistos)):
            temp = data.split("/")
            # print(temp)
            dataFormated = '2020-' + '-'.join(temp[::-1])
            # print(dataFormated)
            # print(estadoTemp.tail(10))
            if(estadoTemp.query('date =="'+dataFormated+'"').shape[0] !=0):
                # print("entourrrrrrrrrrrrrrrrrrrrr")
                valorReal = estadoTemp.query('date =="'+dataFormated+'"')['confirmed'].to_list()[0]
                f.write('Dia ' +  dataFormated + '\n')
                f.write('   Valor Real: %d' %round(valorReal) + '\n')
                # print(casosSelecionados.query('dt_notificacao =="'+data+'"')['acumulado_confirmados'])
                valorPredito = casosSelecionados.query('dt_notificacao =="'+data+'"')['acumulado_confirmados'].to_list()[0]
                f.write('   Valor predito: %d' %round(valorPredito) + '\n')
                erroPercentual[index] = round(100*(valorPredito - valorReal)/float(valorReal),2)
                margem95Hi = casosSelecionados.query('dt_notificacao =="'+data+'"')['Hi.95'].to_list()[0]
                margem95Lo = casosSelecionados.query('dt_notificacao =="'+data+'"')['Lo.95'].to_list()[0]
                margem80Hi = casosSelecionados.query('dt_notificacao =="'+data+'"')['Hi.80'].to_list()[0]
                margem80Lo = casosSelecionados.query('dt_notificacao =="'+data+'"')['Lo.80'].to_list()[0]
                if(valorReal<=margem95Hi and valorReal >= margem95Lo):
                    margem95.append(True)
                else:
                    margem95.append(False)
                if(valorReal<=margem80Hi and valorReal >= margem80Lo):
                    margem80.append(True)
                else:
                    margem80.append(False)
                # print(erroPercentual[index])
                # print(round(erroPercentual[index]))
            else:
                f.write('Dia ' +  dataFormated + '\n')
                f.write('   Valor Real: Não divulgado até o momento' + '\n')
                valorPredito = casosSelecionados.query('dt_notificacao =="'+data+'"')['acumulado_confirmados'].to_list()[0]
                f.write('   Valor predito: %d' %round(valorPredito) + '\n')
                margem95.append(math.nan)
                margem80.append(math.nan)
        f.write("Erro percentual para:" + '\n')
        erros.append(erroPercentual)
        for dia in range(len(erroPercentual)):
            if(erroPercentual[dia] == math.nan):
                f.write("\tDia " +  str(dia+1)+": Não é possivel calcular"  + '\n')
            else:
                f.write("\tDia " +  str(dia+1)+": " + str(erroPercentual[dia]) + "%" + '\n')

    margem95 = np.array(margem95).reshape(-1,diasPrevistos)
    margem80 = np.array(margem80).reshape(-1,diasPrevistos)
    erros = np.array(erros)
    # print(erros)

    d = {
        'Estados': Estados, 
        'Dias coletados': totalDiasEstado
        
        }
    for dia in range(diasPrevistos):
        d['Erro dia(%) ' +str(dia+1)] =  erros[: , dia:dia+1].reshape(-1)
        d['Margem 95 Dia ' +str(dia+1)] =  margem95[: , dia:dia+1].reshape(-1)
        d['Margem 80 Dia ' +str(dia+1)] =  margem80[: , dia:dia+1].reshape(-1)
        

    df = pd.DataFrame(d)
    f.write(df.to_string() + '\n')


    f.write('Está na margem de 95' + '\n')
    for dia in range(diasPrevistos):
        somatorio = df[df['Margem 95 Dia '+str(dia+1)]==1].shape[0]
        qtd = df[df['Margem 95 Dia '+str(dia+1)]==0].shape[0] + somatorio
        f.write(str(np.sort(df[df['Margem 95 Dia '+str(dia+1)]==1]['Estados'].to_numpy())) + '\n')
        # print(str(np.sort(df[df['Margem 95 Dia '+str(dia+1)]==1]['Estados'].to_numpy())) + '\n')
        f.write("Dia " + str(dia+1)+': ' + str(somatorio)+'/'+str(qtd)  + '\n')
        
    f.write('Está na margem de 80' + '\n')
    for dia in range(diasPrevistos):
        somatorio = df[df['Margem 80 Dia '+str(dia+1)]==1].shape[0]
        qtd = df[df['Margem 80 Dia '+str(dia+1)]==0].shape[0] + somatorio
        f.write(str(np.sort(df[df['Margem 80 Dia '+str(dia+1)]==1]['Estados'].to_numpy())) + '\n')
        f.write("Dia " + str(dia+1)+': ' + str(somatorio)+'/' + str(qtd)  + '\n')

    for dia in range(len(erroPercentual)):
        a = np.abs(erros[: ,dia:dia+1])
        nan_array = np.isnan(a)
        not_nan_array = ~ nan_array
        a = a[not_nan_array]
        print('Média do dia '+ str(dia+1)+' :'+str(round(a.sum()/len(a),2 ))+'%' + '\n')
        f.write('Média do dia '+ str(dia+1)+' :'+str(round(a.sum()/len(a),2 ))+'%' + '\n')
        
    f.close()