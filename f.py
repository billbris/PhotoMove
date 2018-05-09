import ftplib
from ftplib import FTP

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
    else:
        try:
            ret = ftp.login(user='Bill')
            #ret = ftp.login()
            print (f'Success!')
            print (f'Site: {ftp_site}')
            print (f'port: {ftp_port}')
            print (f'Message: {ret}')
            ret = ftp.retrlines('LIST')
            print (f'List: {ret}')
            ret = ftp.quit()
        except ftplib.all_errors as e:
            print (f'Error logging in to {ftp_site}: {e}')

if __name__ == '__main__':
    main()
    
