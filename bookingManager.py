import numpy as np
import REE_API
import os
import requests 
import json
import ast
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt 
from datetime import date, datetime, timedelta

"""
    This file contains all the functions to deal with the schedule of the sauna
"""

def handle_response_code(response):
    status = response.status_code
    # Check the status code
    if status < 200:
        print('informational')
        # If the status code is 200, treat the information.
    elif status >= 200 and status < 300:
        print('Connection is established')
        # okBehavior(response) # runs the function to get list of archives
    elif status >= 300 and status < 400:
        print('redirection')
    elif status >= 400 and status < 500:
        print('client error')
    else:
        print('server error')

def init_matrix():
    # Initialize an empty list
    daily_schedule = []
    
    if int(str(datetime.now()).split(' ')[1].split(':')[0]) < 17:
        date_ = (date.today()).strftime("%Y-%m-%d")
    else:
        date_ = (date.today() + timedelta(days=1)).strftime("%Y-%m-%d")
    
    prices = REE_API.get_real_price_tomorrow()
    
    # Create 24 dictionaries and append them to the list
    for i in range(24):
        if (i > 6) and (i < 21):
            daily_schedule.append({"price": prices[i], "emissions": 0, "booked": 0, "client": '', "mode": ''})
        else:
            daily_schedule.append({"price": prices[i], "emissions": 0, "booked": -1, "client": '', "mode": ''})

    # Checks if there is a bookings file already
    if os.path.exists('bookings_file.txt'):
        # Check if the file is empty
        if os.path.getsize('bookings_file.txt') > 0:
            # If not empty, read data
            return loads_matrix()
        else:
            # If empty, write data
            with open('bookings_file.txt', 'w') as f:
                f.write(date_ + "\n")
                # Write each dictionary to the file on a new line
                for hour in daily_schedule:
                    f.write(str(hour) + '\n')
            
            return daily_schedule
    else:
        # If there is no file, create and write it
        with open('bookings_file.txt', 'w') as f:
            f.write(date_ + "\n")
            # Write each dictionary to the file on a new line
            for hour in daily_schedule:
                f.write(str(hour) + '\n')
                
        return daily_schedule
        
def loads_matrix():
    daily_schedule = []
    # Open file and store schedule 
    with open('bookings_file.txt', 'r') as f:
        content = f.read()
    
    for i, row in enumerate(content.splitlines()):
        if i != 0:
            daily_schedule.append(ast.literal_eval(row))
    
    # return the schedule contained in bookings_file.txt  
    return daily_schedule
    
def creates_booking(schedule, username, hour, mode):
    
    """ 
    Function creates new booking with username, hour and desired mode and updates schedule and 
    bookings_file.txt
    """
    
    schedule[hour]["client"] = username
    schedule[hour]["booked"] = 1
    schedule[hour]["mode"] = mode
    
    updates_file(schedule)
    
    return schedule

def cancel_booking(hour, schedule):
    
    """ 
    Function deletes a booking based on the hour and updates schedule and bookings_file.txt
    """
    
    schedule[hour]["client"] = ''
    schedule[hour]["booked"] = 0
    schedule[hour]["mode"] = ''
    
    updates_file(schedule)
    
    return schedule

def updates_file(schedule):
    """
    Function overwrites bookings_file.txt with the updated schedule received as argument
    """
    with open('bookings_file.txt', 'w') as f:
        f.write(datetime.now().strftime("%Y-%m-%d") + "\n")
        # Write each dictionary to the file on a new line
        for hour in schedule:
            f.write(str(hour) + '\n')

  