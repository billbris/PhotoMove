'''
    File: exif_info.py
    Note: This was originally titled: 'ExifLatLon.py'.  This was a convenient set of functions
            to get the GPS values from the EXIF and convert them to a usable format.  
            
            Because this script converts the EXIF from a numerical list to a tag-based 
            dictionary, it was necessary to either use the tags in the other scripts, or convert
            this script to do more than just GPS functions.
            
    Added Functions:
        get_datetimestamp
        get_manufacturer
        
    Changes:
        WPB 2018-01-13    Original transfer and comments
'''
import sys

from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
from datetime import datetime            #WPB: Added for get_datetimestamp

def get_exif_data(image):
    """Returns a dictionary from the exif data of an PIL Image item. Also converts the GPS Tags"""
    try:
        info = image._getexif()
        if info:
            for tag, value in info.items():
                decoded = TAGS.get(tag, tag)
                if decoded == "GPSInfo":
                    gps_data = {}
                    for gps_tag in value:
                        sub_decoded = GPSTAGS.get(gps_tag, gps_tag)
                        gps_data[sub_decoded] = value[gps_tag]
    
                    exif_data[decoded] = gps_data
                else:
                    exif_data[decoded] = value
    except KeyError as e:
        raise KeyError(e)
    except AttributeError as e:
        raise AttributeError('No EXIF')
    else:
        return exif_data

def get_gps_fromexif(exif_data):
    try:
        if exif_data:
            for tag, value in exif_data.items():
                decoded = TAGS.get(tag, tag)
                if decoded == "GPSInfo":
                    gps_data = {}
                    for gps_tag in value:
                        sub_decoded = GPSTAGS.get(gps_tag, gps_tag)
                        gps_data[sub_decoded] = value[gps_tag]
    except KeyError as e:
        raise KeyError(f'gps_fromexif: {e}')
    except AttributeError as e:
        raise AttributeError(f'gps_fromexif: No EXIF')
    else:
        return gps_data
            
def _convert_to_degrees(value):
    """Helper function to convert the GPS coordinates stored in the EXIF to degress in float format"""
    deg_num, deg_denom = value[0]
    d = float(deg_num) / float(deg_denom)

    min_num, min_denom = value[1]
    m = float(min_num) / float(min_denom)

    sec_num, sec_denom = value[2]
    s = float(sec_num) / float(sec_denom)
    
    return d + (m / 60.0) + (s / 3600.0)

def get_lat_lon(exif_data):
    """Returns the latitude and longitude, if available, from the provided exif_data (obtained through get_exif_data above)"""
    lat = None
    lon = None

    try:
        if "GPSInfo" in exif_data:		
            gps_info = exif_data["GPSInfo"]

            gps_latitude = gps_info.get("GPSLatitude")
            gps_latitude_ref = gps_info.get('GPSLatitudeRef')
            gps_longitude = gps_info.get('GPSLongitude')
            gps_longitude_ref = gps_info.get('GPSLongitudeRef')

            if gps_latitude and gps_latitude_ref and gps_longitude and gps_longitude_ref:
                lat = _convert_to_degrees(gps_latitude)
                if gps_latitude_ref != "N":                     
                    lat *= -1

                lon = _convert_to_degrees(gps_longitude)
                if gps_longitude_ref != "E":
                    lon *= -1
        else:
            raise KeyError
    except KeyError as e:
        raise KeyError('GPS info not found')
    else:
        return lat, lon

def get_datetimestamp(exif_data):
    '''
        WPB: 2018-01-13
        Returns the original datetime stamp as a formatted string.
    '''
    try:
        dt_str = exif_data['DateTimeOriginal']
        dt = datetime.strptime(dt_str, '%Y:%m:%d %H:%M:%S')
        return dt
    except KeyError as e:
        raise KeyError(f'No datetimeoriginal in exif: {exif_data}')
      
def get_camera_mfg(exif_data):
    '''
        WPB: 2018-01-13
        Returns the camera manufacturer from the EXIF.
    '''
    try:
        mfg = exif_data['Make']
        return mfg
    except KeyError as e:
        raise KeyError(e)
    
    
################
# Example ######
################
if __name__ == "__main__":
    # load an image through PIL's Image object
    if len(sys.argv) < 2:
        print ("Error! No image file specified!")
        print ("Usage: %s <filename>" % sys.argv[0])
        sys.exit(1)

    image = Image.open(sys.argv[1])
    exif_data = get_exif_data(image)
    print (get_lat_lon(exif_data))
