""" This script store the function required to stream data from the API of your choice"""

import requests
import json
import pandas as pd
import numpy as np

# create GET request

def get_data_from_api():
    
    url = 
    header = 
    params = 

    response = requests.get(url, headers=headers, params=params)
    outputs = response.json()

    return outputs