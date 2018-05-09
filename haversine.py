from math import radians, cos, sin, asin, sqrt

def haversine(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees) in kilometers
    """
    # convert decimal degrees to radians 
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    r = 6371 # Radius of earth in kilometers. Use 3956 for miles
    return c * r
    
def haversine_dict(gps1, gps2):
    '''
    Calculate the great circle distance between two points, each defined 
    by a dictionary including the keys: 'latitude', and 'longitude'.  
    The data is massaged to pass to the main function 'haversine'.
    '''
    lon1 = gps1['longitude']
    lat1 = gps1['latitude']
    lon2 = gps2['longitude']
    lat2 = gps2['latitude']
    return haversine(lon1, lat1, lon2, lat2)
