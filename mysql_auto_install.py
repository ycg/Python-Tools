# -*- coding: utf-8 -*-

import os, time, paramiko

#1.生成配置文件
#2.从服务器获取安装包
#3.自动初始化数据
#4.自动启动

def mysql_start(args):
    os.system("mysqld --defaults-file = /etc/my.cnf &")
    #要判断下数据库是否生成成功
    time.sleep(2)
    print("数据库启动成功!!!")

def initialize_data(args):
    print("开始初始化数据...")
    os.system("mysqld --defaults-file = /etc/my.cnf &> /tmp/mysql.log")
    print("初始化数据完成!!!")
    time.sleep(1)

def create_mysql_linux_user(args):
    execute_remote_shell(args, "groupadd mysql")
    execute_remote_shell(args, "useradd mysql -g mysql")
    print("2-创建用户成功!!!\n")

def generate_mysql_config(args):
    print("正在生成mysql配置文件...")

    #1.生成server_id = IP+端口号
    result = execute_remote_shell(args, "ip addr | grep inet | grep -v 127.0.0.1 | grep -v inet6 | awk \'{ print $2}\' | awk -F \"/\" \'{print $1}\' | awk -F \".\" \'{print $4}\'")
    print(result[0].replace("\n", ""))
    port = 3306
    server_id = "3306" + result[0].replace("\n", "")

    #2.指定数据库目录和安装包地址
    data_dir = "/data/mysql"
    base_dir = "/opt/mysql"

    #3.生成buffer pool并生成instance size
    buffer_pool_instance = 0
    result = execute_remote_shell(args, "free -g | head -n2 | tail -n1 | awk \'{print $2}\'")
    total_memory = int(result[0].replace("\n", ""))
    buffer_pool_size = str(total_memory * 0.75) + "G"
    if(total_memory == 0):
        buffer_pool_size = "500M"
        buffer_pool_instance = 1
    elif(total_memory > 0 and total_memory <= 2):
        buffer_pool_instance = 2
    elif(total_memory > 2 and total_memory <= 8):
        buffer_pool_instance = 3
    elif(total_memory > 8 and total_memory <= 16):
        buffer_pool_instance = 4
    elif(total_memory > 16):
        buffer_pool_instance = 8

    #4.判断是否把bin log放在单独的硬盘
    bin_log = "mysql_bin"

    #5.写入配置到本地，然后scp
    file_path = "/tmp/my.cnf"
    file = open(file_path, "w")
    file.write(mysql_config.format(server_id, port, base_dir, data_dir, buffer_pool_size, buffer_pool_instance, bin_log))
    file.close()
    os.system("scp {0} root@{1}:/etc/".format(file_path, args.ip))

    time.sleep(0.5)
    print("配置文件生成完成!!!\n")
    time.sleep(0.5)

def scp_install_package(args):
    #shell = "scp root@{0}:{1} root@{2}:{3}"
    print("1-正在拷贝mysql安装包...")
    os.system("scp root@192.168.11.128:/opt/ root@192.168.11.129:/opt/")

    time.sleep(0.5)
    print("1-拷贝完成!!!\n")
    time.sleep(0.5)

def execute_remote_shell(args, shell):
    try:
        host_client = paramiko.SSHClient()
        host_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        host_client.connect(args.ip, port=22, username="root")
        stdin, stdout, stderr = host_client.exec_command(shell)
        return stdout.readlines()
    finally:
        if (host_client != None):
            host_client.close()

mysql_config = ("""
[client]
default_character_set = utf8mb4

[mysql]
prompt = \\u@\\h(\\d) \\r:\\m:\\s>
default_character_set = utf8mb4

[mysqld]
server_id = {0}
user = mysql
port = {1}
character_set_server = utf8mb4
basedir = {2}
datadir = {3}
socket = mysql.sock
pid_file= mysql.pid
log_error = mysql.err

#innodb
innodb_buffer_pool_size = {4}
innodb_flush_log_at_trx_commit = 2
innodb_flush_log_at_timeout = 1
innodb_flush_method = O_DIRECT
innodb_support_xa = 1
innodb_lock_wait_timeout = 3
innodb_rollback_on_timeout = 1
innodb_file_per_table = 1
transaction_isolation = REPEATABLE-READ
innodb_log_buffer_size = 16M
innodb_log_file_size = 256M
innodb_data_file_path = ibdata1:1G:autoextend
innodb_log_group_home_dir = ./
innodb_log_files_in_group = 2
#innodb_force_recovery = 1
#read_only = 1
innodb_sort_buffer_size=2M
innodb_online_alter_log_max_size=1G
innodb_buffer_pool_instances = {5}
innodb_buffer_pool_load_at_startup = 1
innodb_buffer_pool_dump_at_shutdown = 1
innodb_lru_scan_depth = 2000
#innodb_file_format = Barracuda
#innodb_file_format_max = Barracuda
innodb_purge_threads = 8
innodb_large_prefix = 1
innodb_thread_concurrency = 0
innodb_io_capacity = 300
innodb_print_all_deadlocks = 1
#innodb_locks_unsafe_for_binlog = 1
#innodb_autoinc_lock_mode = 2
innodb_open_files = 6000

#replication
log_bin = {6}
log_bin_index = mysql_bin_index
binlog_format = ROW
binlog_cache_size = 2M
max_binlog_cache_size = 50M
max_binlog_size = 1G
expire_logs_days = 7
sync_binlog = 0
skip_slave_start = 1
binlog_rows_query_log_events = 1
relay_log = relay_log
relay_log_index = relay_log_index
max_relay_log_size = 1G
#relay_log_purge = 0
master_info_repository = TABLE
relay_log_info_repository = TABLE
relay_log_recovery = ON
log_slave_updates = 1

#slow_log
slow_query_log = 1
long_query_time = 2
log_output = TABLE
slow_query_log_file = slow.log
log_queries_not_using_indexes = 1
log_throttle_queries_not_using_indexes = 30
log_slow_admin_statements = 1
log_slow_slave_statements = 1

#thread buffer size
tmp_table_size = 10M
max_heap_table_size = 10M
sort_buffer_size = 128K
join_buffer_size = 128K
read_buffer_size = 512K
read_rnd_buffer_size = 1M
key_buffer_size = 10M

#other
#sql_safe_updates = 1
skip_name_resolve = 1
open_files_limit = 65535
max_connections = 3000
max_connect_errors = 100000
#max_user_connections = 150
thread_cache_size = 64
lower_case_table_names = 0
query_cache_size = 0
query_cache_type = 0
max_allowed_packet = 1G
time_zone = SYSTEM
lock_wait_timeout = 30
performance_schema = OFF
table_open_cache_instances = 8
metadata_locks_hash_instances = 8
table_open_cache = 4096
table_definition_cache = 2048

#timeout
wait_timeout = 300
interactive_timeout = 300
connect_timeout = 20
""")

class Data():
    pass

args = Data()
args.ip = "192.168.11.129"
generate_mysql_config(args)