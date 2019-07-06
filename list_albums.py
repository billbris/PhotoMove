
import sys
import photos

def main():
    std_albums = photos.get_albums()
    
    print('Albums')
    print('------')
    for a in std_albums:
        print (f'{a.title}')
    
    print('\nSmart Albums')
    print('------------')
    smart_albums = photos.get_smart_albums()
    for a in smart_albums:
        print(f'{a.title}')
        
if __name__ == '__main__':
    main()
