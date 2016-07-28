import urllib2
import socket

import ctypes
import Queue

q=None

MediaReadCb = ctypes.CFUNCTYPE(ctypes.c_ssize_t, ctypes.c_void_p, ctypes.POINTER(ctypes.c_char), ctypes.c_size_t) # Works!

def read_cb(opaque, buf, length):
#    print("Reading: %r %r %r" % (opaque, buf, length))
    data=q.get()
    for i in range(len(data)):
        buf[i]=data[i]
#    print("%r" % data[0:2])
    return len(data)

rb=MediaReadCb(read_cb)

def create_request():
    req=urllib2.Request("http://pub8.jazzradio.com/jr_pariscafe_aacplus.flv")
    req.add_header('Referer','http://www.jazzradio.com/pariscafe')
    req.add_header('User-Agent',"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36")
    return req

def create_stream(req):
    return urllib2.urlopen(req)

def create_request_core():
    s=socket.socket()
    return s

def create_stream_core(s):
    s.connect(("pub8.jazzradio.com",80))
    req=[
        'GET /jr_vocallegends_aacplus.flv HTTP/1.1',
        'Host: www.jazzradio.com',
        'Referer: http://www.jazzradio.com/vocallegends',
        'User-Agent: Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36',
        'Connection: keep-alive',
        '',
        ''
        ]
    s.send("\r\n".join(req))
    return s
    

at=['\x12','\x08']

def find_start(data):
    result=0
    offset=0
    while True:
        t=data.index('\x08', offset)
        size=int(data[t+1:t+1+3].encode('hex'), 16)
        if data[t+11+size+4] in at:
            return t
        else:
            offset=t+1

def break_packets(data, offset=0):
    packets=[]
    i=data.index('\x08', offset)
    size=int(data[i+1:i+1+3].encode('hex'),16)
    if data[i+11+size+4] in at:
        print("Yay!")
        while True:
            t=i
            typ=data[t]
            t=t+1
            size=int(data[t:t+3].encode('hex'),16)
            t=t+3
            time=int((data[t+3]+data[t:t+3]).encode('hex'), 16)
            t=t+4
            stream_id=data[t:t+3]
            t=t+3
            payload=data[t:t+size]
            i=t+size+4
            p=[typ,size,time,stream_id,payload]
            packets.append(p)
            if i > len(data)-1:
                return packets
    else:
        i=data.index('\x12', offset)
        size=int(data[i+1:i+1+3].encode('hex'),16)
        if data[i+11+size+4] in at:
            print("Yay!")
            while True:
                t=i
                typ=data[t]
                t=t+1
                size=int(data[t:t+3].encode('hex'),16)
                t=t+3
                time=int((data[t+3]+data[t:t+3]).encode('hex'), 16)
                t=t+4
                stream_id=data[t:t+3]
                t=t+3
                payload=data[t:t+size]
                i=t+size+4
                p=[typ,size,time,stream_id,payload]
                packets.append(p)
                if i > len(data)-1:
                    return packets
        else:
            print("Fail")
    return packets

import struct

def read_header(data):
    i=0
    s=data[i:i+3]
    i=i+3
    one_byte=data[i]
    i=i+1
    audio_byte=data[i]
    i=i+1
    header_size=struct.unpack(">I",data[i:i+4])[0]

def process_packet(data):
    p=[None]*6
    t=0
    if len(data) < 15:
        return p
    p[0]=data[t:t+4]

    t=t+4
    p[1]=data[t:t+1]
    if not p[1] in at:
        return p

    t=t+1
    p[2]=data[t:t+3]
    size=struct.unpack(">I","\x00"+p[2])[0]
    if t+3+size+7 > len(data):
        return p

    t=t+3
    p[3]=data[t:t+3]+data[t+3:t+4]

    t=t+4
    p[4]=data[t:t+3]

    t=t+3
    p[5]=data[t:t+size]

    #p[7]=t+p[2]
    #print("size: %s"%total_length)
    #p[6]=data[:p[7]]
    #p=[prev_size,typ,size,time,stream_id,payload]
    return p

