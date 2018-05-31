from configparser import ConfigParser

parser = ConfigParser()
parser.read('config.ini')

for section in parser.sections():
    print(f'[{section}]')
    for key in parser[section]:
        print(f'{key}:\t{parser[section][key]}')
