#!/usr/bin/env python3
import sys
import requests
import xmltodict
import math
import logging
import time
from datetime import datetime 
from flask import Flask, request
from geopy.geocoders import Nominatim 

app = Flask(__name__)



def get_data() -> list:
    """
    Gets the data from the NASA website for the ISS trejectories 

    Args: 
        No args for this function 
    
    Returns: 
        data (list): The data from the ISS trajectory xml 

    """
    r = requests.get("https://nasa-public-data.s3.amazonaws.com/iss-coords/current/ISS_OEM/ISS.OEM_J2K_EPH.xml")
    if r.status_code == 200:
        data = xmltodict.parse(r.text)
        return data

@app.route('/delete-data', methods=['DELETE'])
def delete() -> str:
    """
    Deletes all the data from the iss_data set

    Args: 
        No args 

    Returns: 
        (str): A string that says deleted to show the data has been deleted

    """
    global iss_data
    iss_data.clear()

    return "Deleted \n"


@app.route('/post-data', methods=['POST'])
def post() -> str:
    """
    Deletes all the data from the iss_data set

    Args:
        No args

    Returns:
        (str): A string that says "data posted" to show the data has been deleted

    """
    global iss_data
    iss_data = get_data()    
    return "data posted\n"   

#Global variable called iss_data 
iss_data = get_data()

@app.route('/', methods=['GET']) 
def data() -> list:  
    """
    Gets the ISS Trajectory data from the NASA website. 

    Args: 
        No args for this function.

    Returns: 
        iss_data (dict): The dictionary of the data that was imported using the requests library, the imported data was an 
        xml file. 
    """
    if iss_data == {}: 
        return "Data has been deleted\n"
    else:
        return iss_data 



def calculate_speed(x_dot, y_dot, z_dot) -> float:
    """
    calculates the speed
    inputs:
         x_dot (float)
         y_dot (float)
         z_dot (float)
    return:
         calculates speed (float)
    """
    if type(x_dot) == str:
        x_dot = float(x_dot)
        y_dot = float(y_dot)
        z_dot = float(z_dot)
        
    logging.info(f"Calculated speed: {math.sqrt(x_dot**2 + y_dot**2 + z_dot**2):.2f} km/s")
    return math.sqrt(x_dot**2 + y_dot**2 + z_dot**2)

##calculates the average speed
def average_speed(data) -> float:

    """
    Function calculates the average speed
    Args:
         data = dictonary : the data

    return: 
       the average speed (float)
    """
    
    total_speed = 0.0
    for entry in data:
        ##defines the x,y,z,velocity vectors
        x_dot = entry['X_DOT']['#text']
        y_dot = entry['Y_DOT']['#text']
        z_dot = entry['Z_DOT']['#text']
        total_speed += calculate_speed(x_dot, y_dot, z_dot)
    
    num_entries = len(data)
    logging.info(f"Average speed: {total_speed / num_entries:.2f} km/s")
    return total_speed / num_entries

@app.route('/epochs/<epoch>/speed', methods=['GET'])
def get_speed(epoch) -> str:
    '''
    returns the speed of a specific state vecor
    '''
    # Parse the response content
    response = requests.get(url='https://nasa-public-data.s3.amazonaws.com/iss-coords/current/ISS_OEM/ISS.OEM_J2K_EPH.xml')
    data = xmltodict.parse(response.content)
    sub_data = data['ndm']['oem']['body']['segment']['data']['stateVector']

    # Find the matching epoch
    for entry in sub_data:
        if entry['EPOCH'] == epoch:
            # Extract velocity components
            x_dot = float(entry['X_DOT']['#text'])
            y_dot = float(entry['Y_DOT']['#text'])
            z_dot = float(entry['Z_DOT']['#text'])

            # Calculate and return speed
            speed = calculate_speed(x_dot, y_dot, z_dot)
            return {'speed': speed}

    # If no matching epoch is found, return an error message
    return {'error': 'Epoch not found'}, 404

