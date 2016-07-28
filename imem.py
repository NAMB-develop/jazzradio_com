import ctypes

MediaOpenCb = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_void_p, ctypes.POINTER(ctypes.c_void_p), ctypes.POINTER(ctypes.c_uint64)) # The last argument seems to be some sort of buffer size thing.
MediaReadCb = ctypes.CFUNCTYPE(ctypes.c_ssize_t, ctypes.c_void_p, ctypes.POINTER(ctypes.c_char), ctypes.c_size_t)
MediaSeekCb = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_void_p, ctypes.c_uint64)
MediaCloseCb = ctypes.CFUNCTYPE(ctypes.c_void_p, ctypes.c_void_p)

def opaque_to_pyobj(opaque):
    return ctypes.cast(opaque,ctypes.POINTER(ctypes.py_object)).contents.value


def open_cb(opaque, datap, length):
    m=opaque_to_pyobj(opaque)
    import urllib2
    m.stream=urllib2.urlopen(m.request)
    datap.contents.value=opaque
    length.contents.value=4096
    return 0
        
def read_cb(opaque, buf, length):
    m=opaque_to_pyobj(opaque)
    a=m.index-len(m.store)
    if a < 0:
        #The index position is at a position in store.
        to=a*-1 if a*-1 < length else length
        data=m.store[m.index:m.index+to]
        m.index=m.index+to
    else:
        #The index position is at a position in data we need to get.
        data=m.stream.read(length)
        m.store=m.store+data
        m.index=m.index+length

        if len(m.store) > m.storelimit:
            diff=len(m.store)-m.storelimit
            m.cut=m.cut+diff
            m.store=m.store[:m.storelimit]
            m.index=m.index-diff
            
    for i in range(len(data)):
        buf[i]=data[i]
    print("%r %r" % (len(data), length))
    return len(data)

def seek_cb(opaque, offset):
    m=opaque_to_pyobj(opaque)
    #The offset is absolute, therefore we need to adjust it for the bytes we cut off.
    if offset-m.cut < len(m.store) and offset-m.cut > 0:
        m.index=offset-m.cut
        return 0
    else:
        return -1

def close_cb(opaque):
    m=opaque_to_pyobj(opaque)
    m.stream.close()
    m.store=""



class Media_Cast(object):

    def __init__(self, instance, request):
        self.request=request
        self.ob=MediaOpenCb(open_cb)
        self.rb=MediaReadCb(read_cb)
        self.sb=MediaSeekCb(seek_cb)
        self.cb=MediaCloseCb(close_cb)
        self.ref=ctypes.cast(ctypes.pointer(ctypes.py_object(self)), ctypes.c_void_p)
        self.store=""
        self.storelimit=4096
        self.index=0
        self.cut=0
        self.media=instance.media_new_callbacks(self.ob, #open_cb
                                                self.rb, #read_cb
                                                self.sb, #seek_cb
                                                self.cb, #close_cb
                                                self.ref, #opaque
                                                )

    def get_media(self):
        return self.media

def open_cb_queue(opaque, datap, length):
    m=opaque_to_pyobj(opaque)
    #import urllib2
    #m.stream=urllib2.urlopen(m.request)
    datap.contents.value=opaque
    length.contents.value=4096
    return 0

def read_cb_queue(opaque, buf, length):
    m=opaque_to_pyobj(opaque)
    a=m.index-len(m.store)
    if a < 0:
        #The index position is at a position in store.
        to=a*-1 if a*-1 < length else length
        data=m.store[m.index:m.index+to]
        m.index=m.index+to
    else:
        #The index position is at a position in data we need to get.
        data=m.queue.get()
        m.store=m.store+data
        m.index=m.index+length

        if len(m.store) > m.storelimit:
            diff=len(m.store)-m.storelimit
            m.cut=m.cut+diff
            m.store=m.store[:m.storelimit]
            m.index=m.index-diff
            
    for i in range(len(data)):
        buf[i]=data[i]
    #print("%r %r" % (len(data), length))
    return len(data)

class Media_Cast_Queue(object):

    def __init__(self, instance, request, queue):
        self.queue=queue
        self.request=request
        self.ob=MediaOpenCb(open_cb_queue)
        self.rb=MediaReadCb(read_cb_queue)
        self.sb=MediaSeekCb(seek_cb)
        self.cb=MediaCloseCb(close_cb)
        self.ref=ctypes.cast(ctypes.pointer(ctypes.py_object(self)), ctypes.c_void_p)
        self.store=""
        self.storelimit=4096
        self.index=0
        self.cut=0
        self.media=instance.media_new_callbacks(self.ob, #open_cb
                                                self.rb, #read_cb
                                                self.sb, #seek_cb
                                                self.cb, #close_cb
                                                self.ref, #opaque
                                                )

    def get_media(self):
        return self.media    

class Media(object):

    MediaOpenCb = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_void_p, ctypes.c_void_p, ctypes.POINTER(ctypes.c_uint64)) # The last argument seems to be some sort of buffer size thing.
    MediaReadCb = ctypes.CFUNCTYPE(ctypes.c_ssize_t, ctypes.c_void_p, ctypes.POINTER(ctypes.c_char), ctypes.c_size_t)
    MediaSeekCb = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_void_p, ctypes.c_uint64)
    MediaCloseCb = ctypes.CFUNCTYPE(ctypes.c_void_p, ctypes.c_void_p)

    def __init__(self, instance, request):
        self.request=request

        self.store=""
        self.storelimit=4096
        self.index=0
        self.cut=0

        import urllib2 # Temp   
        self.stream=urllib2.urlopen(self.request) #Temp

        def open_cb(opaque, datap, length):
            import urllib2
            self.stream=urllib2.urlopen(self.request)
            length.value=8192
            return 0

        self.ob=Media.MediaOpenCb(open_cb)
        
        def read_cb(opaque, buf, length):
            test=ctypes.cast(opaque,ctypes.POINTER(ctypes.py_object)).contents.value #Works!
            print(test.get_media())
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

        a=ctypes.cast(ctypes.pointer(ctypes.py_object(self)), ctypes.c_void_p)
        
        
        self.media=instance.media_new_callbacks(None, #open_cb #Implementation works, but edit of argument of size is weird, plus ListPOINTER does not work.
                                                self.rb, #read_cb
                                                self.sb, #seek_cb
                                                self.cb, #close_cb
                                                a, #opaque
                                                )

    def get_media(self):
        return self.media
