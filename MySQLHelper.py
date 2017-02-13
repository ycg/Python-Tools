import MySQLdb
import time, threading, string, os, sys

#使用数据库连接池
from MySQLdb.cursors import DictCursor
from DBUtils.PooledDB import PooledDB

class Data:
    pass

'''执行SQL返回List对象'''
def executeToList(sql, host_info):
    conn = None
    try:
        conn = getMySQLConnection(host_info)
        cursor = conn.cursor()
        result = cursor.execute(sql)
        data = []
        for row in cursor.fetchall():
            rowData = Data()
            for key, value in row.items():
                setattr(rowData, key, value)
            data.append(rowData)
        return data
    finally:
        if (conn != None):
            conn.close()
    return None

'''执行Show Status返回字典对象'''
def executeToShowStatus(sql, host_info):
    data = {}
    conn = None
    try:
        conn = getMySQLConnection(host_info)
        cursor = conn.cursor()
        result = cursor.execute(sql)
        for row in cursor.fetchall():
            data[row.get("Variable_name")] = row.get("Value")
        return data
    finally:
        if (conn != None):
            conn.close()
    return None

'''获取MySQL链接'''
def getMySQLConnection(host_info):
    if(connection_pools.get(host_info.key) == None):
        pool = PooledDB(creator=MySQLdb, mincached=1, maxcached=20,
                        host=host_info.ip, port=host_info.port, user=host_info.user, passwd=host_info.password,
                        db="mysql", use_unicode=False, charset="utf8", cursorclass=DictCursor)
        connection_pools[host_info.key] = pool
    return connection_pools[host_info.key].connection()