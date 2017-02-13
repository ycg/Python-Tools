# -*- coding: utf-8 -*-

import random, argparse, sys

'''
1.封装mysqlbinlog远程备份操作
2.支持断开尝试重新链接操作
3.在备份目录随机生成一个server_id
4.如果备份目录已经有文件了，就不需要从头开始获取binlog了
'''

mysqlbinlog = "mysqlbinlog -h{0} -u{1} -p{2} -P{3} --stop-never --raw" \
              "--read-from-remote-server --stop-never-slave-server-id={4} --result-file={5}"

server_id = random.randint(88888,99999)

def check_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", type=str, dest="host", help="mysql host")
    parser.add_argument("--port", type=int, dest="port", help="mysql port")
    parser.add_argument("--user", type=str, dest="user", help="mysql user")
    parser.add_argument("--password", type=str, dest="password", help="mysql password")
    parser.add_argument("--file-path", type=str, dest="path", help="save binlog directory")
    args = parser.parse_args()

    if not args.host or not args.user or not args.password:
        print(parser.format_usage())
        sys.exit(1)

    #args.port =