# geoip-utils

download [GeoIP.dat and GeoLiteCity.dat](www.maxmind.com/download/geoip/database/)
download [qqwry.rar](http://update.cz88.net/soft/qqwry.rar)

convert qqwry.dat.gbk to qqwry.dat(utf8)

    python qqwry_iconv.py
    
search ip by qqwry.dat

    python qqwry.py 114.112.57.180
    
search ip by geoip

    pip install pygeoip
    python ip.py