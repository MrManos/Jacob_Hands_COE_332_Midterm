from flask import Flask, request 
import xmltodict
import requests
import math  
import time
from geopy.geocoders import Nominatim 


app = Flask(__name__)

def get_data() -> list:
    """
        data (list): The data from the ISS trajectory xml 
    """
    r = requests.get("https://nasa-public-data.s3.amazonaws.com/iss-coords/current/ISS_OEM/ISS.OEM_J2K_EPH.xml")
    ## Successful status code 
    if r.status_code == 200:
        data = xmltodict.parse(r.text)
        return data
 

@app.route('/', methods=['GET']) 
def data() -> list:  
    """
    Returns: 
        iss_data (dict): The dictionary of the data that was imported using the requests library, the imported data was an 
        xml file. 
    """
    if iss_data == {}: 
        return "Data has been deleted\n"
    else:
        return iss_data 

@app.route('/keys', methods=['GET'])
def keys() -> list:   
    """
    Goes thrrough all the keys in the data set to find which one epochs is under. 
    Returns: 
        list1 (list): returns a list of keys associated with the xml data
        list2 (list): returns a list of keys associated with the "ndm" key
        list3 (list): returns a list of keys associated with the "oem" key
        list4 (list): returns a list of keys associated with the "body" key
        list5 (list): returns a list of keys associated with the "segment" key
        list6 (list): returns a list of keys associated with the "data" key
        list7 (list): returns the epochs and the values associated with it using the stateVector key. 
    """

    key_data = data() 
    
    try:
        list1 = list(key_data.keys())
        # return list1
        list2 = list(key_data['ndm'].keys()) 
        #return list2 
        list3 = list(key_data['ndm']['oem'].keys())
        #return list3
        list4 = list(key_data['ndm']['oem']['body'].keys())
        #return list4
        list5 = list(key_data['ndm']['oem']['body']['segment'].keys())
        #return list5
        list6 = list(key_data['ndm']['oem']['body']['segment']['data'].keys())
        #return list6
        list7 = list(key_data['ndm']['oem']['body']['segment']['data']['stateVector'])
        return list7
    except AttributeError: 
        return "Data has been deleted\n" 

@app.route('/epochs', methods=['GET']) 
def epochs()->  list:  
    """
    Returns the epochs in the dictionary 
    Returns: 
        epochs (list): returns all epochs associated in the dictionary
    """    
    epochs = keys()  
    
    ## obtains the offset and limit when given in the curl 
    offset = request.args.get('offset',0)
    if offset: 
        try: 
            offset = int(offset)
        except ValueError: 
            return "Invalid start parameter; start must be an integer. \n"
    limit = request.args.get('limit', len(epochs)) 
    if limit: 
        try: 
            limit = int(limit)
        except ValueError: 
            return "Invalid start parameter; start must be an integer. \n" 
    if limit > len(epochs) or offset > len(epochs) or offset < 0 or limit < 0:
        return "Change query paramater \n"

    counter = 0 
    result = [] 
    for d in range(len(epochs)): 
        if counter == limit: 
            break 
        if d >= offset:
            try: 
                result.append(epochs[d]['EPOCH'])
                counter = counter + 1
            except TypeError: 
                return "Data has been deleted\n" 
    return result   


@app.route('/epochs/<epoch>', methods=['GET'])
def get_specific_epoch(epoch: str) -> list:
    """
    Returns the single epoch when provided 
    
    Args: 
        epoch (string): The specific EPOCH procided by the user 

    Returns: 
        Specific_Epoch (list): The state vectors associated with the epoch

    """  
    try:     
        epochs = keys()
        specific_epoch = [] 
        for i in range(len(epochs)): 
            if epoch == str(epochs[i]['EPOCH']):
                specific_epoch = epochs[i] 
                return  specific_epoch  
        if specific_epoch == []: 
            return "Please enter a valid epoch ID\n" 
    except TypeError: 
        return "Data has been deleted\n" 
    
     

