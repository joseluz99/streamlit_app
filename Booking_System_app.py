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
            # strores username on username.txt
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

# schedule is imported from bookings_file.txt and stored in a variable
schedule = BM.init_matrix()
booking = [None] * 24

# if the login is successful, the dashboard is shown
if check_password():
    
    # import the logged in username from username.txt
    with open('username.txt', 'r') as f:
        username = str(f.read()).split('\n')[0]
    
    # show introductory message welcoming user
    st.markdown('Hello, ' + username)
    st.markdown('Welcome to the Booking Management site of our smart sustainable sauna\n') 
    
    # create 3 tabs to display the different information
    tab1, tab2, tab3 = st.tabs(["Overview", "Economic Options", "Sustainable Options"])
    
    # creating 3 dataframes, one for each tab to be displayed
    df_overview = pd.DataFrame()
    df_economic = pd.DataFrame()
    df_sustainable = pd.DataFrame()
    
    times = list(range(0, 24))
    availability = list(range(0, 24))
    prices = list(range(0, 24))
    emissions = list(range(0, 24))
    display_times_book = []
    display_times_unbook = []
    
    # populating the dataframe with information from the schedule (this should have been implemented as a function like in the dashboard
    # but there was no time to effectivate the change)
    for i, hour in enumerate(times):
        if hour < 12:
            times[i] = str(hour) + ' AM'
            prices[i] = int(schedule[i]['price'])
            emissions[i] = int(schedule[i]['emissions'])
            if schedule[i]['booked'] == 1:
                if schedule[i]['client'] == str(username):
                    display_times_unbook.append(times[i])
                    if schedule[i]['mode'] == 'Eco':
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
                    if schedule[i]['mode'] == 'Eco':
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
                    if schedule[i]['mode'] == 'Eco':
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
        
        # first tab shows an overview of the schedule, with all the hours and if they are available for booking or not
        # additionally it shows the hourly electricity price and emissions associated with the electricity generation
        st.markdown('Here is an overview of the booking schedule for tomorrow: \n') 
        
        col1, col2 = st.columns(2)

        with col1:
            # show the morning half
            st.table(df_overview[df_overview.index < 12])
        with col2:
            # show the afternoon half
            st.table(df_overview[df_overview.index >= 12])
    
    with tab2:
        # second tab shows an overview of the schedule, with all the hours and if they are available for booking or not
        # but only the hours that have a price below the daily average will be shown
        st.markdown('In this tab, we suggest you the hours which have the lowest fares for you as a user. \n') 
        st.markdown('Given our pay-per-use tariff model, here are the hours in which the electricity price is below the daily average:\n') 
        
        col1, col2 = st.columns(2)

        with col1:
            # show the morning half
            st.table(df_economic[df_economic.index < 12])
        with col2:
            # show the afternoon half
            st.table(df_economic[df_economic.index >= 12])
    
    with tab3:
        
        # third tab shows an overview of the schedule, with all the hours and if they are available for booking or not
        # but only the hours that have emissions below the daily average will be shown
        st.markdown('In this tab, we suggest you the hours which have the least emissions. \n') 
        st.markdown('Here are the hours in which the emissions from electricity generation are below the daily average:\n') 

        col1, col2 = st.columns(2)

        with col1:
            # show the morning half
            st.table(df_sustainable[df_sustainable.index < 12])
        with col2:
            # show the afternoon half
            st.table(df_sustainable[df_sustainable.index >= 12])
    
    # multiselect where user can choose which hours to book for using the sauna
    book_options = st.multiselect('Choose the hours you wish to book', display_times_book)
    mode = st.selectbox('Choose the mode you wish to book', ('Eco', 'Regular'))    
    
    # in case the user has booked slots, multiselect where user can choose which hours to unbook
    if len(display_times_unbook) != 0:
        unbook_options = st.multiselect('Choose the hours you wish to unbook', display_times_unbook)
    
    # only upon confirmation the changes are effective
    if (st.button('Confirm')):
        
        # create bookings and store them into the bookings_file.txt
        if len(book_options) != 0:
            for hour in book_options:
                hour_input = hour.split(' ')[1]
                if 'AM' in hour_input:
                    schedule = BM.creates_booking(schedule, username, int(hour.split(' ')[0]), mode)
                else:
                    schedule = BM.creates_booking(schedule, username, int(hour.split(' ')[0])+12, mode)
        
        # deletes bookings from the schedule and bookings_file.txt
        if len(display_times_unbook) != 0:
            for hour in unbook_options:
                hour_input = hour.split(' ')[1]
                if 'AM' in hour_input:
                    schedule = BM.cancel_booking(int(hour.split(' ')[0]), schedule)
                else:
                    schedule = BM.cancel_booking(int(hour.split(' ')[0])+12, schedule)
        
        # confirmation message. the only way to update the schedule in streamlit is by refreshing the page
        st.write('Bookings confirmed. Please refresh your page.')
        