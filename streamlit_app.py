# To run dashboard type 'streamlit run streamlit_app.py' on the console, inside the virtual environment
# created to host the project

import streamlit as st
from collections import namedtuple
from datetime import datetime, timedelta
import requests
import math
import matplotlib.pyplot as plt 
import seaborn as sb
import pandas as pd
import numpy as np
import plost                # package is used to create plots/charts within streamlit
from PIL import Image       # package is used to put images within streamlit

from api_connection import get_data_from_api       

# Page setting
st.set_page_config(layout="wide")

with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

### Here starts the web app design

# Introductory presentation

st.title('Welcome to your favorite Dashboard')
st.subheader('Here you can find a lot of stats about the electricity generation in the Spanish grid.')
st.subheader('Lets accelerate the energy transition together by sharing information!')

# First component: two tabs with donut charts. One of them shows the electricity mix in the Spanish Grid;
# the other one shows the carbon emissions related to that electricity by source

tab1, tab2 = st.tabs(["Sources", "Emissions"])

with tab1:
    
    # Get raw data from API
    
    response = get_data_from_api('sources')

    # Retrieve electricity generation sources from the raw data
    
    gen_type = []
    gen_MWh = []
    for gen_t in response['included']:
        if gen_t['type'] == 'Total generation':
            total_generation_MWh = gen_t['attributes']['values'][0]['value']
        else:
            gen_type.append(gen_t['type'])
            gen_MWh.append(gen_t['attributes']['values'][0]['value'])

    df = pd.DataFrame()

    df['gen_type'] = gen_type
    df['gen_MWh'] = gen_MWh
    
    # Create the donut chart with the data
    
    st.markdown('Spanish Electricity Mix (' + str(datetime.now().year) + '/' + str(datetime.now().month) + '/' + str(datetime.now().day-1) + ')')
    plost.donut_chart(                      
            data=df,
            theta='gen_MWh',
            color='gen_type')

with tab2:
    
    # Get raw data from API
    
    response = get_data_from_api('emissions')

    # Retrieve carbon emissions from the raw data
    
    gen_type = []
    emissions_value = []
    for instance in response['included']:
        if instance['type'] == 'tCO2 eq./MWh' or instance['type'] == 'Total tCO2 eq.':
            continue
        else:
            gen_type.append(instance['type'])
            emissions_value.append(instance['attributes']['values'][0]['value'])

    df = pd.DataFrame()

    df['gen_type'] = gen_type
    df['emissions_value'] = emissions_value
    
    # Create the donut chart with the data
    
    st.markdown('Spanish Electricity Mix Emissions (' + str(datetime.now().year) + '/' + str(datetime.now().month) + '/' + str(datetime.now().day-1) + ')')
    plost.donut_chart(                      # donut charts
            data=df,
            theta='emissions_value',
            color='gen_type')

### Second component: A heatmap that shows the emissions in the Spanish Grid for the last year.
### The shade/color is given by the scaling of the emissions in ton

# Get raw data from API

response = get_data_from_api('emissions year')

# Retrieve carbon emissions for 365 days from the raw data

day_year = []
day_emissions = []
for types in response['included']:
    if types['type'] == 'Total tCO2 eq.':
        for i, daily_data in enumerate(types['attributes']['values']):
            day_year.append(daily_data['datetime'].split('T')[0])
            day_emissions.append(float(daily_data['value']))

df_year_emissions = pd.DataFrame()
df_year_emissions['day_year'] = day_year
df_year_emissions['day_emissions'] = day_emissions

# Create the Heatmap with the data

st.markdown('Emissions Heatmap (' + str(datetime.now().year-1) + '/' + str(datetime.now().month) + '/' + str(datetime.now().day) + ' to ' +  str(datetime.now().year) + '/' + str(datetime.now().month) + '/' + str(datetime.now().day-1) + ')')             # text is created with markdown
plost.time_hist(                        # histogram
data=df_year_emissions,
date='day_year',
x_unit='week',
y_unit='day',
color='day_emissions',
aggregate='mean',
legend=None)