@app.route('/epochs/<epoch>', methods=['GET'])
def get_state_vectors(epoch) -> str:
    '''
    Returns the specific state vector provided
    '''
    # Parse the response content
    response = requests.get(url='https://nasa-public-data.s3.amazonaws.com/iss-coords/current/ISS_OEM/ISS.OEM_J2K_EPH.xml')
    data = xmltodict.parse(response.content)
    sub_data = data['ndm']['oem']['body']['segment']['data']['stateVector']

    # Find the matching epoch
    for entry in sub_data:
        if entry['EPOCH'] == epoch:
            # Extract state vectors
            x = float(entry['X']['#text'])
            y = float(entry['Y']['#text'])
            z = float(entry['Z']['#text'])
            x_dot = float(entry['X_DOT']['#text'])
            y_dot = float(entry['Y_DOT']['#text'])
            z_dot = float(entry['Z_DOT']['#text'])

            # Return state vectors
            return {'x': x, 'y': y, 'z': z, 'x_dot': x_dot, 'y_dot': y_dot, 'z_dot': z_dot}

    # If no matching epoch is found, return an error message
    return {'error': 'Epoch not found'}, 404

@app.route('/epochs', methods=['GET'])
def get_epochs() -> str:
    '''
    will return the limit of the users input
    '''
    # Parse the response content
    response = requests.get(url='https://nasa-public-data.s3.amazonaws.com/iss-coords/current/ISS_OEM/ISS.OEM_J2K_EPH.xml')
    data = xmltodict.parse(response.content)
    sub_data = data['ndm']['oem']['body']['segment']['data']['stateVector']

    # Get the 'limit' and 'offset' query parameters
    limit = request.args.get('limit', default=len(sub_data), type=int)
    offset = request.args.get('offset', default=0, type=int)

    # Validate the 'limit' and 'offset' query parameters
    if limit < 0 or offset < 0:
        return {'error': 'Invalid query parameters'}, 400

    # Get the list of epochs based on the 'limit' and 'offset' query parameters
    epochs = [entry['EPOCH'] for entry in sub_data[offset:offset+limit]]

    # Return the list of epochs
    return {'epochs': epochs}

@app.route('/epochs', methods=['GET'])
def get_data()-> str:
    '''
    returns the enitre data
    '''
    # Parse the response content
    response = requests.get(url='https://nasa-public-data.s3.amazonaws.com/iss-coords/current/ISS_OEM/ISS.OEM_J2K_EPH.xml')
    data = xmltodict.parse(response.content)
    sub_data = data['ndm']['oem']['body']['segment']['data']['stateVector']

    # Convert the data to a list of dictionaries
    data_list = []
    for entry in sub_data:
        data_dict = {
            'epoch': entry['EPOCH'],
            'x': float(entry['X']['#text']),
            'y': float(entry['Y']['#text']),
            'z': float(entry['Z']['#text']),
            'x_dot': float(entry['X_DOT']['#text']),
            'y_dot': float(entry['Y_DOT']['#text']),
            'z_dot': float(entry['Z_DOT']['#text']),
        }
        data_list.append(data_dict)

    # Return the entire data set
    return {'data': data_list}


