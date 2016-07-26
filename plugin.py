import urllib2 as _urllib #FIXME: _urllib is not a good name.
import json

TIME_DIFF=0
global AUDIO_DELAY
AUDIO_DELAY=0

CHANNELS=None
FILTERS=None
HTTP_SETTINGS={"User-Agent":"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36"
               }
PLAYER=None
CHANNEL_NAME_ID_DICT={}
global vlc
vlc=None

if __name__=="__main__":
    pass
else:
    import extensions
    global vlc
    vlc = extensions.get_extension('vlc')
    if not vlc:
        raise Exception("VLC extension not loaded.")


def thread_reader(queue):
    pass

import threading

def co_reader(queue, event):
    print("Started coreader")
    import time
    import urllib2
    req=urllib2.Request(stream)
    req.add_header("Referer",referer)
    req.add_header("User-Agent",HTTP_SETTINGS["User-Agent"])
    st=urllib2.urlopen(req)
    title_dur=("Test",123)
    byteamount=0
    while not event.is_set():
        data=st.read(8192*2*2*2*2*2*2)
        byteamount=byteamount+len(data)
        
        if not data:
            print("Stream closed, or ahead?")
            st.close()
        if "onMetaData" in data:
            print("%s + %s" % (time.ctime(int(time.time())), byteamount))
            print("%r"%data)
            index=data.index('onMetaData')
            start=index+20+10
            try:
                length=int(data[start], 16)
            except ValueError:
                length=int(data[start].encode('hex'), 16)
            start=start+1
            title_dur=(data[start:start+length], 0)
        if "time" in data:
            index=data.index('time')+6
            index_end=index+3
            sel=data[index:data.index('t', index)-2]
            #print(sel)
            #print(sel.encode('hex'))
            print("%r"%sel)
            if len(sel)>2:
                duration=int(sel[0:2].encode('hex'), 16)+int(sel[2].encode('hex'), 16)
            else:
                duration=120
            queue.put((title_dur[0], duration))
        if "tlPreciseTime" in data:
            index=data.index('tlPreciseTime')
            index_end=index+20
            #print()
            
        time.sleep(1)
    print("Closing listeneing stream therad")

def initialize_dict():
    global CHANNELS
    global CHANNEL_NAME_ID_DICT
    if not CHANNELS:
        load_channels()
    if CHANNELS:
        for i in CHANNELS:
            if 'key' in i:
                name=i['key']
                channel_id=i['id']
                CHANNEL_NAME_ID_DICT[name]=str(channel_id)
    else:
        raise Exception("Channels have not been initialized.")

def get_currently_playing_channel(channel_key):
    global CHANNEL_NAME_ID_DICT
    if not CHANNEL_NAME_ID_DICT:
        initialize_dict()
    l=get_currently_playing()
    return "%s - %s" % (l[CHANNEL_NAME_ID_DICT[channel_key]]['display_artist'], l[CHANNEL_NAME_ID_DICT[channel_key]]['display_title'])

def play(channel_key):
    streams=get_stream_for_channel(channel_key)
    ref="http://www.jazzradio.com/"+channel_key
    instance=vlc.get_default_instance()
    global PLAYER
    if not PLAYER:
        PLAYER=instance.media_player_new()
        vlc.libvlc_audio_set_delay(PLAYER, AUDIO_DELAY)
    global stream
    stream=streams[0]
    global referer
    referer=ref
    media=instance.media_new(streams[0])
    global HTTP_SETTINGS
    media.add_option(":http-user-agent="+HTTP_SETTINGS["User-Agent"])
    media.add_option(":http-referrer="+ref)
    PLAYER.set_media(media)
    return PLAYER.play()

def stop():
    global PLAYER
    if PLAYER:
        PLAYER.stop()
    else:
        raise Exception("Nothing was playing.")

def load_channels():
    url="http://jazzradio.com/"
    
    response = _urllib.urlopen(url).read()

    start = response.index("NS('AudioAddict.API.Config').filters = ")
    end = response.index("</script>", start)

    z = response[start:end]

    el = z.split("NS('AudioAddict.API.Config')")
    
    filters = el[1][el[1].index("{"):].rsplit(";")[0]
    channels = el[2][el[2].index("["):].rsplit(";")[0]
    
    global CHANNELS
    CHANNELS=[i['channel'] for i in json.loads(channels) if i['channel']['type']=='channel']
    CHANNELS.sort(key=lambda x: x['name'])
    global FILTERS
    FILTERS=json.loads(filters)

