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
    return p

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
