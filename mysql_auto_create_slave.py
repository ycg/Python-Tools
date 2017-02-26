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

repl_password = "$UISL*(ADbuadsf"
mysqldump_path = "/opt/master_data.sql"

def create_slave_for_mysqldump(args):
    #1.创建备份
    shell = "mysqldump -h{0} -u{1} -p{2} -P{3} " \
            "--max-allowed-packet=1G --single-transaction --master-data=2 " \
            "--default-character-set={4} --triggers --routines --events -B --all-databases > {5}"\
            .format(args.master_host, args.master_user, args.master_password, args.master_port, args.charset, args.mysqldump_path)
    os.system(shell)

    #2.导入数据
    #对导入速度进行优化，不要设置双1，而且设置不写binlog
    os.system("mysql -h{0} -u{1} -p{2} -P{3} --max-allowed-packet=1G --default-character-set={4} < {5}"
              .format(args.host, args.user, args.password, args.port, args.charset, args.mysqldump_path))

    #3.创建用户，如果没有指定用户，则自动创建用户
    create_replication_user(args)

    #4.进行change master操作
    change_master(args)

    #5.监测从库状态是否正确，如果没有异常，则创建从库成功

def create_slave_for_xtrabackup():
    pass

def change_master(args):
    sql = "change master to master_host='{0}', master_port={1}, master_user='{2}', master_password='{3}' "\
          .format(args.host, args.port, args.user, args.password)
    if(args.mode == 1):
        #普通复制
        sql = sql + "master_log_file='{0}', master_log_pos={1};"
    elif(args.mode == 2):
        #gtid复制
        sql = sql + "master_auto_position = 1;"

def create_replication_user(args):
    sql = "grants replication slave, replication client on *.* to sys_repl@% identified by '{0}'; flush privileges;".format(args.repl_password)
    pass

def execute_sql(args, sql):
    pass