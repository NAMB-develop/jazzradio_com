class Media(object):

    import ctypes

    MediaOpenCb = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_void_p, ctypes.c_void_p, ctypes.POINTER(ctypes.c_uint64))
    MediaReadCb = ctypes.CFUNCTYPE(ctypes.c_ssize_t, ctypes.c_void_p, ctypes.POINTER(ctypes.c_char), ctypes.c_size_t)
    MediaSeekCb = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_void_p, ctypes.c_uint64)
    MediaCloseCb = ctypes.CFUNCTYPE(ctypes.c_void_p, ctypes.c_void_p)

    def __init__(self, instance, request):
        self.request=request

        self.store=""
        self.storelimit=4096
        self.index=0
        self.cut=0

        def open_cb(opaque, datap, length):
            import urllib2
            self.stream=urllib2.urlopen(self.request)          
            return 0

        self.ob=Media.MediaOpenCb(open_cb)
        
        def read_cb(opaque, buf, length):
            a=self.index-len(self.store)
            if a < 0:
                #The index position is at a position in store.
                to=a*-1 if a*-1 < length else length
                data=self.store[self.index:self.index+to]
                self.index=self.index+to
                for i in range(len(data)):
                    buf[i]=data[i]
                return len(data)
            else:
                #The index position is at a position in data we need to get.
                data=self.stream.read(length)
                self.store=self.store+data
                self.index=self.index+length
                for i in range(len(data)):
                    buf[i]=data[i]

                if len(self.store) > self.storelimit:
                    diff=len(self.store)-self.storelimit
                    self.cut=self.cut+diff
                    self.store=self.store[:self.storelimit]
                    self.index=self.index-diff
                    
                return len(data)                

        self.rb=Media.MediaReadCb(read_cb)

        def seek_cb(opaque, offset):
            #The offset is absolute, therefore we need to adjust it for the bytes we cut off.
            if offset-self.cut < len(self.store) and offset-self.cut > 0:
                self.index=offset-self.cut
                return 0
            else:
                return -1

        self.sb=Media.MediaSeekCb(seek_cb)

        def close_cb(opaque):
            self.stream.close()
            self.store=""

        self.cb=Media.MediaCloseCb(close_cb)
        
        self.media=instance.media_new_callbacks(self.ob, #open_cb #Implementation works, but edit of argument of size is weird, plus ListPOINTER does not work.
                                                self.rb, #read_cb
                                                self.sb, #seek_cb
                                                self.cb, #close_cb
                                                None, #opaque
                                                )

    def get_media(self):
        return self.media
