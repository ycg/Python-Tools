# -*- coding: utf-8 -*-

'''
#自动创建从库
#一丶mysqldump创建
    1.首先从主库进行备份，备份在本地
    2.然后导入到从库

#二丶xtrabackup备份
    1.首先检测有没有安装
    2.slave机器进行备份
    3.把安装包同步到本地机器
    4.数据库恢复
    5.启动

可能有的问题：
1.xtrabackup --远程备份问题
2.大数据库备份问题
3.是否是gtid操作
'''

import os

def create_slave_for_mysqldump(args):
    #1.创建备份
    shell = "mysqldump -h{0} -u{1} -p{2} -P{3} " \
            "--max-allowed-packet=1G --single-transaction --master-data=2 " \
            "--default-character-set={4} --triggers --routines --events -B --all-databases > /opt/master_data.sql"\
            .format(args.master_host, args.master_user, args.master_password, args.master_port, args.charset)
    os.system(shell)

    #2.导入数据
    os.system("mysql -h{0} -u{1} -p{2} -P{3} --max-allowed-packet=1G --default-character-set={4} < /opt/master_data.sql"
              .format(args.host, args.user, args.password, args.port, args.charset))

    #3.进行change master操作

def create_slave_for_xtrabackup():
    pass

def change_master(args):
    if(args.mode == 1):
        #普通复制
        pass
    elif(args.mode == 2):
        #gtid复制
        pass
