create database mysql_monitor;
use mysql_monitor;

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

create table mysql_status_infos
(
    host_id mediumint unsigned not null primary key,
    select_count mediumint unsigned not null comment '查询数量',
    update_count mediumint unsigned not null comment '更新数量',
    insert_count mediumint unsigned not null comment '插入数量',
    delete_count mediumint unsigned not null comment '删除数量',
    commit_count mediumint unsigned not null comment '事物提交数量',
    rollback_count mediumint unsigned not null comment '事物回滚数量',
    send_bytes mediumint unsigned not null comment '发送字节数量',
    receive_bytes mediumint unsigned not null comment '接受字节数量',
    receive_bytes mediumint unsigned not null comment '接受字节数量',
    thread_count mediumint unsigned not null comment '线程数量',
    thread_running_count mediumint unsigned not null comment '正在运行的线程数量',
    qps mediumint unsigned not null comment '每秒查询数量',
    tps mediumint unsigned not null comment '每秒事物数量',
    created_tmp_tables mediumint unsigned not null comment '创建临时表的数量',
    created_tmp_disk_tables mediumint unsigned not null comment '创建基于磁盘的临时表数量',
    created_time timestamp not null default current_timestamp,
    modified_time timestamp not null default current_timestamp on update current_timestamp
) comment = "mysql运行状态信息数据"

create table mysql_all_status_infos
(

) comment = 'mysql所有的状态值';

create table linux_host_infos
(
    host_id int unsigned not null primary key,
    cpu_1 decimal(7,2) unsigned not null default 0 comment 'cpu一分钟负载',
    cpu_5 decimal(7,2) unsigned not null default 0 comment 'cpu五分钟负载',
    cpu_15 decimal(7,2) unsigned not null default 0 comment 'cpu十五分钟负载',
    io decimal(7,2) unsigned not null default 0 comment 'io运行状态',
    mysql_cpu decimal(7,2) unsigned not null default 0 comment 'mysql cpu利用率',
    mysql_memory decimal(7,2) unsigned not null default 0 comment 'mysql使用内存百分比',
    mysql_data_size smallint unsigned not null default 0 comment 'mysql数据文件大小单位为G',
    disk_per tinyint unsigned not null default 0 comment '最大磁盘利用率百分比'
    created_time timestamp not null default current_timestamp,
    modified_time timestamp not null default current_timestamp on update current_timestamp
) comment = 'linux和mysql硬件参数数据';

create table backup_plain
(
    host_id int unsigned not null primary key,
    #是否每日全备
    #每天备份时间点
    #是否需要增量备份
    #备份项选择
    #注意GTID备份的问题
    #注意复制多线程的备份问题
) comment = '周期性备份计划'

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