packets=[None]*1024

import threading

class Streamer(object):

    def __init__(self, event, packets):
        self.packets=packets
        self.event=event
        self.stopper=threading.Event()
        self.thread=None
        self.started=False
        #self.f=open("stream%s.bin"%str(self.stopper),'wb')

    def stop(self):
        print("Stopping thread")
        self.stopper.set()
        self.event.clear()
        self.started=False
        self.stream.close()
        while not self.packets.empty():
            self.packets.get()

    def start(self):
        print("Starting thread")
        self.stopper=threading.Event()
        self.event.clear()
        self.started=True
        self.thread=threading.Thread(target=self.run)
        self.thread.daemon=True
        self.thread.start()
        

    def run(self):
        self.stream=create_stream_core(create_request_core())
        self.start_time=int(time.time())
        http_header=self.stream.recv(129)
        header=self.stream.recv(9)
        self.packets.put(["","","","","","",header])
        #self.f.write(header)
        print("%r"%header)
        chunk=""
        index=0
        last_suc=None
        while not self.stopper.is_set():
            #print("Fetching chunk:")
            d=self.stream.recv(8196)
            #print("Queue size: %s" % self.packets.qsize())
            #self.f.write(d)
            chunk=chunk+d
            if chunk:
                if "adswizz" in chunk:
                    print("Ad coming up")
                    self.event.set()
                while True:
                    p=process_packet(chunk)
                    pdata="".join(filter(None, p))
                    if p[-1]:
                        i=len(pdata)
                        #if len(chunk)>i+4:
                         #   if not chunk[i+4:i+5] in at:
                          #      print("Whats wrong with this part?\n%r"%chunk[:i])
                        last_suc=p
                        self.packets.put(p)
                        chunk=chunk[i:]
                    else:
                        if p[1]:
                            if not p[1] in at:
                                print("Corrupted packet: %r\n%r"%(p,pdata))
                                c=chunk[0:1]
                                chunk=chunk[1:] #Apparently, sometimes an extra byte is added. Retry once:
                                pp=process_packet(chunk)
                                #print("vPacket: %r"%pp)
                                if pp[-1]:
                                    pp[-2]=c+pp[-2]
                                    i=pp[-1]
                                    self.packets.put(pp)
                                    chunk=chunk[i+1:]                                
                                else:
                                    print("Fail after retry: %r"%pp)
                                    print("From chunk: %r"%chunk)
                                    print("Last succesful: %r"%last_suc)
                                    raise IOError
                                break
                            break
                        else:
                            #print("Failed to create packet from chunk:\n%r"%chunk)
                            #print("\n%r"%p)
                            break
                    #chunk=chunk[i:]
        self.stream.close()
        #self.f.close()

import Queue, subprocess, time, sys

def get_time(s1):
    return struct.unpack(">I",s1[3]+s1[0:3])[0]
    #return int((s1[3]+s1[0:3]).encode('hex'), 16)

def get_string(t1):
    s1=struct.pack(">I", t1)
    return s1[1:]+s1[0]

def transform_time(t1, offset):
    i_t1=get_time(t1)
    i_t2=i_t1+offset
    return get_string(i_t2)

"""\x02\x00\nonMetaData         #Length of length indicator + length indicators of first text element.
                                #First text element
\x08                            #Type: SCRIPTDATAECMAARRAY
\x00\x00\x00\x06                #Length of array
\x00\x0bStreamTitle\x02\x00\x1dNaim Amor - Son Grand Sourire                        
\x00\tStreamUrl\x02\x00\x00
\x00\x04name\x02\x00\nNowPlaying                                         
\x00\x04time\x02\x00\x010                       #Time since start of stream.                
\x00\rtlPreciseTime\x02\x00\x010
\x00\x04type\x02\x00\x05event\x00\x00\t"""

