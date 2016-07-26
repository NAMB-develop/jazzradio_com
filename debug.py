#debug

import urllib2

url="http://pub8.jazzradio.com:80/jr_bossanova_aacplus.flv"
referer="http://www.jazzradio.com/bossanova"
useragent="Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36"

req=urllib2.Request(url)
req.add_header("Referer":referer)
req.add_header("User-Agent":useragent)
stream=urllib2.urlopen(req)


import time
while TrueL
    content=stream.read(8196)
    if not content:
        break
    
