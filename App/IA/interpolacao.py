import subprocess
import os
# import casospordia
def interpolacao(day1, day2, day3, day4, state, shapefile):
    # run data_interpolation.R
    arg = [day1, day2, day3, day4, state, shapefile]

    # # Define command and arguments
    # command = r'C:\Program Files\R\R-3.6.3\bin\Rscript'
    # #command = '/usr/bin/Rscript'
    # path2script = os.getcwd() + '/interpolation.R'

    command = '/usr/bin/Rscript'
    path2script = os.getcwd() + '/interpolation.R'

    #Build process command
    cmd = [command, '--vanilla', path2script] + arg

    #check_output will run to the command and store result
    subprocess.call(cmd)


#interpolacao("casos confirmados PE/covid19_18-04.csv", "casos confirmados PE/covid19_19-04.csv", "casos confirmados PE/covid19_20-04.csv", "casos confirmados PE/covid19_21-04.csv")
def main():
    #casospordia.main()
    shapefiles = ['PE.shp', 'BR.shp']
    for shapes in range(0, len(shapefiles)):
        
        state = shapefiles[shapes].split(".")
        shapefiles_path = os.getcwd() + '/shapefiles' + "/" + shapefiles[shapes]
        pasta = os.getcwd() + '/casos confirmados ' + state[0]
        caminhos = [os.path.join(pasta, nome) for nome in os.listdir(pasta)]
        arquivos = [arq for arq in caminhos if os.path.isfile(arq)]
        arquivos.sort()
        print('passei aqui')
        print(len(arquivos))
        for index in range(3, len(arquivos)):
            interpolacao(arquivos[index-3], arquivos[index-2], arquivos[index-1], arquivos[index], state[0], shapefiles_path)
