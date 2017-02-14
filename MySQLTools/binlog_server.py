# -*- coding: utf-8 -*-

import random, argparse, sys, os

#1.封装mysqlbinlog远程备份操作
#2.支持断开尝试重新链接操作
#3.在备份目录随机生成一个server_id
#4.如果备份目录已经有文件了，就不需要从头开始获取binlog了
#5.支持读取配置文件
#6.mysqlbinlog获取事件后，并不会实时落盘，而是先保存在本地服务器的内存中，每4K刷盘一次

mysqlbinlog = "/opt/mysql-5.7/bin/mysqlbinlog -h{0} -u{1} -p{2} -P{3} --stop-never --raw " \
              "--read-from-remote-server --stop-never-slave-server-id={4} --result-file={5} {6}"

server_id = 0

def check_arguments():
    global server_id
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", type=str, dest="host", help="mysql host")
    parser.add_argument("--port", type=int, dest="port", help="mysql port", default=3306)
    parser.add_argument("--user", type=str, dest="user", help="mysql user")
    parser.add_argument("--password", type=str, dest="password", help="mysql password")
    parser.add_argument("--file-path", type=str, dest="file_path", help="save binlog directory")
    parser.add_argument("--conf-file", type=str, dest="conf_file", help="configuration file")
    args = parser.parse_args()

    if(not args.conf_file or args.conf_file == None):
        if not args.host or not args.user or not args.password or not args.file_path or len(args.file_path) <= 0:
            print(parser.format_usage())
            sys.exit(1)
    else:
        read_conf_file(args)
    if(server_id <= 0):
        server_id = random.randint(88888,99999)
    return args

def read_conf_file(args):
    if(os.path.exists(args.conf_file)):
        pass
    else:
        print("配置文件不存在...")
        sys.exit(1)

def get_binlog_file_name(args):
    pass

if(__name__ == "__main__"):
    args = check_arguments()
    print("开始远程备份binlog...")
    binlog_backup = mysqlbinlog.format(args.host, args.user, args.password, args.port, server_id, args.file_path, get_binlog_file_name(args))
    print(binlog_backup)
    os.system(binlog_backup)