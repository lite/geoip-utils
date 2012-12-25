#!/usr/bin/env python
# -*- coding=utf-8 -*- 

# http://www.ywjt.org/index/archives/746.html
# http://dev.maxmind.com/geoip/geolite
# Geo-Region：省份，22＝BEIJING＝北京

import os.path
import re
import pygeoip
from subprocess import Popen, PIPE, STDOUT

from sqlalchemy import *

url="http://ip.taobao.com/service/getIpInfo.php?ip="

gi = pygeoip.GeoIP("./data/GeoLiteCity.dat", pygeoip.MEMORY_CACHE)

def get_login_ipaddrs(host, table, user, passwd, sqltext):
    db = create_engine('mysql://%s:%s@%s/%s?charset=utf8'%(user, passwd, host, table),  echo=False)
    conn = db.connect()
    c = conn.execute(sqltext)
    entries = [row['f_ip'] for row in c.fetchall()]
    conn.close()
    return entries
    
def get_player_ip(sid):
    #sqltext = "select f_ip from gm_login_num where f_login_time > DATE_SUB(CURDATE(), INTERVAL 3 DAY);"
    sqltext = "select f_ip from gm_login_num;"
    return get_login_ipaddrs("192.168.1.21", "webgame_%s"%(sid), "webgame", "game", sqltext)
    
# def get_player_ip():
#     #cmd_netstat = " netstat -nat | grep ESTABLISHED | awk '{split($4,a,\":\"); a[1]}' "
#     cmd_netstat = "netstat -ant | grep ESTABLISHED | grep 44"
#     output,error = Popen(cmd_netstat, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT).communicate()
#     ipaddrs = []
#     for m in re.finditer('(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})[\.|:]\d+\s+ESTABLISHED', output):
#         ipaddrs += [m.group(1)]
#     return ipaddrs
    
def count_ip(ipaddrs, city):
    count = 0
    ips = []
    for ip in ipaddrs:
        ret = ip_detail(ip)
        if  ret == city:
            ips += [ip]
    return city, len(ipaddrs), len(ips), ips
    
def ip_detail(ip):
    ret = gi.record_by_addr(ip)
    return ret["city"]

def main():
    #print count_ip(["125.70.82.110", "1.203.190.72", "1.203.146.200", "115.171.255.52", "222.128.174.241", "1.203.148.176", "125.70.81.240", "123.124.2.85"], "Beijing")
    print count_ip(["115.170.86.204", "114.249.229.33", "114.250.168.29", "122.85.158.181"], "Beijing")
    return
    for sid in ['s8','s11','s12']:
    #for sid in ['s8']:
        ipaddrs = get_player_ip(sid)
        print count_ip(ipaddrs, "Beijing")
    
if __name__ == '__main__':
    main()