def get_stream_for_channel(channel_key):
    url = "http://listen.jazzradio.com/webplayer/"+channel_key+".jsonp?callback=_API_Playlists_getChannel"
    resp = _urllib.urlopen(url).read()
    resp = resp[resp.index("["):resp.rindex(");")]
    result = json.loads(resp)
    return result

def get_currently_playing():
    url="http://www.jazzradio.com/_papi/v1/jazzradio/track_history"
    response = _urllib.urlopen(url).read()
    result = json.loads(response)
    return result

def sync_serverstarttime_and_timediff(starttime):
    return starttime+TIME_DIFF

def get_playing_position(key):
    print("Getting playing position")
    global AUDIO_DELAY
    global TIME_DIFF
    if TIME_DIFF==0:
        ping_procedure()
    channel_id=CHANNEL_NAME_ID_DICT[key]
    h=get_channel_history(channel_id)
    h.sort(key=lambda x: x['started'],reverse=True)
    for i in h[0:2]:
        if i['type']=='advertisement':
            if (get_msec_epoch()/1000)-(i['started']+TIME_DIFF) < 120:
                import time
                print("Ad coming up at: %s" % time.ctime(i['started']))
                print("Ad coming up at: %s" % time.ctime(i['started']+TIME_DIFF))
                print("Current time: %s" % time.ctime(int(time.time())))
                global PLAYER
                instance=vlc.get_default_instance()
                p=PLAYER
                PLAYER=instance.media_player_new()
                vlc.libvlc_audio_set_delay(PLAYER, AUDIO_DELAY)
                PLAYER.set_media(p.get_media())
                PLAYER.play()
                time.sleep(2)
                p.stop()
            else:
                print("Spotted past ad")
    index=0 if h[0]['artist'] else 1
    return (h[index]['started']+TIME_DIFF+(AUDIO_DELAY/1000000),h[index]['length'], h[index]['artist'], h[index]['title'])

def get_channel_history(channel_id):
    url="http://api.audioaddict.com/v1/jazzradio/track_history/channel/%s.json" % channel_id
    response = _urllib.urlopen(url).read()
    result = json.loads(response)
    return result

def get_msec_epoch():
    import datetime
    return int(((datetime.datetime.utcnow()-datetime.datetime(1970,1,1)).total_seconds())*1000)

def convert_to_epoch(dt_obj):
    import datetime
    return int(((dt_obj-datetime.datetime(1970,1,1)).total_seconds())*1000)

#Not sure how this would work...
def ping_procedure():
    import datetime
    epoch=get_msec_epoch()
    result=ping_response_parser(ping(epoch))
    nowsec=get_msec_epoch()
    r=convert_to_epoch(result)
    diff=nowsec-r
    global TIME_DIFF
    TIME_DIFF=diff/1000
    return TIME_DIFF
    

def ping(time_stamp_13_digit):
    url="http://api.audioaddict.com/v1/ping.jsonp?callback=_AudioAddict_WP_Ping__ping&_=%s" % time_stamp_13_digit
    response = _urllib.urlopen(url).read()
    result = response
    return result

def ping_response_parser(response):
    import time
    
    import re
    f=re.findall('"time":"([A-Za-z]{1,}, [0-9]{2} [A-Za-z]{1,} [0-9]{4} [0-9]{2}:[0-9]{2}:[0-9]{2} -[0-9]{1,})"', response)
    if f:
        import dateutil.parser
        import datetime
        z=dateutil.parser.parse(f[0])
        d=z-z.utcoffset()
        naived=d.replace(tzinfo=None)
        
        t=time.mktime(time.strptime(f[0],'%a, %d %b %Y %H:%M:%S -0400'))
        return naived

#{"tlPreciseTime":"200","StreamUrl":"","type":"event","insertionType":"midroll","time":"200","durationMilliseconds":"36873","StreamTitle":"JazzRadio.com","metadata":"adswizzContext=fHA6NzY2M158aDozN158cDo3NzM3","name":"NowPlaying","adw_ad":"true"}
#{"StreamTitle":"Danielle Pauly - Lgende du musette","time":"535","StreamUrl":"","tlPreciseTime":"540","type":"event","name":"NowPlaying"}
    

#OUTDATED
def get_referer():
    url="http://www.jazzradio.com/jazzballads"
    response = _urllib.urlopen(url).read()
    import re
    f = re.findall('src="(/assets/pages/channels-[a-z0-9]*\.js)"', response)
    if f:
        f[0]
    
    

