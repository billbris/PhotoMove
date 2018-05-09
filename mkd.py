import ftplib
from ftplib import FTP
import os
import datetime

SEP = '-'
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
    sub_path = make_targetdir_string('batch')

    full_path = os.path.join(tgt_dir, sub_path)
    makedir(ftp, full_path)   
    
if __name__ == '__main__':
    main()
