import urllib as urllib
import socket

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
        b'GET /jr_pariscafe_aacplus.flv HTTP/1.1',
        b'Host: www.jazzradio.com',
        b'Referer: http://www.jazzradio.com/pariscafe',
        b'User-Agent: Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36',
        b'Connection: keep-alive',
        b'',
        b''
        ]
    s.send(b"\r\n".join(req))
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
        print("Epic fail")
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
    p=[None]*8
    t=0
    if len(data) < 15:
        return p
    p[0]=struct.unpack(">I",data[t:t+4])[0]

    t=t+4
    p[1]=data[t:t+1]
    if not p[1] in at:
        return p

    t=t+1
    p[2]=struct.unpack(">I",bytearray("\x00")+data[t:t+3])[0]
    if t+p[2]+8 > len(data):
        return p

    t=t+3
    p[3]=struct.unpack(">I",data[t+3:t+4]+data[t:t+3])[0]

    t=t+4
    p[4]=data[t:t+3]

    t=t+3
    p[5]=data[t:t+p[2]]

    p[7]=t+p[2]
    #print("size: %s"%total_length)
    p[6]=data[:p[7]]
    #p=[prev_size,typ,size,time,stream_id,payload,data[:total_length],total_length]
    return p

packets=[None]*1024

import threading

class Streamer(object):

    def __init__(self, event, packets):
        self.packets=packets
        self.event=event
        self.stopper=threading.Event()
        self.thread=None
        self.f=open("stream.bin",'wb')

    def stop(self):
        print("Stopping thread")
        self.stopper.set()
        self.f.close()

    def start(self):
        print("Starting thread")
        if not self.thread:
            self.thread=threading.Thread(target=self.run)
            self.thread.daemon=True
            self.thread.start()

    def run(self):
        self.stream=create_stream_core(create_request_core())
        http_header=self.stream.recv(129)
        header=self.stream.recv(9)
        self.packets.put([0,0,0,0,0,"",header])
        self.f.write(header)
        print("%r"%header)
        chunk=bytearray(b'')
        index=0
        last_suc=None
        while not self.stopper.is_set():
            #print("Fetching chunk:")
            d=self.stream.recv(8196)
            self.f.write(d)
            chunk.extend(d)
            if chunk:
                if b"adswizz" in chunk:
                    print("Ad coming up")
                    self.event.set()
                while True:
                    p=process_packet(chunk)
                    #print("Packet type: %r"%p[1])
                    if p[-1]:
                        #print("succes!")
                        i=p[-1]
                        if len(chunk)>i+4:
                            if not chunk[i+4:i+5] in at:
                                print("Whats wrong with this part?\n%r"%chunk[:i])
                        if len(chunk)==i:
                            print("Whats wrong with this part ?\n%r"%chunk[:i])
                        last_suc=p
                        self.packets.put(p)
                        chunk=chunk[i:]
                    else:
                        #print("fail: %r"%p)
                        #print("%r"%p)
                        if p[1]:
                            if not p[1] in at:
                                #print("Failed to create packet from chunk (trimmed):\n%r"%chunk[0:13])
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
                            else:
                                if p[2]:
                                    #print("Too short!")
                                    pass
                                else:
                                    #print("Dont know what happened: %r"%chunk)
                                    pass
                            break
                        else:
                            #print("Failed to create packet from chunk:\n%r"%chunk)
                            #print("\n%r"%p)
                            break
                    #chunk=chunk[i:]
        self.stream.close()

import queue as Queue
import subprocess, time, sys

class Worker(object):

    def __init__(self, event=None):
        self.ad_event1=threading.Event()
        self.buffer1=Queue.Queue()
        self.s1=Streamer(self.ad_event1, self.buffer1)
        self.ad_event2=threading.Event()
        self.buffer2=Queue.Queue()
        self.s2=Streamer(self.ad_event2, self.buffer2)
        self.current=self.buffer1
        self.debugevent=threading.Event()
        self.debugevent.set()
        self.init=time.time()

    def run(self):
        path="vlc"
        if "win" in sys.platform:
            path="X:\\My Documents\\Projects\\VLC\\"+path
        process=subprocess.Popen([path,"-","--verbose","3","--aout","alsa"], stdin=subprocess.PIPE, bufsize=-1)
        self.s1.start()
        adcoming=False
        delay=30
        
        while True:
            try:
                p=self.current.get(True, 5)
            except Queue.Empty:
                print("Empty queue for longer than 5 seconds!")
            process.stdin.write(p[6])
            print("%r"%p[5])
            #print("Written from s1: %s"%p[-1])
            if "adswizz" in str(p[5]) or self.debugevent.is_set():
                self.debugevent.clear()
                if time.time()-self.init > delay:
                    self.init=time.time()                 
                    print("Ad!")
                    self.s2.start()
                    while True:
                        p2=self.buffer2.get(True)
                        #print("Written from s2: %s"%p2[-1])
                        if p[5]==p2[5]:
                            self.current=self.buffer2
                            self.s1.stop()
                            break

   
w=Worker()
w.run()
        
        

        
