import subprocess
import os
import App.predicao_arima.cumulativeSum



def arimaForecast(predictionFile,estado):
    # run ARIMA_prediction.R
    arg = [predictionFile,estado]

    # Define command and arguments
    command = '/usr/bin/Rscript'
    # command = r'C:\Program Files\R\R-3.6.3\bin\Rscript'
    path2script = os.getcwd() + '/arima.R'

    #Build process command
    cmd = [command, '--vanilla', path2script] + arg

    #check_output will run to the command and store result
    print(cmd)
    subprocess.call(cmd)
    
def main(estado):
    arimaForecast(os.path.join(os.path.dirname(__file__))+'/baseARIMA.csv',estado)
    

# main()
