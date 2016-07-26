import urllib2

import ctypes

#MediaOpenCb = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_void_p, ctypes.POINTER(ctypes.c_void_p), ctypes.POINTER(ctypes.c_uint64))
#MediaReadCb = ctypes.CFUNCTYPE(ctypes.c_ssize_t, ctypes.c_void_p, ctypes.c_char_p, ctypes.c_size_t)
#MediaSeekCb = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_void_p, ctypes.c_uint64)
#MediaCloseCb = ctypes.CFUNCTYPE(ctypes.c_void_p, ctypes.c_void_p)

import edited_vlc as vlc

class Media(object):

    def __init__(self, request):
        self.request=request

    def open_media(self):
        self.stream=urllib2.urlopen(self.request)

#@MediaReadCb
def read_cb(opaque, buf, length):
    print("Reading: %r %r %r" % (opaque, buf, length))
    print("Reading: %r %r %r" % (type(opaque), type(buf), type(length)))
    data=m.stream.read(length.value)
    buf.value=data
    length.value=len(data)
    print("%r" % data[0:2])
    #print(buf)
    #buf=data
    return length.value

#@MediaCloseCb
def close_cb(opaque):
    opaque.stream.close()
    pass

#@MediaOpenCb
def open_cb(opaque, unknown, number):
    print("Opening: %s %s %s" % (type(opaque),type(unknown),type(number)))
    opaque.stream=urllib2.urlopen(opaque.request)
    return 0

#@MediaSeekCb
def seek_cb(unknown, number):
    return 0

read_cb.argtypes=[ctypes.c_void_p, ctypes.c_char_p, ctypes.c_size_t]
read_cb.restype=ctypes.c_ssize_t

rb=vlc.CallbackDecorators.MediaReadCb(read_cb)

url="http://pub8.jazzradio.com/jr_pariscafe_aacplus.flv"
referer='http://www.jazzradio.com/pariscafe'

req=urllib2.Request(url)
req.add_header('Referer', referer)
req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36')
global m
m=Media(req)
m.open_media()

def create_media(vlc_instance, m):

    global t
    t=ctypes.byref(ctypes.py_object(m))
    
    return vlc.libvlc_media_new_callbacks(vlc_instance,
                                          None,
                                          rb,
                                          None,
                                          None,
                                          t)


#http://stackoverflow.com/questions/31250640/using-vlc-imem-to-play-an-h264-video-file-from-memory-but-receiving-error-main/31316867#31316867
#http://stackoverflow.com/questions/20694876/how-can-i-load-a-memory-stream-into-libvlc


i=vlc.Instance('-vvv')
p=i.media_player_new()
z=create_media(i, m)
p.set_media(z)




