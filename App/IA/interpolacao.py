import subprocess
import os


def interpolacao(day1, day2, day3, day4):
    # run data_interpolation.R
    arg = [day1, day2, day3, day4]

    # Define command and arguments
    # command = r'C:\Program Files\R\R-3.6.3\bin\Rscript'
    command = '/usr/bin/Rscript'
    path2script = os.getcwd() + '/database_interpolation.R'

    #Build process command
    cmd = [command,'--vanilla', path2script] + arg

    #check_output will run to the command and store result
    subprocess.call(cmd)
    #print(x)

# interpolacao("casos confirmados/covid19_05-03.csv", "casos confirmados/covid19_06-03.csv",
#              "casos confirmados/covid19_07-03.csv", "casos confirmados/covid19_08-03.csv")

# print("aaa")
def main():
    pasta = './casos confirmados'            
    caminhos = [os.path.join(pasta, nome) for nome in os.listdir(pasta)]
    arquivos = [arq for arq in caminhos if os.path.isfile(arq)]
    arquivos.sort()
    for index in range(3,len(arquivos)):
        # print("aaas")
        interpolacao(arquivos[index-3],arquivos[index-2],arquivos[index-1],arquivos[index])