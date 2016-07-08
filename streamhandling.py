import urllib2

def create_request():
    req=urllib2.Request("http://pub8.jazzradio.com/jr_pariscafe_aacplus.flv")
    req.add_header('Referer','http://www.jazzradio.com/pariscafe')
    req.add_header('User-Agent',"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36")
    return req

def create_stream(req):
    return urllib2.urlopen(req)

def find_start(data):
    result=0
    offset=0
    while True:
        t=data.index('\x08', offset)
        size=int(data[t+1:t+1+3].encode('hex'), 16)
        if data[t+11+size+4]=='\x08' or data[t+11+size+4]=='\x12':
            return t
        else:
            offset=t+1

def break_packets(data, offset=0):
    packets=[]
    i=data.index('\x08', offset)
    size=int(data[i+1:i+1+3].encode('hex'),16)
    if data[i+11+size+4]=='\x08' or data[i+11+size+4]=='\x12':
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

def read_header(data):
    i=0
    s=data[i:i+3]
    i=i+3
    one_byte=data[i]
    i=i+1
    audio_byte=data[i]
    i=i+1
    header_size=int(data[i:i+4].encode('hex'),16)

def process_packet(data):
    t=0
    if len(data) < 15:
        return None
    try:
        prev_size=int(data[t:t+4].encode('hex'),16)
    except ValueError:
        print("%r"%data)
    t=t+4
    if data < 5:
        return None
    typ=data[t]
    t=t+1
    size=int(data[t:t+3].encode('hex'),16)
    if t+size+8 > len(data):
        return None
    t=t+3
    time=int((data[t+3]+data[t:t+3]).encode('hex'), 16)
    t=t+4
    stream_id=data[t:t+3]
    t=t+3
    payload=data[t:t+size]
    total_length=t+size
    p=[prev_size,typ,size,time,stream_id,payload,data[:total_length],total_length]
    return p

def run():
    stream=create_stream(create_request())
    header=stream.read(9)
    chunk=""
    index=0
    while True:
        print("Fetching chunk:")
        chunk=chunk+stream.read(8196)
        while True:
            p=process_packet(chunk)
            index=index+1 if index < len(packets)-1 else 0
            if p:
                i=p[-1]
                packets[index]=p
            else:
                break
            chunk=chunk[i:]

packets=[None]*1024

import threading

class Streamer(object):

    def __init__(self, event, packets):
        self.packets=packets
        self.event=event
        self.stop=threading.Event()
        self.thread=None

    def stop(self):
        print("Stopping thread")
        self.stop.set()

    def start(self):
        print("Starting thread")
        if not self.thread:
            self.thread=threading.Thread(target=self.run)
            self.thread.daemon=True
            self.thread.start()

    def run(self):
        self.stream=create_stream(create_request())
        header=self.stream.read(9)
        self.packets.put([0,0,0,0,0,"",header])
        print("%r"%header)
        chunk=""
        index=0
        while not self.stop.is_set():
            print("Fetching chunk:")
            chunk=chunk+self.stream.read(8196)
            if "adswizz" in chunk:
                print("Ad coming up")
                self.event.set()
            while True:
                p=process_packet(chunk)
                if p:
                    i=p[-1]
                    self.packets.put(p)
                    #self.packets[index]=p
                    #index=index+1 if index < len(self.packets)-1 else 0
                else:
                    break
                chunk=chunk[i:]
        self.stream.close()

import Queue, subprocess

class Worker(object):

    def __init__(self):
        self.ad_event1=threading.Event()
        self.buffer1=Queue.Queue()
        self.s1=Streamer(self.ad_event1, self.buffer1)
        self.ad_event2=threading.Event()
        self.buffer2=Queue.Queue()
        self.s2=Streamer(self.ad_event2, self.buffer2)
        self.current=self.buffer1

    def run(self):
        process=subprocess.Popen(["X:\\My Documents\\Projects\\VLC\\vlc","-"], stdin=subprocess.PIPE)
        self.s1.start()
        adcoming=False
        while True:
            p=self.current.get(True)
            process.stdin.write(p[6])
            if "adswizz" in p[5]:
                print("Ad!")
                self.s2.start()
                adcoming=True
            if adcoming:
                if not self.buffer2.empty():
                    p2=self.buffer2.get()
                    if p[5]==p2[5]:
                        self.current=self.buffer2
                        adcoming=False
                        self.s1.stop()
                #self.s1.stop()
                #process.kill()
        
w=Worker()
w.run()
        
        

        
