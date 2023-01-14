import time 
import bookingManager as BM # supporting functions to handle the 
from datetime import date, datetime, timedelta
import numpy as np 
import pandas as pd  
import streamlit as st  # data web app development
from PIL import Image

def schedule_to_df(schedule):

    """Function saves the schedule in DataFrame data structure""" 
    df_overview = pd.DataFrame()
    times = list(range(0, 24))
    availability = list(range(0, 24))
    prices = list(range(0, 24))
    emissions = list(range(0, 24))

    for i, hour in enumerate(times):
        if hour < 12:
            times[i] = str(hour) + ' AM'
            prices[i] = int(schedule[i]['price'])
            emissions[i] = int(schedule[i]['emissions'])
            if schedule[i]['booked'] == 1:
                if schedule[i]['mode'] == 'Eco':
                    availability[i] = 'Booked by ' + str(schedule[i]['client']) + ' in Eco Mode'
                elif schedule[i]['mode'] == 'Regular 50':
                    availability[i] = 'Booked by ' + str(schedule[i]['client']) + ' in Regular 50 Mode'
                else:
                    availability[i] = 'Booked by ' + str(schedule[i]['client']) + ' in Regular 47 Mode'
            elif schedule[i]['booked'] == 0:
                availability[i] = 'No Bookings'
            else:
                availability[i] = 'Closed'
        elif hour == 12:
            times[i] = str(hour) + ' PM'
            prices[i] = int(schedule[i]['price'])
            emissions[i] = int(schedule[i]['emissions'])
            if schedule[i]['booked'] == 1:
                if schedule[i]['mode'] == 'Eco':
                    availability[i] = 'Booked by ' + str(schedule[i]['client']) + ' in Eco Mode'
                elif schedule[i]['mode'] == 'Regular 50':
                    availability[i] = 'Booked by ' + str(schedule[i]['client']) + ' in Regular 50 Mode'
                else:
                    availability[i] = 'Booked by ' + str(schedule[i]['client']) + ' in Regular 47 Mode'
            elif schedule[i]['booked'] == 0:
                availability[i] = 'No Bookings'
            else:
                availability[i] = 'Closed'
        else:
            times[i] = str(hour-12) + ' PM'
            prices[i] = int(schedule[i]['price'])
            emissions[i] = int(schedule[i]['emissions'])
            if schedule[i]['booked'] == 1:
                if schedule[i]['mode'] == 'Eco':
                    availability[i] = 'Booked by ' + str(schedule[i]['client']) + ' in Eco Mode'
                elif schedule[i]['mode'] == 'Regular 50':
                    availability[i] = 'Booked by ' + str(schedule[i]['client']) + ' in Regular 50 Mode'
                else:
                    availability[i] = 'Booked by ' + str(schedule[i]['client']) + ' in Regular 47 Mode'
            elif schedule[i]['booked'] == 0:
                availability[i] = 'No Bookings'
            else:
                availability[i] = 'Closed'
    
    df_overview['Time'] = times
    df_overview['Availability'] = availability
    df_overview['Price [€/MWh]'] = prices
    df_overview['Estimated Emissions [ton/MWh]'] = emissions

    return df_overview

st.set_page_config(
    page_title="Sauna Dashboard",
    page_icon="✅",
    layout="wide",
)

@st.experimental_memo
def get_data() -> pd.DataFrame:
    """Function that reads the dataset"""
    return pd.read_csv(dataset_path)

# import a sauna image for the dashboard
image = Image.open('sauna.jpg')

# import dataset with sauna operation data
dataset_path = "dataset.csv"

# show image in the dashboard
st.image(image)

# Dashboard title and intro
st.title("Welcome to your Smart Steam Sauna Dashboard")
st.subheader('Here you can find valuable real-time information about your Sauna')

# import dataset and perform some data manipulation
df = get_data()

df['TimeStamp'] = pd.to_datetime(df['TimeStamp'])
df['timediff'] = df['TimeStamp'].diff().dt.total_seconds()

df['Energy consumed'] = df['Power_W']*df['ON/OFF']*df['timediff']