@app.route('/now', methods=['GET'])
def get_now() -> str:
    '''
    return the velocity now
    '''
    response = requests.get(url='https://nasa-public-data.s3.amazonaws.com/iss-coords/current/ISS_OEM/ISS.OEM_J2K_EPH.xml')
    
    data = xmltodict.parse(response.content)

    sub_data = data['ndm']['oem']['body']['segment']['data']['stateVector']
    # Parse the response content
    current_time = datetime.now()
    logging.info(f"Current timestamp: {current_time}")

    # Find the closest epoch (state vector) based on the current time
    closest_epoch = None
    closest_time_diff = float('inf')  # Initialize with a large value
    velocity_now = None
    for bob in sub_data:
        timestamp_str = bob['EPOCH']
        timestamp_format = "%Y-%jT%H:%M:%S.%fZ"
        timestamp_dt = datetime.strptime(timestamp_str, timestamp_format)
        ### need to add time to catch up to UTC
        time_diff = abs((current_time - timestamp_dt).total_seconds() + 21600) 
        if time_diff < closest_time_diff:
            closest_time_diff = time_diff
            velocity_now = bob
            closest_epoch = bob['EPOCH']

    # Extract velocity components for the closest epoch
    x_dot_now = float(velocity_now['X_DOT']['#text'])
    y_dot_now = float(velocity_now['Y_DOT']['#text'])
    z_dot_now = float(velocity_now['Z_DOT']['#text'])

    # Calculate speed "now"
    speed_now = calculate_speed(x_dot_now, y_dot_now, z_dot_now)
    return(f"Speed 'now': {speed_now:.2f} km/s and the closest time now is {closest_epoch}")
 
 
 
@app.route('/comment', methods=['GET'])
def comment() -> list:
    """
    Gives the comments that are associated with the data set 
    Returns: 
        list_of_comments (list): The comments associated with the data set as a list
        (str): A string that says data deleted if command is called after the data has been deleted
    
    """
    try:
        comment_data = data()
        list_of_comments = list(comment_data['ndm']['oem']['body']['segment']['data']['COMMENT'])
        return list_of_comments
    except TypeError: 
        return "Data has been deleted\n" 

@app.route('/metadata', methods=['GET'])
def metadata() -> dict:
    """
    Gives the metadata that is associated with the data set

    Args:
        None
    Returns:
        meta (dict): The metadata associated with the data set as a dictionary
        (str): A string that says data deleted if command is called after the data has been deleted
    """
    try: 
        metadata = data() 
        meta = metadata['ndm']['oem']['body']['segment']['metadata'] 
        return meta
    except TypeError: 
        return "Data was deleted\n" 
 
@app.route('/header', methods=['GET'])
def header() -> dict:
    """
    Gives the header that is associated with the data set
    Args:
        Non
    Returns:
        header (dict): The header associated with the data set as a dictioanry  
        (str): A string that says data deleted if command is called after the data has been deleted
    """
    try:
        header_data = data() 
        header = header_data['ndm']['oem']['header'] 
        return header
    except TypeError: 
        return "Data has been deleted\n" 


@app.route('/epochs/<string:epoch>/location', methods=['GET'])
def location(epoch: list) -> dict:
    """
    This route finds the location of a given epoch 

    Args: 
        epoch (list): The single epoch and all values associated with it
        
    Returns: 
        location (dict): A dictionary with latitude, longitude, altitude with its units, and its
                         geopostion for the epoch specified. 

    """
    try:
        MEAN_EARTH_RADIUS = 6371 #km 

        the_epoch = get_epochs(epoch)
        units = "km" 
        
        x = float(the_epoch['X']['#text']) 
        y = float(the_epoch['Y']['#text'])  
        z = float(the_epoch['Z']['#text'])  
   
        hrs = float(the_epoch['EPOCH'][9:11])
        mins = float(the_epoch['EPOCH'][12:14]) 
     
        lat = math.degrees(math.atan2(z, math.sqrt(x**2 + y**2))) 
        lon = math.degrees(math.atan2(y,x)) - ((hrs-12)+(mins/60))*(360/24) + 32
        alt = math.sqrt(x**2 + y**2 + z**2) - MEAN_EARTH_RADIUS
        
        if abs(lon) > 180: 
            if lon > 0: 
                lon = lon-180
                lon = 180-lon
            else: 
                lon = lon+180
                lon = 180+lon  

        geocoder = Nominatim(user_agent='iss_tracker')
        geoloc = geocoder.reverse((lat,lon), zoom=15, language='en') 

        if geoloc == None: 
            position = 'ISS is over the Ocean'
        else: 
            position = {'Address': geoloc.address} 

        location = {'latitude': lat, 'longitude': lon, 'altitude': {'value': alt,  'units': units}, 'geo': position }  
        return location
    except TypeError: 
        return "Make sure epoch ID is correct or the data was deleted\n" 

