# -*- coding: utf-8 -*-

'''
create database mysql_monitor;
use mysql_monitor;

drop table host_infos;
drop table replication_infos;

create table host_infos
(
    host_id mediumint unsigned not null auto_increment primary key,
    host_ip varchar(30) not null default '' comment '主机ip地址',
    host_name varchar(30) not null default '' comment '主机名称',
    port smallint unsigned not null default 3306 comment '端口号',
    user varchar(30) not null default 'root' ,
    password varchar(30) not null default '' comment '密码',
    remark varchar(100) not null default '' comment '备注',
    is_master tinyint not null default 0 comment '是否是主库',
    is_slave tinyint not null default 0 comment '是否是从库',
    master_id mediumint unsigned not null default 0 comment '如果是从库-关联他主库的id',
    is_deleted tinyint not null default 0 comment '删除的将不再监控',
    created_time timestamp not null default current_timestamp,
    modified_time timestamp not null default current_timestamp on update current_timestamp
) comment = 'mysql账户信息' ;

create table replication_infos
(
    host_id mediumint unsigned not null primary key,
    io_thread_status varchar(5) not null default 'YES' comment 'io线程状态',
    sql_thread_status varchar(5) not null default 'YES' comment 'sql线程状态',
    master_log_file varchar(50) not null default '' comment '主库binlog文件名',
    master_log_pos varchar(50) not null default '' comment '主库当前的pos位置',
    slave_log_file varchar(50) not null default '' comment '从库接受到主库binlog文件名',
    slave_log_pos varchar(50) not null default '' comment '从库正在执行的pos位置',
    delay_pos_count int unsigned not null default 0 comment '延迟的pos数量',
    master_execute_gtid_set varchar(500) not null default '' comment '主库已经执行的gtid',
    slave_retrieved_gtid_set varchar(500) not null default '' comment '从库接受到的gtid',
    slave_execute_gtid_set varchar(500) not null default '' comment '从库已经执行的gtid',
    mode tinyint not null default 0 comment '复制模式：0-普通复制 1-gtid复制',
    error_message varchar(500) not null default '' comment '复制异常信息',
    created_time timestamp not null default current_timestamp,
    modified_time timestamp not null default current_timestamp on update current_timestamp
) comment = 'mysql复制监控信息';

#mysql主机性能信息
create table host_performance_infos
(
    host_id int unsigned not null primary key,
    cpu decimal(7,2) unsigned not null default 0,
    io decimal(7,2) unsigned not null default 0,
    memory decimal(7,2) unsigned not null default 0,
    disk tinyint unsigned not null default 0
    threads smallint unsigned not null default 0,
    created_time timestamp not null default current_timestamp,
    modified_time timestamp not null default current_timestamp on update current_timestamp
)

#mysql其它性能监控信息
create table mysql_performance_infos
(
    host_id int unsigned not null primary key,
    created_time timestamp not null default current_timestamp,
    modified_time timestamp not null default current_timestamp on update current_timestamp
)

#mysql任务计划
create table job_infos
(
    id int unsigned not null auto_increment primary key,
    host_id int unsigned not null,

    is_complete tinyint not null default 0,
    execute_sql mediumtext not null default '',
    is_deleted tinyint not null default 0,
    created_time timestamp not null default current_timestamp,
    modified_time timestamp not null default current_timestamp on update current_timestamp
)

#把所有的mysql主机信息加载到内存
select id as host_id, host as ip, port, user, password, is_master, is_slave from host_infos where is_deleted = 0;

'''

#复制，CPU，内存，磁盘，线程
#以及mysql一些性能指标
#自动检测是主库还是从库，以及既是主库也是从库

#按复制延迟最大的显示前10台
#按数据CPU占用最大的显示前10太
#有很多的条件可以进行排序进行参考
#如果从库报错，可以通过host_id来查询出错的error信息

import MySQLdb
import time

'''是key-value结构，kye：host_id value：host_info'''
host_dic = {}

