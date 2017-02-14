# -*- coding: utf-8 -*-

import random, argparse, sys, os, commands, time

#1.封装mysqlbinlog远程备份操作
#2.支持断开尝试重新链接操作
#3.在备份目录随机生成一个server_id
#4.如果备份目录已经有文件了，就不需要从头开始获取binlog了
#5.支持读取配置文件
#6.mysqlbinlog获取事件后，并不会实时落盘，而是先保存在本地服务器的内存中，每4K刷盘一次
#python binlog_server.py --host=192.168.11.128 --user=yancg --password=123456 --port=3310 &


path = "/opt/mysql-5.7/bin/"
mysql = path + "mysql -h{0} -u{1} -p\'{2}\' -P{3} -e\"{4}\" | head -n2 | tail -n 1 | awk \'{5}\'"
mysqlbinlog = path + "mysqlbinlog -h{0} -u{1} -p{2} -P{3} --stop-never --raw " \
                     "--read-from-remote-server --stop-never-slave-server-id={4} --result-file={5} {6} &>> {7}"

def check_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", type=str, dest="host", help="mysql host")
    parser.add_argument("--port", type=int, dest="port", help="mysql port", default=3306)
    parser.add_argument("--user", type=str, dest="user", help="mysql user")
    parser.add_argument("--password", type=str, dest="password", help="mysql password")
    parser.add_argument("--file-path", type=str, dest="file_path", help="save binlog directory", default="")
    parser.add_argument("--conf-file", type=str, dest="conf_file", help="configuration file", default="")
    parser.add_argument("--server-id", type=int, dest="server_id", help="server id")
    parser.add_argument("--log-file", type=str, dest="log_file", help="log file path", default="/tmp/binlog.log")
    args = parser.parse_args()

    if(not args.conf_file or args.conf_file == None):
        if(not args.host or not args.user or not args.password):
            print(parser.format_usage())
            sys.exit(1)
    else:
        read_conf_file(args)
    if(not args.server_id or args.server_id <= 0):
        args.server_id = random.randint(88888,99999)
    if(len(args.file_path) <= 0):
        args.file_path = os.getcwd() + "/"
    return args

def read_conf_file(args):
    if(os.path.exists(args.conf_file)):
        pass
    else:
        print("配置文件不存在...")
        sys.exit(1)

def get_binlog_file_name(args):
    files = os.listdir(args.file_path)
    file_count = len(files)
    if(file_count == 0):
        binglog_name = get_first_binlog_file_name(args)
    elif(file_count == 1):
        if(files[0] == os.path.basename(args.conf_file) or files[0] == sys.argv[0]):
            binglog_name = get_first_binlog_file_name(args)
        else:
            binglog_name = files[0]
    else:
        (status, output) = commands.getstatusoutput("ls -l {0} |tail -n 1 |awk \'{1}\'".format(args.file_path, "{print $9}"))
        binglog_name = output
    return binglog_name.replace("\n", "").replace("\t", "").replace("\r", "")

def get_first_binlog_file_name(args):
     mysql_shell = mysql.format(args.host, args.user, args.password, args.port, "show master logs;", "{print $1}")
     (status, output) = commands.getstatusoutput(mysql_shell)
     return output.split("\n")[1]

if(__name__ == "__main__"):
    args = check_arguments()
    print("开始远程备份binlog...")
    while(True):
        binlog_backup = mysqlbinlog.format(args.host, args.user, args.password, args.port,
                                           args.server_id, args.file_path, get_binlog_file_name(args), args.log_file)
        os.system(binlog_backup)
        time.sleep(10)