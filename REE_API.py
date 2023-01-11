# import requests library
import requests
import json
# import plotting library
#import matplotlib
#import matplotlib.pyplot as plt
from datetime import date, datetime, timedelta

def get_real_price_tomorrow():
    # datetime object containing current date and time
    tomorrow = date.today() + timedelta(days=1)
    # Time formate for REE API
    dt_string_start = str(tomorrow.year) + str(tomorrow.month) + str(tomorrow.day) + 'T00:00'
    dt_string_end = str(tomorrow.year) + str(tomorrow.month) + str(tomorrow.day) + 'T23:00'

    endpoint = 'https://apidatos.ree.es'
    get_archives = '/en/datos/mercados/precios-mercados-tiempo-real'
    headers = {'Accept': 'application/json',
                'Content-Type': 'application/json',
                'Host': 'apidatos.ree.es'}
    params = {'start_date': dt_string_start, 'end_date': dt_string_end, 'time_trunc': 'hour'}
    #params = {'start_date': dt_string_start, 'time_trunc': 'hour'}

    response = requests.get(endpoint + get_archives, headers=headers, params=params)

    values = response.json()

    values['data']
    prices = []

    for value in values['included'][0]['attributes']['values']:
        prices.append(value['value'])

    return prices

