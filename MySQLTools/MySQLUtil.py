# -*- coding: utf-8 -*-

import MySQLdb
import MySQLdb.converters


'''
1.执行sql的功能
2.执行sql工具，返回数据，比如list或者单行数据
3.返回的数据库是字典还是list这个要写明，注意调用不同的cursor会返回不同的数据类型
4.insert的时候要注意单引号问题，如果是拼接的要手动，直接执行的可以不要写，也就是字符转移问题
5.注意python的None和mysql的NULL的互换
6.
'''

def execute(sql):
    pass

def execute_fetch_all(sql):
    pass

def execute_fetch_one(sql):
    pass

def get_connection(host_info):
    return get_connection(host_info.ip, host_info.port, host_info.user, host_info.password)

def get_connection(ip, port, user, password):
    return MySQLdb.connect(host=ip, port=port, user=user, passwd=password, charset="utf8")

def close(connection, cursor):
    if(cursor != None):
        cursor.close()
    if(connection != None):
        connection.close()

def convert_to_null(value):
    if(value == None):
        result = None
        result = MySQLdb.converters.None2NULL(value, result)
        return result
    return value

'''转换变量为MySQL整形类型'''
def convert_value_to_int(value):
    if(value == None):
        return convert_to_null(value)
    else:
        return value

'''把变量转换成MySQL字符串类型'''
def convert_value_to_str(value):
    if(value == None):
        return convert_to_null(value)
    else:
        return ("'%s'" % value)