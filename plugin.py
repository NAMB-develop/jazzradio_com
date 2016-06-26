import urllib2 as _urllib #FIXME: _urllib is not a good name.
import json

CHANNELS=None
HTTP_SETTINGS={"User-Agent":"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36"
               }
PLAYER=None
CHANNEL_NAME_ID_DICT={}

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
        for i in range(len(CHANNELS['channels'])):
            if 'key' in CHANNELS['channels'][i]['channel']:
                name=CHANNELS['channels'][i]['channel']['key']
                channel_id=CHANNELS['channels'][i]['channel']['id']
                CHANNEL_NAME_ID_DICT[name]=str(channel_id)
    else:
        raise Exception("Channels could not be initialized.")

def get_currently_playing_channel(channel_key):
    l=get_currently_playing()
    return "%s - %s" % (l[CHANNEL_NAME_ID_DICT[channel_key]]['display_artist'], l[CHANNEL_NAME_ID_DICT[channel_key]]['display_title'])

def play(channel_key):
    streams=get_stream_for_channel(channel_key)
    referer="http://www.jazzradio.com/"+channel_key
    instance=vlc.get_default_instance()
    global PLAYER
    PLAYER=instance.media_player_new()
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
    
    resp = "{\"filters\":"+filters+", \"channels\":"+channels+"}"
    result = json.loads(resp)
    global CHANNELS
    CHANNELS=result
    return result

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
    
