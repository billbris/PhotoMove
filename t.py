import os
import sys

def main():
    un = os.uname()
    print(f'OS: {os.name}')
    print(f'uname: {un}')
    print(f'Platform: {sys.platform}')

    if sys.platform == 'ios':
        dir_prefix = un.nodename
    else:
        dir_prefix = 'batch'
    print(f'Directory prefix: {dir_prefix}')
    
if __name__ == '__main__':
    main()
