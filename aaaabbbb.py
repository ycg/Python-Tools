# -*- coding: utf-8 -*-

from __future__ import with_statement
from PyWapFetion import Fetion, send2self, send
# 仅作参考，详细了解请参考源码

# 快速发送：
send2self('手机号',  '密码', '信息')
send('手机号', '密码', '接收方手机号', '信息')


'''
print("分级方法和方法恢复")

aa = "  eth0: 319951426860 1397751285    0    0    0     0          0         0 284464809982 1100636227    0    0    0     0       0          0"

abb = []
list_a = aa.split(" ")
print(list_a)
for value in list_a:
    if(len(value) > 0):
        abb.append(value)

print(abb)
print(abb[1],abb[9])
#print(list_a[0].split(":")[1])'''