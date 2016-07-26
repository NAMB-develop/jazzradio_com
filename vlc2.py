import subprocess
import urllib2


##req=urllib2.Request("http://icecast.omroep.nl/radio4-bb-mp3")
##stream = urllib2.urlopen(req)
##
##req=urllib2.Request("http://pub8.jazzradio.com:80/jr_bossanova_aacplus.flv")
##req.add_header("User-Agent","Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36")
##req.add_header("Referer","http://www.jazzradio.com/bossanova")
##stream = urllib2.urlopen(req)
##
##player = subprocess.Popen(['cvlc','-'], stdin=subprocess.PIPE)
##totaldata=""
##while True:
##    data=stream.read(8196)
##    totaldata=totaldata+data
##    print(len(data))
##    if not data:
##        break
##    player.stdin.write(data)

f=open("bn.bin",'r')
data=f.read()
f.close()

def bytestring_to_int(bytestring):
    return int(bytestring.encode('hex'), 16)

def read_stream(data):
    data[0:3]='FLV'
    data[3]="\x01"
    data[4]="\x04" #audio
    data[5:9]=int("\x00\x00\x00\t".encode('hex')) #9, header size
    #packet start
    data[9:13]=int("\x00\x00\x00\x00".encode('hex')) #0, size of previous packet
    data[13]="\x12" #18, AMF metadata
    data[14:17]="\x00\x00\xae" #payload size
    data[17:20]="\x00\x00\x00" #Timestamp, null for first packet
    data[20]="\x00" #extender for timestamp
    data[21:24]="\x00\x00\x00" #stream ID. Null for first of same type
        #payload start
    index=24+bytestring_to_int(data[14:17])
    payload_data=data[24:index]
    
    #packet 2 start
    size_prev=bytestring_to_int(data[index:index+4])
    index=index+4
    packet_type=data[index] #8, audio
    index=index+1
    payload_size=bytestring_to_int(data[index:index+3])
    index=index+3
