import photos

def main():
    media = 'image'
    all_assets = photos.get_assets(media_type=media)
    i = 1
    for a in all_assets:
        l = a.local_id
        x = l.find('/')
        if x != -1:
            l = a.local_id[:x]
        print('{0:2}: l:{1} full:{2}'.format(i,l,a.local_id))
        i+=1

if __name__ == '__main__':
    main()
