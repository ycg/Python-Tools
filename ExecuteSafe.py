# -*- coding: utf-8 -*-

#主要是针对update，delete，drop table操作，防止误操作
#那么就要进行原始数据备份，然后再执行相关update和delete操作
#还有一个工具就是说自动识别主库还是从库，防止在从库执行误操作

import time, argparse, sys

def check_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", type=str, dest="host", help="mysql host", default="")
    parser.add_argument("--port", type=int, dest="port", help="mysql port", default=3306)
    parser.add_argument("--user", type=str, dest="user", help="mysql user", default="")
    parser.add_argument("--password", type=str, dest="password", help="mysql password", default="")

    parser.add_argument("--backup-host", type=str, dest="backup host", help="backup mysql host", default="")
    parser.add_argument("--backup-port", type=int, dest="backup port", help="backup mysql port", default=3306)
    parser.add_argument("--backup-user", type=str, dest="backup user", help="backup mysql user", default="")
    parser.add_argument("--backup-password", type=str, dest="backup password", help="backup mysql password", default="")
    parser.add_argument("--backup-table-name", type=str, dest="backup table name", help="backup table name", default="")

    parser.add_argument("--sql", type=str, dest="execute sql", help="input execute sql")
    args = parser.parse_args()

    args.host="192.168.1.13"

    return args

def execute_backup(sys_args):
    #要进行sql解析
    #要进行sql判断，是否是update，还是delete，还是执行drop table操作
    #要把数据进行备份，要根据原始的表结构，字段新建一张表，然后导入数据
    #表名可以通过参数给定，也可以代码自动生成
    execute_sql = sys_args.sql.strip()
    print(execute_sql)
    pass

if(__name__ == "__main__"):
    args = check_arguments()
    print(args)
    start_time = time.time()
    print("start...")