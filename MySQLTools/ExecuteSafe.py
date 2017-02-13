#主要是针对update，delete操作，防止误操作
#那么就要进行原始数据备份，然后再执行相关update和delete操作
#还有一个工具就是说自动识别主库还是从库，防止在从库执行误操作

import time, argparse, sys, pymysql, datetime
from pymysqlreplication import BinLogStreamReader
from pymysqlreplication.row_event import WriteRowsEvent, UpdateRowsEvent, DeleteRowsEvent

connection_settings = {}
insert_sql = "INSERT INTO `{0}`.`{1}` ({2}) VALUES ({3});"
update_sql = "UPDATE `{0}`.`{1}` set {2} WHERE {3};"
delete_sql = "DELETE FROM `{0}`.`{1}` WHERE {2};"

def sql_format(dic, split_value):
    list = []
    for key, value in dic.items():
        if(value == None):
            list.append("`%s`=null" % key)
            continue
        if(isinstance(value, int)):
            list.append("`%s`=%d" % (key, value))
        else:
            list.append("`%s`='%s'" % (key, value))
    return split_value.join(list)

def sql_format_for_insert(values):
    list = []
    for value in values:
        if (value == None):
            list.append("null")
            continue
        if (isinstance(value, int)):
            list.append('%d' % value)
        else:
            list.append('\'%s\'' % value)
    return ', '.join(list)

def check_arguments():
    global connection_settings
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", type=str, dest="host", help="mysql host")
    parser.add_argument("--port", type=int, dest="port", help="mysql port")
    parser.add_argument("--user", type=str, dest="user", help="mysql user")
    parser.add_argument("--password", type=str, dest="password", help="mysql password")
    parser.add_argument("--log-file", type=str, dest="log_file", help="")
    parser.add_argument("--start-file", type=str, dest="start_file", help="")
    parser.add_argument("--start-pos", type=int, dest="start_pos", help="")
    parser.add_argument("--end-pos", type=int, dest="end_pos", help="")
    parser.add_argument("--end-file", type=str, dest="end_file", help="")
    parser.add_argument("--out-file", type=str, dest="out_file", help="")
    parser.add_argument("--start-datetime", type=str, dest="start_datetime", help="")
    parser.add_argument("--end-datetime", type=str, dest="end_datetime", help="")
    parser.add_argument("-B", "--flashback", dest="flashback", help="", default=False, action='store_true')
    parser.add_argument('-d', '--databases', dest='databases', type=str, nargs='*', help='dbs you want to process', default='')
    parser.add_argument('-t', '--tables', dest='tables', type=str, nargs='*', help='tables you want to process', default='')
    args = parser.parse_args()

    if not args.host or not args.user or not args.password:
        print(parser.format_usage())
        sys.exit(1)
    if(not args.port):
        args.port = 3306
    if(not args.out_file):
        args.out_file = "/tmp/binlog.sql"
    if(not args.start_pos):
        args.start_pos = 0
    args.tables = args.tables if args.tables else None
    args.start_pos = args.start_pos if args.start_pos else 4
    args.end_pos = args.end_pos if args.end_pos else None
    args.databases = args.databases if args.databases else None
    args.start_datetime = datetime.datetime.strptime(args.start_datetime, "%Y-%m-%d %H:%M:%S") if args.start_datetime else None
    args.end_datetime = datetime.datetime.strptime(args.end_datetime, "%Y-%m-%d %H:%M:%S") if args.end_datetime else None
    connection_settings = {'host': args.host, 'port': args.port, 'user': args.user, 'passwd': args.password}

    conn = None
    cursor = None
    try:
        conn = pymysql.connect(**connection_settings)
        cursor = conn.cursor()
        cursor.execute("select @@server_id;")
        args.server_id = cursor.fetchone()[0]
        if(not args.log_file):
            cursor.execute("show master status;")
            args.log_file = cursor.fetchone()[0]
    finally:
        if(cursor != None):
            cursor.close()
        if(conn != None):
            conn.close()
    return args


if(__name__ == "__main__"):
    args = check_arguments()
    start_time = time.time()