class HostInfo:
    pass

class ReplicationInfo:
    pass

'''加载host数据'''
def load_host_infos():
    result = execute_for_local_sql("select host_id, host_ip as ip, port, user, password, is_master, is_slave, master_id from mysql_monitor.host_infos where is_deleted = 0;");
    for host_info in result:
        host_dic[host_info.host_id] = host_info

'''收集复制信息'''
def monitor_replication():
    data_list = []
    for key, value in host_dic.items():
        if(value.is_slave == 0):
            continue
        result = execute("show slave status;", value.ip, value.port, value.user, value.password)[0];
        replicationInfo = ReplicationInfo()
        replicationInfo.host_id = value.host_id
        replicationInfo.io_status = result.Slave_IO_Running
        replicationInfo.sql_status = result.Slave_SQL_Running
        replicationInfo.master_log_file = result.Master_Log_File
        replicationInfo.master_log_pos = result.Read_Master_Log_Pos
        replicationInfo.slave_log_file = result.Relay_Master_Log_File
        replicationInfo.slave_log_pos = result.Exec_Master_Log_Pos
        replicationInfo.delay_pos_count = result.Read_Master_Log_Pos - result.Exec_Master_Log_Pos;
        replicationInfo.error_message = result.Last_Error
        replicationInfo.slave_retrieved_gtid_set = result.Retrieved_Gtid_Set
        replicationInfo.slave_execute_gtid_set = result.Executed_Gtid_Set
        if(len(result.Retrieved_Gtid_Set) > 0):
            replicationInfo.mode = 1
            master_host_info = host_dic[value.master_id]
            result = execute("show slave status;", master_host_info.ip, master_host_info.prot, master_host_info.user, master_host_info.password)[0];
            replicationInfo.master_execute_gtid_set = result.Executed_Gtid_Set
        else:
            replicationInfo.mode = 0
            replicationInfo.master_execute_gtid_set = ""
        data_list.append(replicationInfo)

        update_repl_infos(data_list)

'''更新复制信息入库'''
def update_repl_infos(repl_infos):
    conn = None
    try:
        conn = get_local_connection()
        cursor = conn.cursor()
        for entity in repl_infos:
            sql = "update mysql_monitor.replication_infos set io_thread_status = '%s', sql_thread_status = '%s', " \
                  "master_log_file = '%s', master_log_pos = %s, slave_log_file = '%s', slave_log_pos = %s, " \
                  "delay_pos_count = %s, master_execute_gtid_set = '%s', slave_retrieved_gtid_set = '%s', " \
                  "slave_execute_gtid_set = '%s', mode = %s, error_message = '%s' WHERE host_id = %s;" % \
                  (entity.io_status, entity.sql_status, entity.master_log_file, entity.master_log_pos,
                   entity.slave_log_file, entity.slave_log_pos, entity.delay_pos_count, entity.master_execute_gtid_set,
                   entity.slave_retrieved_gtid_set, entity.slave_execute_gtid_set, entity.mode, entity.error_message, entity.host_id)
            cursor.execute(sql)
    finally:
        if (conn != None):
            conn.close()
    return None

def monitor_cpu_io_memory():
    pass

def monitor_mysql_performance():
    pass


class Data:
    pass


class HostInfo:
    cpu = ""
    io = ""
    memory = ""

host = "10.168.22.17"
port = 3306
user = "yangcg"
password = "yangcaogui"

'''获取本地的数据库连接'''
def get_local_connection():
    return MySQLdb.connect(host=host, port=port, user=user, passwd=password)

'''执行本地的数据库sql'''
def execute_for_local_sql(sql):
    return execute(sql, host, port, user, password)

'''执行远程数据库sql'''



count = 1
load_host_infos()
while(count < 100):
    print("开始更新复制信息")
    monitor_replication()
    print("OK!!!!!!!!!!!!!")
    time.sleep(3)
    count = count + 1