### Third component: scatterplot with the price of electricity against share of renewables in the grid
### to get a sense of the influence (positive or negative) of the use of these technologies in the PVPC
### price (price consumers are charged)

# Get raw data from API (renewables share)

response = get_data_from_api('renewable share')

# Retrieve renewables share from the raw data
# Renewable share is retrieved daily (only option from the API for this indicator)
# The period considered is 2 months prior to the current date

share_ren = [0 for _ in range(len(response['included'][0]['attributes']['values']))]
for types in response['included']:
    if types['attributes']['type'] == 'Renovable':
        for i in range(len(types['attributes']['values'])):
            #print(i, types['type'], types['attributes']['values'][i]['datetime'])
            share_ren[i] = share_ren[i] + float(types['attributes']['values'][i]['percentage'])

# Loop that retrives the prices for the period considered
# Computation time is a challenge because renewable shares are retrieved daily (limitation due to API)
# although prices can only be retrieved hourly. Therefore, an average daily price must be computed and
# the computation time is considerable. This means that the last component of the dashboard will appear 
# between 0 and 60 seconds after the other 2.

daily_average_price = []
for i in range(len(share_ren)):
    current_date = datetime.now() - timedelta(days=i)
    day_before = datetime.now() - timedelta(days=i+1)

    start_date = str(day_before.year) + '-' + str(day_before.month) + '-' + str(day_before.day) + 'T00:00'
    end_date = str(current_date.year) + '-' + str(current_date.month) + '-' + str(current_date.day-1) + 'T23:00'


    url = 'https://apidatos.ree.es/en/datos/mercados/precios-mercados-tiempo-real'
    headers = {'Accept': 'application/json',
               'Content-Type': 'application/json',
               'Host': 'apidatos.ree.es'}
    params = {'start_date': start_date, 'end_date': end_date, 'time_trunc':'hour'}

    response = requests.get(url, headers=headers, params=params)
    outputs = response.json()

    avg = []

    for j in range(len(outputs['included'][0]['attributes']['values'])):
        avg.append(outputs['included'][0]['attributes']['values'][j]['value'])
    
    daily_average_price.append(sum(avg) / len(avg))
    #print(outputs['included'][0]['attributes']['values'][j]['datetime'].split('T')[0], sum(avg),len(avg))
    avg.clear()
    
prices_share_df = pd.DataFrame()
prices_share_df['daily_average_price'] = daily_average_price
prices_share_df['share_ren'] = share_ren

# Create the Scatterplot with the PVPC (€) and share of renewables

st.markdown('Relationship between PVPC prices and the share of Renewables in the grid')
st.vega_lite_chart(prices_share_df, {
    'mark': {'type': 'circle', 'tooltip': True},
    'encoding': {
        'x': {'field': 'share_ren', 'type': 'quantitative'},
        'y': {'field': 'daily_average_price', 'type': 'quantitative'},
    },
    },
                   use_container_width=True)

# Interpolation to summarize the impact of increased renewables share in the grid
# Possible improvement is showing the tendency line in the chart, which unfortunately 
# is still not possible using the plost library.

z = np.polyfit(share_ren, daily_average_price, 1)
p = np.poly1d(z)

if p[1] > 0:
    st.text('The chart above shows the relationship between the share of renewables in the Spanish Electricity Grid and the Consumers price.')
    st.text('It shows that for each 10' + '% ' + 'of additional renewables in the grid, the price rises ' + str(int(abs(p[1]/10))) + '€ per MWh')
elif p[1] < 0:
    st.text('The chart above shows the relationship between the share of renewables in the Spanish Electricity Grid and the Consumers price.')
    st.text('It shows that for each 10' + '% ' + 'of additional renewables in the grid, the price drops ' + str(int(abs(p[1]/10))) + '€ per MWh')

### End of the dashboard. New components might (and will) be added below...