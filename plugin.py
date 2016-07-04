import urllib2 as _urllib #FIXME: _urllib is not a good name.
import json

TIME_DIFF=0
global AUDIO_DELAY
AUDIO_DELAY=3000000

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
    referer="http://www.jazzradio.com/"+channel_key
    instance=vlc.get_default_instance()
    global PLAYER
    if not PLAYER:
        PLAYER=instance.media_player_new()
        vlc.libvlc_audio_set_delay(PLAYER, AUDIO_DELAY)
    media=instance.media_new(streams[0])
    global HTTP_SETTINGS
    media.add_option(":http-user-agent="+HTTP_SETTINGS["User-Agent"])
    media.add_option(":http-referrer="+referer)
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

def get_channel_history(channel_id):
    url="http://api.audioaddict.com/v1/jazzradio/track_history/channel/%s.json" % channel_id
    response = _urllib.urlopen(url).read()
    result = json.loads(response)
    return result

#FIXME: UNTESTED
def ping_procedure():
    import datetime
    now=datetime.datetime.utcnow()
    nowsec=int((now-datetime.datetime(1970,1,1)).total_seconds())
    result=ping_response_parser(ping(nowsec))
    global TIME_DIFF
    TIME_DIFF=(now-result).total_seconds()
    return (now-result).total_seconds()
    

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
    
    

