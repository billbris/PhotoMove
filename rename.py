import photos
import sys
import os
import piexif
from objc_utilX import *
import datetime
import timeit

from PIL import Image
from PIL.ExifTags import TAGS
from PIL.ExifTags import GPSTAGS

'''
    Run with timeit:

    Run with all duplicates:
'''
const0th = '0th'
constExif = 'Exif'

constDT = 0x0132         #306
constDTOrig = 0x9003     #36867
constDTSubSec = 0x9291   #37521
SEP = '-'                #Filename elements separator

def get_date_taken(exif_dict):
    dt = format_date_time(exif_dict)
    return (dt)

def format_date_time(exif_dict):
    '''
        Exif date/time format == YYYY:MM:DD HH:mm:ss
        This is stored as an ascii string of bytes, thus the str() conversion
            with utf-8.
    '''
    try:
        dt_string = str(exif_dict[constExif][constDTOrig], 'utf-8')
        dt_subsec = str(exif_dict[constExif][constDTSubSec], 'utf-8')
        dt_micro = int(dt_subsec)
        dt_full = '{}:{}'.format(dt_string, dt_subsec)
        fmt = '%Y:%m:%d %H:%M:%S:%f'
        d = datetime.datetime.strptime(dt_full, fmt)
    except KeyError as e:
        d = datetime.datetime.now()
    finally:
        return d

def dump_exif(exif_dict):
    print('Data:')
    x = get_date_taken((exif_dict))
    print('\n')
    for ifd_name in exif_dict:
        if ifd_name == 'thumbnail':
            continue
        if ifd_name == 'GPS':
            print('\n{} IFD:'.format(ifd_name))
            for key in exif_dict[ifd_name]:
                try:
                    print('0x{0:04x}({0})-{1}:\t{2}'.format(key, GPSTAGS[key], exif_dict[ifd_name][key][:10]))
                except: 
                    print('0x{0:04x}({0})-{1}E:\t{2}'.format(key, GPSTAGS[key], exif_dict[ifd_name][key]))
            continue
            
        print('\n{} IFD:'.format(ifd_name))
        for key in exif_dict[ifd_name]:
            try:
                print('0x{0:04x}({0})-{1}:\t{2}'.format(key, TAGS[key], exif_dict[ifd_name][key][:10]))
            except: 
                print('0x{0:04x}({0})-E:\t{2}'.format(key, TAGS[key], exif_dict[ifd_name][key]))
            
    
def rename_asset(asset):
    try:
        #img = asset.get_image()
        #exif_dict = piexif.load(img.info['exif'])
        #date_taken = get_date_taken(exif_dict)
        #print(date_taken)
        d = asset.creation_date
        date_taken = f'{d.year:04}{SEP}{d.month:02}{SEP}{d.day:02}{SEP}{d.minute:02}{SEP}{d.second:02}{SEP}{d.microsecond:06}'
        if len(asset.media_subtypes) != 0:
            date_taken += f'{SEP}{asset.media_subtypes[0]}'
        date_taken += '.jpg'
        return date_taken
    except Exception as e:
        print ('ERROR: rename_asset')
        print ('Exception: \n{}'.format(e))
        #print(f'img:{img}')
        #print(f'exif:{exif_dict}')
        print(f'Asset creation date: {asset.creation_date}')
        return None
    
def rename_all_assets():
    i = 1
    media='image'

    all_assets = photos.get_assets(media_type=media)

    '''
    a = all_assets[-1]
    new_name = rename_asset(a)
    return new_name
    '''
    
    unique_names = set()
    duplicate_names = []
    none_names = 0
    for a in all_assets:
        pool = ObjCClass('NSAutoreleasePool').new()
        try:
            new_name = rename_asset(a)
            if new_name == None:
                none_names += 1
            else:
                if new_name in unique_names:
                    duplicate_names.append(new_name)
                else:
                    unique_names.add(new_name)
                print('{:4}: {}'.format(i, new_name))        
        except SystemError as e:
            print('\t{0:4}: ERROR {1}'.format(i, e))
        finally:
            i+=1
            pool.drain()
    
    print ('Duplicates:  {}'.format(len(duplicate_names)))
    for d in duplicate_names:
        print (d)
    print ('Uniques:     {}'.format(len(unique_names)))
    print ('Nones:       {}'.format(none_names))
    print ('Total files: {}'.format(i))
        
def main():
    
    rename_all_assets()
   
    ''' 
    print('------')
    for t in TAGS:
        print('0x{0:04x}:{1}'.format(t, TAGS[t]))
    '''
    '''
    print(exif_name)
    print('\n')
    for x in exif_name:
        print(x)    
    '''
    #t = timeit.Timer(lambda: rename_all_assets())
    #res = t.timeit(number=1)
    #print ('Time: {} seconds'.format(res))
    
if __name__ == '__main__':
    main()
