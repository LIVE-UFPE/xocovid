import pandas as pd
import numpy as np
from datetime import timedelta
import os

def date_array(dataframe):
    start_date = dataframe['date'].min().to_pydatetime()
    end_date = dataframe['date'].max().to_pydatetime()
    end_date = end_date + timedelta(days=1)
    array_dates = np.arange(start_date, end_date, dtype='datetime64[D]')
    return array_dates

def main(data):

    # loading the csv file
    cases_per_state = pd.read_csv(os.path.join(os.path.dirname(__file__))+'/dados/Casos por Estado '+ data +'.csv', delimiter=',',index_col = 0)
    cases_per_state['date'] = pd.to_datetime(cases_per_state['date'])

    # sorting dataset by date
    cases_per_state['date'] = pd.to_datetime(cases_per_state['date'])
    cases_per_state = cases_per_state.sort_values(by=['date'])

    cases_per_state = cases_per_state[['date','state','confirmed','deaths']]

    #casesPE = casesPE[casesPE['city'] != 'Importados/Indefinidos']
    states = cases_per_state['state'].unique()

    for state in states:
        temp = cases_per_state[cases_per_state['state'] == state]
        dates_for_timeserie = date_array(temp)
        confirmed_cases = len(dates_for_timeserie) * [0]
        deaths_cases = len(dates_for_timeserie) * [0]
        notification_dates_array = temp['date'].values.astype('datetime64[D]')  # datas dos casos confirmados
        array_index = 0
        for day in dates_for_timeserie:
            if day in notification_dates_array:
                idx = temp[temp['date'] == day].index
                confirmed_cases[array_index] = temp['confirmed'][idx[0]]
                deaths_cases[array_index] = temp['deaths'][idx[0]]
                array_index = array_index + 1
            else:
                confirmed_cases[array_index] = confirmed_cases[array_index - 1]
                deaths_cases[array_index] = deaths_cases[array_index - 1]
                array_index = array_index + 1
        confirmed_cases_dataframe = pd.DataFrame({'dt_notificacao':dates_for_timeserie, 'acumulado_confirmados':confirmed_cases})
        confirmed_cases_dataframe.to_csv(os.path.join(os.path.dirname(__file__))+"/dados/confirmados/" + data + state + ".csv", index=False)
        deaths_cases_dataframe = pd.DataFrame({'dt_notificacao': dates_for_timeserie,'acumulado_mortes':deaths_cases})
        deaths_cases_dataframe.to_csv(os.path.join(os.path.dirname(__file__))+"/dados/mortes/" + data + state + ".csv", index=False)
        array_index = 0