# load schedule from bookings_file.txt
schedule = BM.loads_matrix()
schedule_df = schedule_to_df(schedule)

# show schedule on the Dashboard
st.subheader("1) Today's Schedule:")

col1, col2 = st.columns(2)

with col1:
    st.markdown("Morning")
    st.table(schedule_df[schedule_df.index < 12])
with col2:
    st.markdown("Afternoon")
    st.table(schedule_df[schedule_df.index >= 12])

# creating a single-element container
placeholder = st.empty()

# near real-time / live feed simulation
for seconds in range(len(df)):

    with placeholder.container():
        
        st.subheader('2) On the first tab you will find operational conditions, on the second tab you will find an economic overview')
        
        # generate three tabs to separate type of information shown
        tab1, tab2 = st.tabs(["Operations", "Economic"])
        
        # first tab shows the operation indicators
        with tab1:
            
            kpi11, kpi12, kpi13, kpi14 = st.columns(4)

            if df["ON/OFF"][seconds] == 1:
                value11 = 'ON'
            elif df["ON/OFF"][seconds] == 0:
                value11 = 'OFF'

            # show state of relay controller for current
            kpi11.metric(
                label="🧖🏻 Sauna State",
                value=value11,
            )
            
            value12 = float(df["Power_W"][seconds]*df["ON/OFF"][seconds])

            if seconds > 0:
                delta = float(df["Power_W"][seconds]*df["ON/OFF"][seconds]-df["Power_W"][seconds-1]*df["ON/OFF"][seconds-1])
            else:
                delta = 0
            
            # show current power consumption
            kpi12.metric(
                label="⚡ Power Consumption",
                value=str(value12) + ' kW',
                delta=delta,
            )
            
            if seconds > 0:
                delta = float(df["Sauna Temperature"][seconds]-df["Sauna Temperature"][seconds-1])
            else:
                delta = 0
            
            # show current sauna temperature
            value13 = float(df["Sauna Temperature"][seconds])

            kpi13.metric(
                label="🌡️ Sauna Temperature",
                value=str(value13) + ' °C',
                delta=delta,
            )

            if seconds > 0:
                delta = float(df["Steam"][seconds]-df["Steam"][seconds-1])
            else:
                delta = 0

            value14 = int(df["Steam"][seconds])

            # show current steam percentage
            kpi14.metric(
                label="💨 Steam",
                value=str(value14) + ' %',
                delta=delta,
            )

            # chart displays historical temperature and steam %
            chart_data = pd.DataFrame(
                df[df.index < seconds][["Sauna Temperature", "Steam"]].to_numpy(),
                columns=['Sauna Temperature (°C)', 'Steam (%)'])

            st.line_chart(chart_data)
        
        # second tab shows the economic/financial indicators
        with tab2:

            kpi21, kpi22 = st.columns(2)
            
            value21 = int(schedule_df['Price [€/MWh]'][int(str(datetime.now()).split(' ')[1].split(':')[0])])
            
            # show current electricity price
            kpi21.metric(
                label="🏷️ Current Electricity Price",
                value=str(value21) + ' €/MWh',
            )
            
            value21 = int(schedule_df['Estimated Emissions [ton/MWh]'][int(str(datetime.now()).split(' ')[1].split(':')[0])])
            
            # show current electricity generation emissions
            kpi21.metric(
                label="🌫️ Estimated Emissions associated with Electricity generation",
                value=str(value21) + ' ton/MWh',
            )

            df_cost = df[df.index < seconds]
            value22 = float((df_cost['Cost']*df_cost['ON/OFF']).sum())

            # show accumulated energy costs associated with the sauna operation
            kpi22.metric(
                label="💰 Cost since beginning of day",
                value=(str(value22) + ' €'),
            )

            value22 = float(df[df.index < seconds]['Energy consumed'].sum()/3600/1000)

            # show accumulated energy consumed associated with the sauna operation
            kpi22.metric(
                label="⚡ Total Energy consumed since beginning of day",
                value=(str(value22) + ' kWh'),
            )
        
        # implementation of the data update every second
        time.sleep(1)