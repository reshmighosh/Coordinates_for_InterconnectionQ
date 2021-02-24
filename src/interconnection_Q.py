import csv
from datetime import datetime, timedelta
import datetime
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from geopy.geocoders import Nominatim


def get_IR_county_coordinates(IR_file):

  """
  `IR_file: Interconnection request excel file for a particular state; for NY skip 19 rows from the boottom for IR queue sheet`

  """

  IR_queue = pd.read_excel(IR_file, skiprows = None, skipfooter = 19, sheet_name = 'Interconnection Queue')
  IR_queue.columns = [i.replace('/', '_') for i in IR_queue.columns]

  IR_queue.columns = [i.replace(' ', '_').lower() for i in IR_queue.columns]

  # Import to mention state name along with county name as geopy searches through
  IR_queue['county_state'] = IR_queue['county'] + ', ' + IR_queue['state']
  list_counties = list(IR_queue.county_state)
  county_coordinates = [list(geolocators.geocode(i))[1] for i in list_counties]

  if IR_queue['county_state'].shape[0] == 0:
    error = 'county and state names not concatenated properly'
    raise RuntimeError(error)

  IR_queue['county_coordinates'] = county_coordinates

  # Save the dataframe as file as geopy is slow
  IR_queue.to_csv('IR_queue.csv', index = False)

  return

def IR_analysis(processed_IR_file):
    """
    ```
    Import processed Interconnection Queue file with Coordinates and use the Latitude, Longitude, and Porposed in-service (IS) time for analysis
    
    ```
    """

    # Read the processed Interconnection Queue file with coordinates for County and State level

    IR_queue = pd.read_csv(processed_IR_file, sep = ",", skiprows  = 0) 

    # Split county coordinates in Latitude and Longitude and add them to a dataframe and rename

    temp = IR_queue['county_coordinates'].str[1:-1].str.split(',', expand=True).astype(float)
    IR_queue_final = pd.concat([IR_queue, temp], axis = 1)
    IR_queue_final.rename(columns = {0: 'Latitude', 1:'Longitude'}, inplace = True)

    # Filter the dataframe with only important columns and state of NY (some entries have PA)

    IR_plants = IR_queue_final[['project_name', 'date_of_ir', 'sp_(mw)', 'wp_(mw)', 'type__fuel', 'county', 'state', 'proposed__in-service', 'county_coordinates', 'Latitude', 'Longitude']]

    IR_plants = IR_plants[IR_plants.state == 'NY']

    # Change the proposed in service column to datetime format and address missing, random values

    IR_plants.iloc[:, 7]  = IR_plants.iloc[:, 7].str.replace('/', '-')
    IR_plants['proposed__in-service'] = IR_plants['proposed__in-service'].replace('I-S', 'nan')
    IR_plants['proposed__in-service'] = pd.to_datetime(IR_plants['proposed__in-service'])
    IR_plants['proposed_IS_year'] = IR_plants['proposed__in-service'].dt.year
    IR_plants['proposed_IS_month'] = IR_plants['proposed__in-service'].dt.month

    return IR_plants
