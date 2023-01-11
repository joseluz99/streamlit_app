import streamlit as st
import bookingManager as BM
import streamlit_authenticator as stauth
import REE_API as API_data
from collections import namedtuple
import datetime
import math
import pandas as pd
import numpy as np
import plost                # this package is used to create plots/charts within streamlit
from PIL import Image       # this package is used to put images within streamlit

# import requests library
import requests
import json
    
# Page setting
st.set_page_config(layout="wide")

def check_password():
    """Returns `True` if the user had a correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if (
            st.session_state["username"] in st.secrets["passwords"]
            and st.session_state["password"]
            == st.secrets["passwords"][st.session_state["username"]]
        ):
            st.session_state["password_correct"] = True
            with open('username.txt', 'w') as f:
                f.write(st.session_state["username"] + "\n")
            del st.session_state["password"]  # don't store username + password
            del st.session_state["username"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show inputs for username + password.
        st.text_input("Username", on_change=password_entered, key="username")
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        return False
    elif not st.session_state["password_correct"]:
        # Password not correct, show input + error.
        st.text_input("Username", on_change=password_entered, key="username")
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        st.error("😕 User not known or password incorrect")
        return False
    else:
        # Password correct.
        return True

schedule = BM.init_matrix()
booking = [None] * 24

if check_password():
        
    with open('username.txt', 'r') as f:
        username = str(f.read()).split('\n')[0]
    
    st.markdown('Hello, ' + username)
    st.markdown('Welcome to the Booking Management site of our smart sustainable sauna\n') 
    
    tab1, tab2, tab3 = st.tabs(["Overview", "Economic Options", "Sustainable Options"])
    
    df_overview = pd.DataFrame()
    df_economic = pd.DataFrame()
    df_sustainable = pd.DataFrame()
    
    times = list(range(0, 24))
    availability = list(range(0, 24))
    prices = list(range(0, 24))
    emissions = list(range(0, 24))
    display_times_book = []
    display_times_unbook = []
    
    for i, hour in enumerate(times):
        if hour < 12:
            times[i] = str(hour) + ' AM'
            prices[i] = int(schedule[i]['price'])
            emissions[i] = int(schedule[i]['emissions'])
            if schedule[i]['booked'] == 1:
                if schedule[i]['client'] == str(username):
                    display_times_unbook.append(times[i])
                    if schedule[i]['mode'] == 'Economic':
                        availability[i] = 'Booked by you in Economic Mode'
                    elif schedule[i]['mode'] == 'Regular':
                        availability[i] = 'Booked by you in Regular Mode'
                else:
                    availability[i] = 'Booked'
            elif schedule[i]['booked'] == 0:
                availability[i] = 'Free'
                display_times_book.append(times[i])
            else:
                availability[i] = 'Closed'
        elif hour == 12:
            times[i] = str(hour) + ' PM'
            prices[i] = int(schedule[i]['price'])
            emissions[i] = int(schedule[i]['emissions'])
            if schedule[i]['booked'] == 1:
                if schedule[i]['client'] == str(username):
                    display_times_unbook.append(times[i])
                    if schedule[i]['mode'] == 'Economic':
                        availability[i] = 'Booked by you in Economic Mode'
                    elif schedule[i]['mode'] == 'Regular':
                        availability[i] = 'Booked by you in Regular Mode'
                else:
                    availability[i] = 'Booked'
            elif schedule[i]['booked'] == 0:
                availability[i] = 'Free'
                display_times_book.append(times[i])
            else:
                availability[i] = 'Closed'
        else:
            times[i] = str(hour-12) + ' PM'
            prices[i] = int(schedule[i]['price'])
            emissions[i] = int(schedule[i]['emissions'])
            if schedule[i]['booked'] == 1:
                if schedule[i]['client'] == str(username):
                    display_times_unbook.append(times[i])
                    if schedule[i]['mode'] == 'Economic':
                        availability[i] = 'Booked by you in Economic Mode'
                    elif schedule[i]['mode'] == 'Regular':
                        availability[i] = 'Booked by you in Regular Mode'
                else:
                    availability[i] = 'Booked'
            elif schedule[i]['booked'] == 0:
                availability[i] = 'Free'
                display_times_book.append(times[i])
            else:
                availability[i] = 'Closed'
    
    df_overview['Time'] = times
    df_overview['Availability'] = availability
    df_overview['Price [€/MWh]'] = prices
    df_overview['Estimated Emissions [ton/MWh]'] = emissions

    df_economic = df_overview[df_overview['Price [€/MWh]'] < df_overview['Price [€/MWh]'].mean()]
    df_sustainable = df_overview[df_overview['Estimated Emissions [ton/MWh]'] < df_overview['Estimated Emissions [ton/MWh]'].mean()]
     
    with tab1:
        
        st.markdown('Here is an overview of the booking schedule for tomorrow: \n') 
        
        col1, col2 = st.columns(2)

        with col1:
            st.table(df_overview[df_overview.index < 12])
        with col2:
            st.table(df_overview[df_overview.index >= 12])
    
    with tab2:
        
        st.markdown('In this tab, we suggest you the hours which have the lowest fares for you as a user. \n') 
        st.markdown('Given our pay-per-use tariff model, here are the hours in which the electricity price is below the daily average:\n') 
        
        col1, col2 = st.columns(2)

        with col1:
            st.table(df_economic[df_economic.index < 12])
        with col2:
            st.table(df_economic[df_economic.index >= 12])
    
    with tab3:
        
        st.markdown('In this tab, we suggest you the hours which have the least emissions. \n') 
        st.markdown('Here are the hours in which the emissions from electricity generation are below the daily average:\n') 

        col1, col2 = st.columns(2)

        with col1:
            st.table(df_sustainable[df_sustainable.index < 12])
        with col2:
            st.table(df_sustainable[df_sustainable.index >= 12])
    
    modes = ['Economic', 'Regular']
    
    book_options = st.multiselect('Choose the hours you wish to book', display_times_book)
    mode = st.selectbox('Choose the mode you wish to book', ('Economic', 'Regular'))    
    
    if len(display_times_unbook) != 0:
        unbook_options = st.multiselect('Choose the hours you wish to unbook', display_times_unbook)
        
    if (st.button('Confirm')):
        
        if len(book_options) != 0:
            for hour in book_options:
                hour_input = hour.split(' ')[1]
                if 'AM' in hour_input:
                    schedule = BM.creates_booking(schedule, username, int(hour.split(' ')[0]), mode)
                else:
                    schedule = BM.creates_booking(schedule, username, int(hour.split(' ')[0])+12, mode)
        
        if len(display_times_unbook) != 0:
            for hour in unbook_options:
                hour_input = hour.split(' ')[1]
                if 'AM' in hour_input:
                    schedule = BM.cancel_booking(int(hour.split(' ')[0]), schedule)
                else:
                    schedule = BM.cancel_booking(int(hour.split(' ')[0])+12, schedule)
        
        st.write('Bookings confirmed. Please refresh your page.')
        