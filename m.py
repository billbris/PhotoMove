import sys
import os
import photos
import location
import exif_info
import time
from objc_util import ObjCInstance

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

def main():
    #album_name = 'My Photo Stream'
    #albums = photos.get_albums()
    album_name = 'Camera Roll'
    albums = photos.get_smart_albums()
    
    album = get_album_byname(albums, album_name) 
    print('Album: {}'.format(album.title))
    if type(album) != photos.AssetCollection:
        sys.exit('Album not found!')

    print ('Photo Count: {}'.format(len(album.assets)))
    i = 0
    good = bad = heic = other = good_addr = bad_addr = 0
    grg = True
    for a in album.assets:
        try:
            i += 1
            '''
            if i%25 == 0:
                time.sleep(5)
            '''
            #p = a.get_image()
            #exif = exif_info.get_exif_data(p)
            dts = a.creation_date
            revgeo = None
            if a.location != None:
                revgeo = location.reverse_geocode(a.location)
                if len(revgeo)>0:
                    good_addr += 1
                    grg = True
                else:
                    bad_addr += 1
                    grg= False
                #time.sleep(0.75)
            print(f'{i:4}: loc: {a.location}\t geo: {grg}\t{dts}\t{revgeo}')
        except KeyError as e:
            except_report(a, i, 'KEY ', e)
            bad += 1
        except AttributeError as e:
            root, ext = get_filename(a)
            if ext == '.HEIC':
                heic += 1
                except_report(a, i, 'ATTRIB', (f'* Filename: {root:15}\t'+str(e)))
            else:
                other += 1
                except_report(a, i, 'ATTRIB', (f'. Filename: {root:15}\t'+str(e)))
            bad += 1        
        else:
            try:
                '''
                dt = exif_info.get_datetimestamp(exif)
                mfg = exif_info.get_camera_mfg(exif)
                gps = exif_info.get_lat_lon(exif)
                '''
                #success_report(a, i, None, None, None)
                #time.sleep(1)
                good += 1
            except KeyError as e:
                except_report(a, i, 'KEY ', e)
                bad += 1
            except AttributeError as e:    
                except_report(a, i, 'ATTR', e)
                bad += 1
                
    #--- End of asset loop
    
    print(f'Good:  {good}')
    print(f'Bad :  {bad}')
    print(f'HEIC:  {heic}')
    print(f'other: {other}')
    print(f'Good Geo: {good_addr}')
    print(f'Bad Geo:  {bad_addr}')
        
if __name__ == '__main__':
    location.start_updates()
    #time.sleep(5)
    main()
    location.stop_updates()
