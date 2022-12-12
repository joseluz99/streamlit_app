""" This script store the function required to stream data from the API of your choice"""

import requests
import json
import pandas as pd
import numpy as np
from datetime import datetime

# create different GET requests to support dashboard

def get_data_from_api(switch):
    
   current_date = datetime.now()
    
   # Option emissions gets raw data from the REE API regarding emissions for the desired time period,
   # set to 1 day and starting on the day previous to the current day
    
   if switch == 'emissions':
      option = 'generacion/no-renovables-detalle-emisiones-CO2'
      start_date = str(current_date.year) + '-' + str(current_date.month) + '-' + str(current_date.day-1) + 'T00:00'
      end_date = str(current_date.year) + '-' + str(current_date.month) + '-' + str(current_date.day-1) + 'T23:00'
      params = {'start_date': start_date, 'end_date': end_date, 'time_trunc':'month'}
   
   # Option emissions year gets raw data from the REE API regarding emissions for the desired time period,
   # set to 1 year and starting on the day previous to the current day
   
   elif switch == 'emissions year':
      option = 'generacion/no-renovables-detalle-emisiones-CO2'
      start_date = str(current_date.year-1) + '-' + str(current_date.month) + '-' + str(current_date.day) + 'T00:00'
      end_date = str(current_date.year) + '-' + str(current_date.month) + '-' + str(current_date.day-1) + 'T23:00'
      params = {'start_date': start_date, 'end_date': end_date, 'time_trunc':'day'}
   
   # Option renewable share gets raw data from the REE API regarding the share of each generation source
   # (both renewable and non-renewable) for the desired time period, set to 2 months and starting on 
   # the day previous to the current day
   
   elif switch == 'renewable share':
      option = 'generacion/evolucion-renovable-no-renovable'
      start_date = str(current_date.year) + '-' + str(current_date.month-2) + '-' + str(current_date.day) + 'T00:00'
      end_date = str(current_date.year) + '-' + str(current_date.month) + '-' + str(current_date.day-1) + 'T23:00'
      params = {'start_date': start_date, 'end_date': end_date, 'time_trunc':'day'}
   
   # Option sources gets raw data from the REE API regarding the electricity generation mix
   # for the desired time period, set to 2 months and starting on the day previous to the current day
   
   elif switch == 'sources':
      option = 'generacion/estructura-generacion'
      start_date = str(current_date.year) + '-' + str(current_date.month) + '-' + str(current_date.day-1) + 'T00:00'
      end_date = str(current_date.year) + '-' + str(current_date.month) + '-' + str(current_date.day-1) + 'T23:00'
      params = {'start_date': start_date, 'end_date': end_date, 'time_trunc':'month'}
   
   # Option PVPC prices gets raw data from the REE API regarding the consumer prices
   # for the desired time period, set to 1 day and starting on the day previous to the current day
   # This option will be used on a loop to retrieve prices for longer periods
   
   elif switch == 'PVPC prices':
      option = 'mercados/precios-mercados-tiempo-real'
      start_date = str(current_date.year) + '-' + str(current_date.month) + '-' + str(current_date.day-1) + 'T00:00'
      end_date = str(current_date.year) + '-' + str(current_date.month) + '-' + str(current_date.day-1) + 'T23:00'
      params = {'start_date': start_date, 'end_date': end_date, 'time_trunc':'month'}
   

   url = 'https://apidatos.ree.es/en/datos/' + option
   headers = {'Accept': 'application/json',
         'Content-Type': 'application/json',
         'Host': 'apidatos.ree.es'}

   # Perform request to the API
   
   response = requests.get(url, headers=headers, params=params)
   outputs = response.json()

   return outputs