def read_metadata(metadata):
    i=0
    ll=int(metadata[0].encode('hex'),16)
    i=i+1
    l=int(metadata[i:i+2].encode('hex'),16)
    i=i+2
    s1=str(metadata[i:i+l])
    i=i+l
    t=metadata[i]
    i=i+1
    la=int(metadata[i:i+4].encode('hex'),16)
    i=i+4
    result={}
    for el in range(la):
        kl=int(metadata[i:i+2].encode('hex'),16)
        i=i+2
        k=str(metadata[i:i+kl])
        i=i+kl
        vll=int(metadata[i].encode('hex'),16)
        i=i+1
        vl=int(metadata[i:i+2].encode('hex'),16)
        i=i+2
        v=str(metadata[i:i+vl])
        i=i+vl
        result[k]=v
    if "time" in result and "tlPreciseTime" in result:
        for z in ["time","tlPreciseTime"]:
            if len(result[z])>2:
                #result[z]=(int(result[z][:-2])*60)+int(result[z][-2:])
                pass
            else:
                #result[z]=int(result[z])
                pass
    return result

instance=None

class Worker(object):

    def __init__(self, event=None):
        self.ad_event1=threading.Event()
        self.buffer1=Queue.Queue()
        self.s1=Streamer(self.ad_event1, self.buffer1)
        self.ad_event2=threading.Event()
        self.buffer2=Queue.Queue()
        self.s2=Streamer(self.ad_event2, self.buffer2)
        self.current=self.buffer1
        self.debug=False
        self.debug_en=True
        #self.debug_break=True
        self.ad_switch=True
        self.t_prev_ad=time.time()
        self.songchanges=Queue.Queue()


    def start_vlc_imem(self):
        import sys, os
        sys.path.insert(0, os.path.join("..","..",".."))

        import extensions
        extensions.load_extension("vlc")
        
        global instance
        instance=extensions.get_extension("vlc").Instance('-vvv')

        import imem

        global q
        q=Queue.Queue()

        mm=imem.Media_Cast_Queue(instance, create_request(), q)
        p=instance.media_player_new()

        p.set_media(mm.get_media())

        def play():
            p.play()
        
        import threading
        threading.Timer(5, p.play, ()).start()
            


        return q
        

    def start_vlc_v2(self):
        import sys, os
        sys.path.insert(0, os.path.join("..","..",".."))

        import extensions
        extensions.load_extension("vlc")
        
        global instance
        instance=extensions.get_extension("vlc").get_default_instance()

        os.mkfifo("temp")

        m=instance.media_new("temp")
        p=instance.media_player_new()
        p.set_media(m)
        p.play()

        
        fifo=open("temp",'wb',0)
        def proc_shell():
            pass
        proc_shell.stdin=fifo
        proc=proc_shell

        
        return proc
        
        
        


    def start_vlc(self):
        path="vlc"
        if "win" in sys.platform:
            path="X:\\My Documents\\Projects\\VLC\\"+path
        proc=subprocess.Popen([path,"-","--verbose","3"
                                  #,"--aout","alsa"
                               #,"--file-caching","0" #Dont seem to work
                               #,"--network-caching","0" #Dont seem to work
                                  ], stdin=subprocess.PIPE
                              , bufsize=-1
                              )
        return proc

    def start_ffplay(self):
        proc=subprocess.Popen(["ffplay","-"
                               ,"-noinfbuf"
                                  #,"--aout","alsa"
                               #,"--file-caching","0" #Dont seem to work
                               #,"--network-caching","0" #Dont seem to work
                                  ], stdin=subprocess.PIPE
                              #, bufsize=6000 #Works apparently, dont know why# not sure of cause
                              )
        return proc

    def process(self):
        if self.slowdown:
            #print("Slowdown!")
            if self.current.qsize() < 120:
                return
        else:
            self.slowdown=time.time() - self.startuptime < 0 #Never true
        
        try:
            self.p=self.current.get(True, 5)
        except Queue.Empty:
            print("Empty queue for longer than 5 seconds!")
            return
        if self.p[3] and len(self.p[3]) == 4:
            self.p[3]=transform_time(transform_time(self.p[3],-1*self.offset_start), self.offset)
        data="".join(filter(None, self.p))
        self.proc.stdin.write(data)
        #print("Writing")
        self.f.write(data)
        if "onMetaData" in self.p[5]:
            print(read_metadata(self.p[5]))

    def process_v2(self):
        if self.slowdown:
            #print("Slowdown!")
            if self.streamers[self.cur].packets.qsize() < 120:
                return
        else:
            self.slowdown=time.time() - self.startuptime < 0 #Never true
        
        try:
            self.p=self.streamers[self.cur].packets.get(True, 5)
        except Queue.Empty:
            print("Empty queue for longer than 5 seconds!")
            return
        if self.p[3] and len(self.p[3]) == 4:
            self.p[3]=transform_time(transform_time(self.p[3],-1*self.offset_start), self.offset)
        data="".join(filter(None, self.p))
        self.proc.stdin.write(data)
        #print("Writing")
        #self.f.write(data)
        if "onMetaData" in self.p[5]:
            d=read_metadata(self.p[5])
            if "tlPreciseTime" in d and "StreamTitle" in d:
                correctedtime=self.streamers[self.cur].start_time+int(d["tlPreciseTime"])
                self.songchanges.put((correctedtime, d["StreamTitle"]))
            print(d)
            return True
        return False

    def process_v2_imem(self):
        if self.slowdown:
            #print("Slowdown!")
            if self.streamers[self.cur].packets.qsize() < 120:
                return
        else:
            self.slowdown=time.time() - self.startuptime < 0 #Never true
        
        try:
            self.p=self.streamers[self.cur].packets.get(True, 5)
        except Queue.Empty:
            print("Empty queue for longer than 5 seconds!")
            return
        if self.p[3] and len(self.p[3]) == 4:
            self.p[3]=transform_time(transform_time(self.p[3],-1*self.offset_start), self.offset)
        data="".join(filter(None, self.p))
        q.put(data)
        #print("Writing")
        #self.f.write(data)
        if "onMetaData" in self.p[5]:
            d=read_metadata(self.p[5])
            if "tlPreciseTime" in d and "StreamTitle" in d:
                correctedtime=self.streamers[self.cur].start_time+int(d["tlPreciseTime"])
                self.songchanges.put((correctedtime, d["StreamTitle"]))
            print(d)
            return True
        return False        
            
    def run_repeatable(self):
        self.streamers=[self.s1, self.s2]
        self.cur=0
        self.streamers[self.cur].start()
        self.startuptime=int(time.time())
        #self.proc=self.start_ffplay()
        self.proc=self.start_vlc_imem()
        adcoming=False
        self.delay=30
        self.offset=0
        self.offset_start=0
        self.p=None
        #self.f=open("stream.flv",'wb')
        self.slowdown=False
        self.stdinwrite_speed=0

        while True:
            self.delayer = time.time()-self.t_prev_ad > self.delay
            self.trackswitch = self.process_v2_imem()
            if self.ad_switch and self.delayer and self.streamers[self.cur].event.is_set():
            #if self.trackswitch:
                self.streamers[self.cur].event.clear()
                self.t_prev_ad=time.time()
                print("Ad!")
                self.prospect=self.cur+1 if self.cur < len(self.streamers)-1 else 0
                if self.cur==self.prospect:
                    print("Current and prospect streamers appear to be the same object.")
                self.streamers[self.prospect].start()
                self.streamers[self.prospect].packets.get(True)
                self.streamers[self.prospect].packets.get(True)
                self.p2=self.streamers[self.prospect].packets.get(True)
                tries=0
                maxtries=500
                while tries<maxtries:
                    #Currently the fastest: 160:
                    tries=tries+1
                    if self.p[5]==self.p2[5]:
                        print("Switching to thread %s. Succesful in %s tries" % (self.prospect, tries))
                        self.streamers[self.cur].stop()
                        self.cur=self.prospect
                        self.offset=get_time(self.p[3])
                        self.offset_start=get_time(self.p2[3])
                        break
                    else:
                        #print("Not similar, rechecking...\n%r\n%r"%(p[5],p2[5]))
                        self.p2=self.streamers[self.prospect].packets.get(True)
                        #p2=self.buffer2.get(True)
                        #process()
                if not tries<maxtries:
                    print("Failed to interlace stream in thread %s..." % self.prospect)
                    self.streamers[self.prospect].stop()

        #self.streamers[self.current].stop()
        self.proc.kill()
        #self.f.close()

    def run(self):
        self.s1.start()
        self.stream_starttime=int(time.time())
        #time.sleep(10)
        self.proc=self.start_ffplay()
        adcoming=False
        self.delay=30
        self.offset=0
        self.offset_start=0
        self.p=None
        f=open("stream.flv",'wb')
        self.slowdown=False
        self.startuptime=time.time()
        self.stdinwrite_speed=0
        #self.stdinwrite_speed
        while True:
            def process(t=None):
                if self.slowdown:
                    #print("Slowdown!")
                    if self.current.qsize() < 120:
                        return
                else:
                    self.slowdown=time.time() - self.startuptime < 0 #Never true
                
                try:
                    self.p=self.current.get(True, 5)
                except Queue.Empty:
                    print("Empty queue for longer than 5 seconds!")
                    return
                if self.p[3] and len(self.p[3]) == 4:
                    self.p[3]=transform_time(transform_time(self.p[3],-1*self.offset_start), self.offset)
                data="".join(filter(None, self.p))
                self.proc.stdin.write(data)
                #print("Writing")
                f.write(data)
                if "onMetaData" in self.p[5]:
                    print(read_metadata(self.p[5]))
                    
                #time.sleep(0.04) # works quickest! but greatly delays playing...
            process()
            self.delayer = time.time()-self.t_prev_ad > self.delay
            if self.ad_switch and self.delayer and self.ad_event1.is_set():
                def switch():
                    self.t_prev_ad=time.time()
                    self.delay=time.time()
                    print("Ad!")
                    self.s2.start()
                    self.buffer2.get(True)
                    self.buffer2.get(True)
                    self.p2=self.buffer2.get(True) # Third packet is significant
                    tries=0
                    maxtries=500
                    while tries<maxtries:
                        #Currently the fastest: 160:
                        tries=tries+1
                        if self.p[5]==self.p2[5]:
                            print("Switching to thread 2. Succesful in %s tries" % tries)
                            self.current=self.buffer2
                            self.s1.stop()
                            self.offset=get_time(self.p[3])
                            self.offset_start=get_time(self.p2[3])
                            break
                        else:
                            #print("Not similar, rechecking...\n%r\n%r"%(p[5],p2[5]))
                            self.p2=self.buffer2.get(True)
                            #p2=self.buffer2.get(True)
                            #process()
                    if not tries<maxtries:
                        print("Failed to grasp stream in thread 2...")
                switch()
                
        f.close()
        self.proc.kill()

   
w=Worker()
w.run_repeatable()        


#Runs slowest, because pulling p2 twice as fast is probably slower...
##                tries=0
##                maxtries=500
##                while tries<maxtries:
##                    tries=tries+1
##                    if p[5]==p2[5]:
##                        print("Switching to thread 2. Succesful in %s tries" % tries)
##                        self.current=self.buffer2
##                        self.s1.stop()
##                        global self.offset
##                        self.offset=get_time(p[3])
##                        global self.offset_start
##                        self.offset_start=get_time(p2[3])
##                        break
##                    else:
##                        print("Not similar, rechecking...\n%r\n%r"%(p[5],p2[5]))
##                        p2=self.buffer2.get(True)
##                        p2=self.buffer2.get(True)
##                        process()

        
