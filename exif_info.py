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
import photos

from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
from datetime import datetime            #WPB: Added for get_datetimestamp

def get_exif_data(image):
    """Returns a dictionary from the exif data of an PIL Image item. Also converts the GPS Tags"""
    exif_data = {}
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
        raise KeyError('get_exif_data'+e)
    except AttributeError as e:
        raise AttributeError('No EXIF')
    else:
        return exif_data

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
    
def test():
    #album_name = 'My Photo Stream'
    #albums = photos.get_albums()
    album_name = 'Camera Roll'
    albums = photos.get_smart_albums()
    
    album = get_album_byname(albums, album_name) 
    print('Album: {}'.format(album.title))
    if type(album) != photos.AssetCollection:
        sys.exit('Album not found!')

    print ('Photo Count: {}'.format(len(album.assets)))
    
    a = album.assets[-2]
    i = 0
    good = bad = 0
    try:
        p = a.get_image()
        exif = get_exif_data(p)
    except KeyError as e:
        except_report(i, 'KEY ', e)
        bad += 1
    except AttributeError as e:    
        except_report(i, 'ATTRIB', 'No EXIF in file')
        bad += 1
    else:
        try:
            print(f'EXIF\n{exif}')
            dt = get_datetimestamp(exif)
            mfg = get_camera_mfg(exif)
            gps = get_lat_lon(exif)
            success_report(i, mfg, dt, gps)
            good += 1
        except KeyError as e:
            except_report(i, 'KEY ', e)
            bad += 1
        '''
        except AttributeError as e:    
            except_report(i, 'ATTR', e)
            bad += 1
        '''
                
    print(f'Good: {good}')
    print(f'Bad : {bad}')
 
def get_album_byname(albums, album_name):
    album = None
    for a in albums:
        if a.title == album_name:
            return a
    return None

def success_report(i, mfg, dt, gps):
    fstr = f'{i:4}: SUCC\t{mfg:5}\t{dt}\t{gps}'
    print(fstr)
    return
    
def except_report(i, etype, e):
    except_rpt = f'{i:4}: {"ERR "} - {etype} - {e}'
    print(except_rpt)
    return


################
# Example ######
################
if __name__ == "__main__":
    test()
    
    '''
    # load an image through PIL's Image object
    if len(sys.argv) < 2:
        print ("Error! No image file specified!")
        print ("Usage: %s <filename>" % sys.argv[0])
        sys.exit(1)

    image = Image.open(sys.argv[1])
    exif_data = get_exif_data(image)
    print (get_lat_lon(exif_data))
    '''
