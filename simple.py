import ftplib
from ftplib import FTP
import photos
import sys
import os
import datetime
from objc_utilX import *
from collections import namedtuple
import configparser
from configparser import ConfigParser
import console
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
config_section = 'ftp_connection'

Settings = namedtuple('Settings', [
    'ftp_server',
    'ftp_port',
    'ftp_user',
    'ftp_pass',
    'ftp_basedir',
    'filename_sep',
    'media_type'
    ])
    
settings = Settings(
    'brisky.serveftp.com',
    21,
    'ftp_access',
    'Spartan86',
    '/ftp_access/dropzone',
    '-',
    'image')
    
SEP = settings.filename_sep

def datetime_string(d): 
    '''
        returns a formatted string of the date passed in.
    '''
    dt_string = f'{d.year:04}{SEP}{d.month:02}{SEP}{d.day:02}{SEP}{d.hour:02}{SEP}{d.minute:02}{SEP}{d.second:02}{SEP}{d.microsecond:06}'
    return dt_string
 
def make_targetdir_string(prefix):
    '''
        Create a subdirectory name that will hold all of the copied files.  
        The subdirectory name is a formatted current date/time string prefixed with a string.
    '''
    sub_path = datetime_string(datetime.datetime.today())
    tgt_dir = f'{prefix}{SEP}{sub_path}'
    return tgt_dir
        
def get_photo_format(uti_string):
    format_prefix = 'public.'
    return (uti_string.split(format_prefix,1)[1])
    
def create_asset_name(asset, buffer_uti):
    '''
        Given an iOS asset (picture/video/etc) create a filename using the
        asset metadata
    '''

    try:
        d = asset.creation_date
        date_taken = datetime_string(d)
        if len(asset.media_subtypes) != 0:
            date_taken += f'{SEP}{asset.media_subtypes[0]}'
        suffix = get_photo_format(buffer_uti)    
        date_taken += f'.{suffix}'
        return date_taken
    except Exception as e:
        print ('ERROR: rename_asset')
        print ('Exception: \n{}'.format(e))
        print(f'Asset creation date: {asset.creation_date}')
        return None
        
def copy_assets(ftp, media, tgt_dir):
    '''
        Step through all of the iOS media assets filtering by media type.  
        For each asset create a new filename based on the asset metadata and 
        then copy the asset via ftp to a target directory
    '''
    i = 1
    all_assets = photos.get_assets(media_type=media)
    for a in all_assets:
        pool = ObjCClass('NSAutoreleasePool').new()
        try:
            buffer = a.get_image_data(original = False)
            tgt_filename = create_asset_name(a, buffer.uti)
            fullpath = os.path.join(tgt_dir, tgt_filename)
            ftp.storbinary("STOR "+fullpath, buffer)		            
            print('{0:4}: --> {1} - {2}'.format(i, tgt_dir, tgt_filename))
        except SystemError as e:
            print('\t{0:4}: ERROR {1}'.format(i, e))
            print('\t\t{1} - {2}'.format(tgt_dir, tgt_filename))
        finally:
            i+=1
            pool.drain()

def make_ftp_targetdir(ftp, dirpath):
    '''
        Ensure that the ftp target directory exists.  If it does not, 
        create it.
    '''
    try:
        ftp.mkd(dirpath)
        print('MKD Success')
    except ftplib.all_errors as e:
        if '550' in e.args[0]:
            print(f'MKD Success: Directory already exists - [{dirpath}]')
        else:
            print('MKD Error')
            print('Error: {e}')

def load_config():
    try:
        parser = ConfigParser()
        parser.read('config.ini')
        section = parser[config_section]
        global settings
        settings = settings._replace(ftp_server    = section['ftp_server'])
        settings = settings._replace(ftp_pass      = section['ftp_pass'])
        settings = settings._replace(ftp_port      = int(section['ftp_port']))
        settings = settings._replace(ftp_basedir   = section['ftp_basedir'])
        settings = settings._replace(filename_sep  = section['filename_sep'])
        settings = settings._replace(media_type    = section['media_type'])
        global SEP
        SEP = settings.filename_sep
    except configparser.Error as e:
        print(f'Error: loading configuration file')
        print(f'\t{e}')
        
def setup():
    print('In setup...')
    load_config()

def start_ftp_session():
    print ('In start_ftp_session...')
    ftp = FTP()
    try:
        ret = ftp.connect(host=settings.ftp_server, port=settings.ftp_port)
        print (f'Connected: {ret}')
    except ftplib.all_errors as e:
        print (f'Error connecting to {settings.ftp_server}: {e}')
        sys.exit()
    else:
        try:
            ret = ftp.login(user=settings.ftp_user, passwd=settings.ftp_pass)
        except ftplib.all_errors as e:
            print (f'Error logging in to {settings.ftp_server}: {e}')
            sys.exit()
             
    if sys.platform == 'ios':
        un = os.uname()
        dir_prefix = un.nodename
    else:
        dir_prefix = 'batch'
    sub_dir = make_targetdir_string(dir_prefix)
    target_dir = os.path.join(settings.ftp_basedir, sub_dir)
    make_ftp_targetdir(ftp, target_dir)
                
    console.set_idle_timer_disabled(True)    #Don't let device go to sleep
    
    return ({'FTP':ftp, 'TargetDir':target_dir}) #return tuple 
    
def teardown(ftp):
    ftp.quit()
    console.set_idle_timer_disabled(False)    #Let device go back to its idle timer
    return
    
def main():
    setup()
    
    results = start_ftp_session()
    
    '''
    t = timeit.Timer(lambda: copy_assets(results['FTP'], settings.media_type, results['TargetDir']))
    res = t.timeit(number=1)
    print ('Time: {} seconds'.format(res))
    '''
    print(f'Settings: {settings}')
    teardown(results['FTP'])
    print()
    print('--------')
    print('Finished')
    
if __name__ == '__main__':
    main()
