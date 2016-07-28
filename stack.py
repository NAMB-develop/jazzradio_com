import ctypes
import io
import sys
import time

import edited_vlc as vlc

MediaOpenCb = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_void_p, ctypes.POINTER(ctypes.c_void_p), ctypes.POINTER(ctypes.c_uint64))
MediaReadCb = ctypes.CFUNCTYPE(ctypes.c_ssize_t, ctypes.c_void_p, ctypes.POINTER(ctypes.c_char), ctypes.c_size_t)
MediaSeekCb = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_void_p, ctypes.c_uint64)
MediaCloseCb = ctypes.CFUNCTYPE(ctypes.c_void_p, ctypes.c_void_p)


def media_open_cb(opaque, data_pointer, size_pointer):
    stream=ctypes.cast(opaque,ctypes.POINTER(ctypes.py_object)).contents.value
    data_pointer.contents.value = opaque
    size_pointer.contents.value = sys.maxsize
    return 0


def media_read_cb(opaque, buffer, length):
    stream=ctypes.cast(opaque,ctypes.POINTER(ctypes.py_object)).contents.value
    new_data = stream.read(length)
    for i in range(len(new_data)):
        buffer[i]=new_data[i]
    return len(new_data)


def media_seek_cb(opaque, offset):
    stream=ctypes.cast(opaque,ctypes.POINTER(ctypes.py_object)).contents.value
    stream.seek(offset)
    return 0


def media_close_cb(opaque):
    stream=ctypes.cast(opaque,ctypes.POINTER(ctypes.py_object)).contents.value
    stream.close()


callbacks = {
    'open': MediaOpenCb(media_open_cb),
    'read': MediaReadCb(media_read_cb),
    'seek': MediaSeekCb(media_seek_cb),
    'close': MediaCloseCb(media_close_cb)
}

def main(path):
    global stream
    stream = open(path, 'rb')
    instance = vlc.Instance('-vvv')
    player = instance.media_player_new()
    media = instance.media_new_callbacks(callbacks['open'], callbacks['read'], callbacks['seek'], callbacks['close'], ctypes.cast(ctypes.pointer(ctypes.py_object(stream)), ctypes.c_void_p))
    player.set_media(media)
    player.play()

    while True:
        time.sleep(1)


main("/home/frank/Downloads/Zommer.mp3")