@app.route('/epochs/<epoch>/speed', methods=['GET'])
def get_speed(epoch: list) -> dict:
    """
    Returns the instantaneous speed of a specific epoch 

    Args: 
        epoch (string): The specific EPOCH

    Returns: 
        awnser (f string): Returns the insatntaneous speed in an F string with the message "The speed of 
        the epoch is:"  
    """
    try: 
        Specific_Epoch = get_specific_epoch(epoch) 

        x_dot = float(Specific_Epoch['X_DOT']['#text'])
        y_dot = float(Specific_Epoch['Y_DOT']['#text'])
        z_dot = float(Specific_Epoch['Z_DOT']['#text']) 

        speed = math.sqrt(x_dot**2+y_dot**2+z_dot**2)

        awnser = {'value': speed, 'units': "km/s" }
        return awnser
    except TypeError: 
        return "Data has been deleted or try changing the epoch id\n" 



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

# @app.route('/post-data', methods=['POST'])
# def post() -> str:
#     """
#     Deletes all the data from the iss_data set

#     Returns:
#         (str): A string that says "data posted" to show the data has been deleted

#     """
#     global iss_data
#     iss_data = get_data()    
#     return "data posted\n"   

#Global variable called iss_data 
iss_data = get_data()

@app.route('/comment', methods=['GET'])
def comment() -> list:
    """
    Gives the comments that are associated with the data set 

    Returns: 
        list_of_comments (list): returns the comments header as a list
    
    """
    try:
        comments = data()
        list_of_comments = list(comments['ndm']['oem']['body']['segment']['data']['COMMENT'])
        return list_of_comments
    except TypeError: 
        return "Data has been deleted\n" 

@app.route('/header', methods=['GET'])
def header() -> dict:
    """
    Returns the headers as a dict 

    Returns:
        header (dict): The header values as a dict 
    """
    try:
        header_data = data() 
        header = header_data['ndm']['oem']['header'] 
        return header
    except TypeError: 
        return "Data has been deleted\n" 

@app.route('/metadata', methods=['GET'])
def metadata() -> dict:
    """
    Returns the metadata

    Returns:
        meta (dict): The metadata as a dictionary
    """
    try: 
        metadata = data() 
        meta = metadata['ndm']['oem']['body']['segment']['metadata'] 
        return meta
    except TypeError: 
        return "Data was deleted\n" 


@app.route('/epochs/<epoch>/location', methods=['GET'])
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

        the_epoch = get_specific_epoch(epoch)
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

        ## nominatim: allows developers to convert human-readable addresses into precise geographic coordinates and vice versa (chatgpt response)
        geocoder = Nominatim(user_agent='iss_tracker')
        ## reverses the geocoder
        geoloc = geocoder.reverse((lat,lon), zoom=15, language='en') 

        if geoloc == None: 
            position = 'ISS is over the Ocean'
        else: 
            position = {'Address': geoloc.address} 

        ## Returns the location as a string
        location = {'latitude': lat, 'longitude': lon, 'altitude': {'value': alt,  'units': units}, 'geo': position }  
        return location
    except TypeError: 
        return "Make sure epoch ID is correct or the data was deleted\n" 
    


@app.route('/now', methods = ['GET'])
def now() -> dict:
    """
    The route returns the closest epoch at the current time with all the geodata and speed

    Returns: 
        now (dict): Contains the geolocation of the  

    """
    try: 
        current_time = time.time()
        epoch_data = epochs() 
        time_epoch = time.mktime(time.strptime(epoch_data[0][:-5], '%Y-%jT%H:%M:%S'))
        minimum = current_time - time_epoch 
 
        for epoch in epoch_data:
            time_epoch = time.mktime(time.strptime(epoch[:-5], '%Y-%jT%H:%M:%S'))
            diff = current_time - time_epoch
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


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')