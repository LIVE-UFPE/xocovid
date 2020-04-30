import subprocess
import os
import App.predicao_arima.cumulativeSum as cumulativeSum

def arimaForecast(predictionFile):
    # run ARIMA_prediction.R
    arg = [predictionFile]

    # Define command and arguments
    command = '/usr/bin/Rscript'
    # command = r'C:\Program Files\R\R-3.6.3\bin\Rscript'
    path2script = os.getcwd() + '/arima.R'

    #Build process command
    cmd = [command, '--vanilla', path2script] + arg

    #check_output will run to the command and store result
    print(cmd)
    subprocess.call(cmd)
    
def main():
    cumulativeSum.main()
    arimaForecast('./baseARIMA_2020-04-12.csv')

#main()