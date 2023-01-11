import numpy as np
import REE_API
import os
import seaborn as sb
import requests 
import json
import ast
import plost
import pandas as pd
# import plotting library
import matplotlib
import matplotlib.pyplot as plt 
from datetime import date, datetime, timedelta

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

def get_real_price_day ():
    # datetime object containing current date and time
    
    now = datetime.now()

    # Time formate for REE API
    nowZero = now - timedelta(hours=now.hour)
    dt_string_start = nowZero.strftime("%Y/%m/%dT%00:00")
    endhour = nowZero + timedelta(hours=23)
    dt_string_end = endhour.strftime("%Y/%m/%dT%H:00")
    #print("date and time =", dt_string)

    endpoint = 'https://apidatos.ree.es'
    get_archives = '/en/datos/mercados/precios-mercados-tiempo-real'
    headers = {'Accept': 'application/json',
               'Content-Type': 'application/json',
               'Host': 'apidatos.ree.es'}
    params = {'start_date': dt_string_start, 'end_date': dt_string_end, 'time_trunc': 'hour'}

    response = requests.get(endpoint + get_archives, headers=headers, params=params)

    handle_response_code(response)

    json = response.json()

    spot_market_prices = json['included'][0]
    values = spot_market_prices['attributes']['values']

    for t in values:
        t['datetime'] = datetime.fromisoformat(t['datetime'])

    #print(values)
    return values

def init_matrix():
    # Initialize an empty list
    daily_schedule = []
    
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
    # Open file and create data structure to store it
    with open('bookings_file.txt', 'r') as f:
        content = f.read()
    
    for i, row in enumerate(content.splitlines()):
        if i != 0:
            daily_schedule.append(ast.literal_eval(row))
            
    return daily_schedule

def checks_availability(schedule):
    
    available_hours = []
    
    for i in range(len(schedule)):
        
        if schedule[i]["booked"] == 0:
            available_hours.append(i)
    
    return available_hours
    
def creates_booking(schedule, username, hour, mode):
    
    schedule[hour]["client"] = username
    schedule[hour]["booked"] = 1
    schedule[hour]["mode"] = mode
    
    updates_file(schedule)
    
    return schedule

def cancel_booking(hour, schedule):
    
    schedule[hour]["client"] = ''
    schedule[hour]["booked"] = 0
    schedule[hour]["mode"] = ''
    
    updates_file(schedule)
    
    return schedule

def updates_file(schedule):
    
    with open('bookings_file.txt', 'w') as f:
        f.write(datetime.now().strftime("%Y-%m-%d") + "\n")
        # Write each dictionary to the file on a new line
        for hour in schedule:
            f.write(str(hour) + '\n')
  
def loads_usernames():
    username_list = []
    
    with open('usernames.txt', 'r') as f:
        content = f.read()
    
    for i, row in enumerate(content.splitlines()):
        username_list.append(row.split(', ')[0])
    
    return username_list
  
def checks_password(username, password):
    
    with open('usernames.txt', 'r') as f:
        content = f.read()
    
    for i, row in enumerate(content.splitlines()):
        if row.split(', ')[0] == username:
            if row.split(', ')[1] == password:
                return 1
            else:
                return 0

def add_user(username, password, email):
    with open('usernames.txt', 'a') as f:
        f.write(username + ', ' + password + ', ' + email + '\n')

def check_bookings_username(schedule, username):
    
    bookings = []
    
    for i, hour in enumerate(schedule):
        if hour['client'] == username:
           bookings.append(i) 
           
    return bookings

def validate_email(email):
    
    if '@' not in email:
        print('here 1')
        return 0

    if '.com' not in email and '.pt' not in email and '.es' not in email and '.it' not in email and '.ge' not in email and '.at' not in email:
        print('here 2')
        return 0
    
    return 1
    
#get_real_price_day()
# schedule = init_matrix()
# username_list = loads_usernames()

# username = input('Username : ')

# if username in username_list:
#     password = getpass.getpass()
# else:
#     print('New user. Welcome!')
    
#     while{True}:
#         email = input('Please insert your email: ')
#         if validate_email(email) == 1:
#             break
#         print('Invalid email.')
    
#     while{True}:
#         password1 = getpass.getpass('Please set your password: ')
#         password2 = getpass.getpass('Repeat your password: ')
#         if password1 == password2:
#             password = password1
#             add_user(username, password, email)
#             print('Welcome, ' + str(username) + '!')
#             break
#         print('Passwords do not correspond.\n')

# while{True}:

#     if checks_password(username, password) == 1:
#         print('Hello ' + str(username) + '!')
#         break
#     else:
#         print('Wrong password.')
#         password = getpass.getpass('Insert password again: ')
        

# availability = checks_availability(schedule)
# bookings = check_bookings_username(schedule, username)

# if len(bookings) != 0:
#     print('\n')
#     print('You already have bookings for this date, at times:')
#     print(*bookings, sep = ', ')
#     print('Select one of the previous hours to cancel booking or create a new booking with')
    
    
# print('The available hours for ' + datetime.now().strftime("%Y-%m-%d") + ' are:')
# print(*availability, sep = ', ')

# hour = int(input('Hour desired: '))

# if hour in availability:
#     schedule = creates_booking(schedule, username, hour)
#     print('Booking confirmed!\n')
# else:
#     if hour in bookings:
#         print('Are you sure you want to cancel your booking for ' + str(hour) + '? (y/n)')
        
#         answer = input()
        
#         if answer == 'y' or answer == 'Y':
#             schedule = cancel_booking(hour, schedule)
#             print('Booking cancelled \n')
#         else:
#             print('Booking at ' + str(hour) + ' remains')
#     else:
#         print('Try again. No availability at ' + str(hour))

# print('end')