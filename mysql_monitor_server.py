# -*- coding: utf-8 -*-

'''
#1.提高在后台一直监测数据库，最基本的监控mysql status
#2.提供监测磁盘的功能，比如单表增长过快，需要进行邮件提醒
#3.提供本地客户端登录，也就是链接数据库即可
#4.所有的监控数据都进行入库处理
#5.支持指定cpu或者线程数大于多少记录mysql信息，如果processlist trx innodb status等等
#6.提供各种命令状态去查看数据库情况
    1.增长最快的前十个表
    2.表体积最大的前十个表
    3.各种资源利用率的前十数据
    4.数据库体积前十

select table_schema, table_name, concat(round(data_length/1024/1024,2), "M") as 数据大小
from information_schema.tables
where table_schema != 'mysql' and table_schema != 'information_schema' and table_schema != 'performation_schema'
and data_length > 1024 * 1024 * 100 order by data_length desc limit 100;


select table_schema, table_name, concat(round(index_length/1024/1024,2), "M") as 索引大小
from information_schema.tables
where table_schema != 'mysql' and table_schema != 'information_schema' and table_schema != 'performation_schema'
and index_length > 1024 * 1024 * 100 order by index_length desc limit 100;

1.每次获取status之后就通过线程把数据写入到数据库
'''