@app.route('/now', methods = ['GET'])
def now() -> dict:
    """
    The route returns the closest epoch at the current time 

    Args: 
        None
    Returns: 
        now (dict): This dictionary contains the ID for the closest epoch, it's geogrpahical location, and 
                    its speed and how many seconds it is away from now 

    """
    try: 
        time_now = time.time()
        epochs_data = get_epochs() 
        time_epoch = time.mktime(time.strptime(epochs_data[0][:-5], '%Y-%jT%H:%M:%S'))
        minimum = time_now - time_epoch 
 
        for epoch in epochs_data:
            time_epoch = time.mktime(time.strptime(epoch[:-5], '%Y-%jT%H:%M:%S'))
            diff = time_now - time_epoch
            if abs(diff) < abs(minimum):  
                minimum = diff 
                closest_epoch = epoch 
                          

        now = {} 
        now['closest_epoch'] = closest_epoch 
        now['seconds_from_now'] = minimum  
        now['location'] = location(closest_epoch)
        now['speed'] = get_speed(closest_epoch) 

        return now 
    except ValueError: 
        return "The data was deleted\n" 



@app.route('/now', methods = ["GET"])
def main():

    response = requests.get(url='https://nasa-public-data.s3.amazonaws.com/iss-coords/current/ISS_OEM/ISS.OEM_J2K_EPH.xml')
    
    data = xmltodict.parse(response.content)

    sub_data = data['ndm']['oem']['body']['segment']['data']['stateVector']
    print(data['ndm']['oem']['body']['segment']['data']['stateVector'][44]['EPOCH'])
    for entry in sub_data:
        print(entry)
        print(entry['X_DOT'])
        print(entry['X_DOT']['#text'])
        break
    
    # Extract timestamps from the first and last epochs
    first_epoch = data['ndm']['oem']['body']['segment']['metadata']['START_TIME']
    last_epoch = data['ndm']['oem']['body']['segment']['metadata']['STOP_TIME']
    print(f"Data range: From {first_epoch} to {last_epoch}")
    
    
    
    avg_speed = average_speed(sub_data)
    print(f"Average speed of the whole data set: {avg_speed:.2f} km/s")

    ## Chat gpt helped me with this part: 
    current_time = datetime.now()
    logging.info(f"Current timestamp: {current_time}")

    # Find the closest epoch (state vector) based on the current time
    closest_epoch = None
    closest_time_diff = float('inf')  # Initialize with a large value
    velocity_now = None
    for bob in sub_data:
        timestamp_str = bob['EPOCH']
        timestamp_format = "%Y-%jT%H:%M:%S.%fZ"
        timestamp_dt = datetime.strptime(timestamp_str, timestamp_format)
        ### need to add time to catch up to UTC
        time_diff = abs((current_time - timestamp_dt).total_seconds() + 21600) 
        if time_diff < closest_time_diff:
            closest_time_diff = time_diff
            velocity_now = bob
            closest_epoch = bob['EPOCH']

    # Extract velocity components for the closest epoch
    x_dot_now = float(velocity_now['X_DOT']['#text'])
    y_dot_now = float(velocity_now['Y_DOT']['#text'])
    z_dot_now = float(velocity_now['Z_DOT']['#text'])

    # Calculate speed "now"
    speed_now = calculate_speed(x_dot_now, y_dot_now, z_dot_now)
    print(f"Speed 'now': {speed_now:.2f} km/s and the closest time now is {closest_epoch}")
   
        
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
    main()
