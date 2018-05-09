import ftplib
from ftplib import FTP
import photos
import sys
import os
import datetime
from objc_utilX import *
import timeit

'''
    Run with timeit:
        - Files copied:    1364        1364        1364    |    4086
        - Time required:    576.477    488.685    496.627  |  1561.789
        - Average/file:     0.42325    0.35880    0.36463  |  0.38223

    Run with all duplicates:
        - Files copied:    1364
        - Time required:    642.80715
        - Average/file:    2.1219

    Run without exif calls (asset.creation_date):
        - Files copied:    1373
        - Time required:   580.427
        - Average/file:    0.4227         

'''

SEP = '-'

def datetime_string(d):
    dt_string = f'{prefix}{SEP}{d.year:04}{SEP}{d.month:02}{SEP}{d.day:02}{SEP}{d.minute:02}{SEP}{d.second:02}{SEP}{d.microsecond:06}'
    return dt_string
 
def make_targetdir_string(prefix):
        sub_path = datetime_string(datetime.datetime.today())
        tgt_dir = f'{prefix}{SEP}{sub_path}'
        return tgt_dir
        
def make_target_filename(prefix, d):
    base_name = f'{prefix}{SEP}{datetimems_string(d)}'
    return base_name
    
def datetime_string(d):
        dt_string = f'{d.year:04}{SEP}{d.month:02}{SEP}{d.day:02}{SEP}{d.hour:02}{SEP}{d.minute:02}{SEP}{d.second:02}'
        return dt_string
        
def datetimems_string(d):
    dtms_string = f'{d.year:04}{SEP}{d.month:02}{SEP}{d.day:02}{SEP}{d.minute:02}{SEP}{d.second:02}{SEP}{d.microsecond:06}'
    return dtms_string
     
def create_asset_name(asset, prefix):
    try:
        #img = asset.get_image()
        #exif_dict = piexif.load(img.info['exif'])
        #date_taken = get_date_taken(exif_dict)
        #print(date_taken)
        d = asset.creation_date
        date_taken = datetimems_string(d)
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
        
def copy_assets(ftp, prefix, media, tgt_dir):
    
    i = 1
    all_assets = photos.get_assets(media_type=media)
    for a in all_assets:
        pool = ObjCClass('NSAutoreleasePool').new()
        try:
            '''
            l = a.local_id
            x = l.find('/')
            if x != -1:
                l = a.local_id[:x]
            '''
            #buffer = a.get_image()
            tgt_filename = create_asset_name(a, prefix)
            buffer = a.get_image_data(original = False)
            #tgt_filename = '{0}-{1}.jpg'.format(prefix, l)
            #ftp.copy_file(tgt_dir, tgt_filename, buffer)
            fullpath = os.path.join(tgt_dir, tgt_filename)
            ftp.storbinary("STOR "+fullpath, buffer)		            
            print('{0:4}: --> {1} - {2}'.format(i, tgt_dir, tgt_filename))
        except SystemError as e:
            print('\t{0:4}: ERROR {1}'.format(i, e))
            print('\t\t{1} - {2}'.format(tgt_dir, tgt_filename))
        finally:
            i+=1
            pool.drain()

def makedir(ftp, dirpath):
    try:
        ftp.mkd(dirpath)
        print('MKD Success')
    except ftplib.all_errors as e:
        if '550' in e.args[0]:
            print('MKD Success: Directory already exists')
        else:
            print('MKD Error')
            print('Error: {e}')
                
def main():
    ftp_site = '10.0.0.64'
    #ftp_site = 'dornoch'
    ftp_port = 2021
    username = 'Bill'
    ftp = FTP()
    try:
        ret = ftp.connect(host=ftp_site, port=ftp_port)
        print (f'Connected: {ret}')
    except ftplib.all_errors as e:
        print (f'Error connecting to {ftp_site}: {e}')
        sys.exit()
    else:
        try:
            ret = ftp.login(user='Bill')
        except ftplib.all_errors as e:
            print (f'Error logging in to {ftp_site}: {e}')
            sys.exit()

    prefix = 'ipad'
    media = 'image'
    tgt_dir = 'ftp_simple'
    
    if sys.platform == 'ios':
        un = os.uname()
        dir_prefix = un.nodename
    else:
        dir_prefix = 'batch'
    sub_dir = make_targetdir_string(dir_prefix)
    tgt_dir = os.path.join(tgt_dir, sub_dir)
    makedir(ftp, tgt_dir)
    
    t = timeit.Timer(lambda: copy_assets(ftp, prefix, media, tgt_dir))
    res = t.timeit(number=1)
    print ('Time: {} seconds'.format(res))
    
if __name__ == '__main__':
    main()
