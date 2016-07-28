import imem

import ctypes

import sys, os
sys.path.insert(0, os.path.join("..","..",".."))

import extensions
extensions.load_extension("vlc")

global instance
instance=extensions.get_extension("vlc").Instance('-vvv')

def create_request():
    import urllib2
    req=urllib2.Request("http://pub8.jazzradio.com/jr_pariscafe_aacplus.flv")
    req.add_header('Referer','http://www.jazzradio.com/pariscafe')
    req.add_header('User-Agent',"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36")
    return req

mm=imem.Media_Cast(instance, create_request())
p=instance.media_player_new()

p.set_media(mm.get_media())

p.play()


#TODO: Wrap everything else around this
