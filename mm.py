import sys
import os
import photos
import location
import exif_info
import time
from objc_util import ObjCInstance
import haversine

def get_album_byname(albums, album_name):
    album = None
    for a in albums:
        if a.title == album_name:
            return a
    return None

def get_filename(asset):
    r = ObjCInstance(asset)
    root,ext = os.path.splitext(str(r.filename()))
    return root, ext
    
def success_report(a, i, mfg, dt, gps):
    #fstr = f'{i:4}: SUCC\t{mfg:5}\t{dt}\t{gps}\t{a.creation_date}'
    results = None
    if a.location != None:
        results = location.reverse_geocode(a.location)
    fs = f'{i:4}: SUCC\t{a.creation_date}\t{a.location}\t{results}'
    print(fs)
    return
    
def except_report(a, i, etype, e):
    except_rpt = f'{i:4}: {a.creation_date}\t{"ERR "} - {etype} - {e}'
    print(except_rpt)
    return

def find_nearest_location(locations, loc):
    '''
    Search through the collection of locations to see if current location
    is close to anything in the collection.
    '''
    radius_km = 0.05  #Distance to regard as zero
    
    for l in locations:
        dist = haversine.haversine_dict(loc, l)
        if dist <= radius_km:
            i = locations.index(l)
            
def list_by_location(locations, photos):
    lp = 0
    for loc in locations:
        lp+=1
        print(f'{lp:2} Loc: {loc}')
        ip = 0
        for photo in photos:
            if photo['location_idx'] == locations.index(loc):
                ip+=1
                print (f"\t {ip:3}: {photo['creation_date']}")
        print(f'\t==Location Index: {lp:3} Photos:{ip:3}')
    print(f'Total Locations: {lp}')

def main():
    #album_name = 'My Photo Stream'
    #albums = photos.get_albums()
    album_name = 'Camera Roll'
    albums = photos.get_smart_albums()
    
    album = get_album_byname(albums, album_name) 
    print('Album: {}'.format(album.title))
    if type(album) != photos.AssetCollection:
        sys.exit('Album not found!')

    photo_info_list = []
    print ('Photo Count: {}'.format(len(album.assets)))
    i = 0
    kID = 'local_id'
    kDate = 'creation_date'
    kGeo = 'location'
    kLocID = 'location_idx'

    for a in album.assets:
        try:
            i += 1
            photo_info = {}
            photo_info[kID]    = a.local_id        #iOS local filename
            photo_info[kDate]  = a.creation_date   #Photo date/timestamp
            photo_info[kGeo]   = a.location        #GPs lat/lon of photo 
            photo_info[kLocID] = None              #index into locations list
            photo_info_list.append(photo_info)
        except Exception as e:
            print (f'Exception: {e}')
                
    #--- End of asset loop
    print (f'Album: {album_name}')
    print (f'Count: {i}')
      
    print (f'\n===== Post sort ({kDate})')
    # Sort photo_info_list by creation date
    s_photo_list = sorted(photo_info_list, key= lambda p: p[kDate] )
    count = i = no_gps = 0
    locations = []    #list of locations
    base_loc = None   #current location
    radius_km = 0.05  #Distance to regard as zero

    print (f'Count sorted: {len(s_photo_list)}')
    for s in s_photo_list:
        dist = 0
        i+=1
        #print (f'{i:4}: {s}')
        if s[kGeo] == None:
            no_gps += 1
            continue
        
        if s[kLocID] == None:
            #s[kLocID] = find_nearest_location(locations, s[kLocID])
            if len(locations) != 0:
                for loc in locations:
                    # See if current location is near existing location
                    dist = haversine.haversine_dict(s[kGeo], loc)
                    if dist <= radius_km:
                        s[kLocID] = locations.index(loc)
                        break
            if s[kLocID] == None:
                # Add current photo 's' to locations as it is not within radius
                # Add current location to locations list
                locations.append(s[kGeo])
                s[kLocID] = locations.index(s[kGeo])
            print(f'{i:4}: index:{s[kLocID]} latlon:{locations[s[kLocID]]}')
        else:
            dist = 'None'
        
        '''    
        print(f'# of Locations: {len(locations)}')
        i = 0
        for ll in locations:
            i+= 1
            print(f'{i:4}: {ll}')
        '''
    print (f'No gps photos: {no_gps}')   
    
    no_gps = 0
    for s in s_photo_list:
        if s[kLocID] == None:
            no_gps+=1
            print (f'{no_gps:3}: {s_photo_list.index(s)} - {s[kDate]}')
    print (f'No. photos no location idx: {no_gps}')
    
    i = total = 0
    for ll in locations:
        x = 0
        idx = locations.index(ll)
        for s in s_photo_list:
            if s[kLocID] == idx:
                x+=1
        results = location.reverse_geocode(ll)
        print (f'idx: {idx:2} count: {x:4} loc:{results}')
        total += x
    print (f'Total loc pictures: {total}')
    print(f'============')
    
    list_by_location(locations, s_photo_list)    
    
if __name__ == '__main__':
    main()

