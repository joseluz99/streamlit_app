import requests
import json
from datetime import date, datetime, timedelta

def get_real_price_tomorrow():
    
    """
    Function retrieves day-ahead prices for electricity if called after 5PM
    Before 5PM it retrieves today's electricity prices
    """
    
    if int(str(datetime.now()).split(' ')[1].split(':')[0]) < 17:
        tomorrow = date.today()
    else:
        tomorrow = date.today() + timedelta(days=1)
        
    # Time structure for REE API
    dt_string_start = str(tomorrow.year) + str(tomorrow.month) + str(tomorrow.day) + 'T00:00'
    dt_string_end = str(tomorrow.year) + str(tomorrow.month) + str(tomorrow.day) + 'T23:00'

    endpoint = 'https://apidatos.ree.es'
    get_archives = '/en/datos/mercados/precios-mercados-tiempo-real'
    headers = {'Accept': 'application/json',
                'Content-Type': 'application/json',
                'Host': 'apidatos.ree.es'}
    params = {'start_date': dt_string_start, 'end_date': dt_string_end, 'time_trunc': 'hour'}

    # calling the API
    response = requests.get(endpoint + get_archives, headers=headers, params=params)

    values = response.json()

    values['data']
    prices = []

    for value in values['included'][0]['attributes']['values']:
        prices.append(value['value'])

    # return array with 24 entries with price for each hour of the day
    return prices