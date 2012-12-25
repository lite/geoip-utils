#!/usr/bin/env python
# coding: utf-8

'''用Python脚本查询纯真IP库

QQWry.Dat的格式如下:

+----------+
|  文件头  |  (8字节)
+----------+
|  记录区  | （不定长）
+----------+
|  索引区  | （大小由文件头决定）
+----------+

文件头：4字节开始索引偏移值+4字节结尾索引偏移值

记录区： 每条IP记录格式 ==> IP地址[国家信息][地区信息]

   对于国家记录，可以有三种表示方式：

       字符串形式(IP记录第5字节不等于0x01和0x02的情况)，
       重定向模式1(第5字节为0x01),则接下来3字节为国家信息存储地的偏移值
       重定向模式(第5字节为0x02),
   
   对于地区记录，可以有两种表示方式： 字符串形式和重定向

   最后一条规则：重定向模式1的国家记录后不能跟地区记录

索引区： 每条索引记录格式 ==> 4字节起始IP地址 + 3字节指向IP记录的偏移值

   索引区的IP和它指向的记录区一条记录中的IP构成一个IP范围。查询信息是这个
   范围内IP的信息

'''

import sys
import socket
from struct import pack, unpack

class IpInfo:
    pass
    
class WryDat():
    def load(self, dbname):
        f = file(dbname, 'r')
        self.img = f.read()
        f.close()
        (self.first_idx, self.last_idx) = unpack('II', self.img[:8])
        self.load_indexes()
        
    def get_iprange(self, idx):
        next_idx = idx + 4
        iprange = unpack('I', self.img[idx:idx+4])[0]
        return iprange, next_idx
            
    def get_addr_by_offset(self, idx):
        next_idx = idx + 3
        offset = unpack("I", self.img[idx:idx+3]+"\0")[0]
        #print hex(idx), hex(next_idx)
        byte = ord(self.img[offset])
        if byte == 0x01 or byte == 0x02:
            addr = self.get_addr_by_offset(offset+1)[0]
        else:
            addr = self.get_addr_by_string(offset)[0]
        return addr, next_idx
       
    def get_addr_by_string(self, idx): 
        next_idx = self.img.find('\0', idx)+1
        #print hex(idx), hex(next_idx)
        try:
            area_utf8 = unicode(self.img[idx:next_idx],'gbk').encode('utf-8')
            #print area_utf8
            return area_utf8, next_idx
        except:
            pass
        return "", next_idx
        
    def load_ipinfo(self, offset):
        ipinfo = IpInfo()

        ipinfo.iprange, idx = self.get_iprange(offset)
        byte = ord(self.img[idx])
        if byte == 0x01:
            ipinfo.country, idx = self.get_addr_by_offset(idx+1)
            ipinfo.area = ""
        else:
            if byte == 0x02:
                ipinfo.country, idx = self.get_addr_by_offset(idx+1)
            else:
                ipinfo.country, idx = self.get_addr_by_string(idx)
            
            byte = ord(self.img[idx])
            if byte == 0x01 or byte == 0x02:
                ipinfo.area, idx = self.get_addr_by_offset(idx+1)
            else:
                ipinfo.area, idx = self.get_addr_by_string(idx)
            
        return ipinfo
        
    def load_indexes(self):
        self.indexes = []
        idx = self.first_idx
        while idx <= self.last_idx:
            (ipaddr, offset) = unpack("II", self.img[idx:idx+7]+"\0")
            idx += 7
            ipinfo = self.load_ipinfo(offset)
            self.indexes += [(ipaddr, ipinfo)]

    def save(self, newdb):
        countries = {}
        areas = {}
        new_img = ""
        # records
        for i in xrange(len(self.indexes)):
            ipinfo = self.indexes[i][1]
            idx = len(new_img) + 8
            ipinfo.offset = idx
            new_img += pack("I", ipinfo.iprange)
            if(countries.has_key(ipinfo.country)):
                offset = countries[ipinfo.country]
                new_img += chr(0x02) if len(ipinfo.area)>0 else chr(0x01)
                new_img += pack("I", offset)[0:3]
            else:
                countries[ipinfo.country] = idx +4
                new_img += ipinfo.country
            
            if len(ipinfo.area)>0:
                if(areas.has_key(ipinfo.area)):
                    offset = areas[ipinfo.area]
                    new_img += chr(0x02)
                    new_img += pack("I", offset)[0:3]
                else:
                    areas[ipinfo.area] = idx +4
                    new_img += ipinfo.area

        # indexes
        first_idx = len(new_img) + 8
        for i in xrange(len(self.indexes)):
            new_img += pack("II", self.indexes[i][0], self.indexes[i][1].offset)[0:7]
        # header
        last_idx = first_idx + 7 * len(self.indexes)
        new_img = pack('II', first_idx, last_idx) + new_img;
        f = file(newdb, 'w')
        f.write(new_img)
        f.close()
        
            
if __name__ == '__main__':
    wry = WryDat()
    wry.load("qqwry.dat.gbk")
    wry.save("qqwry.dat")