# -*- coding: utf-8 -*-

import MySQLdb
import ConfigParser
import time, threading
import collections, paramiko, threadpool
from MySQLdb.cursors import DictCursor
from DBUtils.PooledDB import PooledDB

#grant SUPER, REPLICATION CLIENT on *.* to 'yangcg'@'%' identified by '123456';

monitor_repl = "A"
monitor_status = "B"
monitor_innodb = "C"
monitor_host = "D"

print_count = 0
time_interval = 2
connection_pools = {}
host_ssh_client  = {}
thread_pool = threadpool.ThreadPool(100)
host_infos = collections.OrderedDict()
linux_infos = collections.OrderedDict()
mysql_status_infos = collections.OrderedDict()
mysql_innodb_infos = collections.OrderedDict()
mysql_replication_infos = collections.OrderedDict()
single_monitor_host_id_and_key = collections.OrderedDict()
monitor_types = collections.OrderedDict()
monitor_types[monitor_repl] = "Monitor Replication"
monitor_types[monitor_status] = "Monitor MySQL Status"
monitor_types[monitor_innodb] = "Monitor MySQL Innodb"
monitor_types[monitor_host] = "Monitor MySQL Host"

change_mode = 0
current_mode = "M"
current_host_id = "0"
single_monitor_mode = "S"
multi_monitor_mode = current_mode
current_monitor_type = monitor_status

'''数据对象'''
class Data:
    pass

'''主机信息'''
class HostInfo:
    def __init__(self, ip, port, user, password, remark):
        self.ip = ip
        self.port = port
        self.user = user
        self.remark = remark
        self.password = password

'''复制信息'''
class ReplicationInfo:
    def __init__(self):
        pass

'''MySQL状态信息'''
class MySQLStatusInfo:
    def __init__(self):
        self.id = 0
    pass

'''Innodb状态信息'''
class MySQLInnodbInfo:
    pass

'''加载mysql帐号'''
def load_all_host_infos():
    conf = ConfigParser.ConfigParser()
    conf.read("host.conf")

    g_port = conf.getint("global", "global_port")
    g_user = conf.get("global", "global_user")
    g_password = conf.get("global", "global_passoword")

    for section_name in conf.sections():
        if(section_name == "global"):
            continue

        ip, port, user, password, remark = "", 0, "", "", ""
        for option_name in conf.options(section_name):
            if(option_name == "host"):
                ip = conf.get(section_name, "host")
            if (option_name == "port"):
                port = conf.getint(section_name, "port")
            if (option_name == "user"):
                user = conf.get(section_name, "user")
            if (option_name == "remark"):
                remark = conf.get(section_name, "remark")
            if (option_name == "password"):
                password = conf.get(section_name, "password")

        if(port <= 0):
            port = g_port
        if(len(user) <= 0):
            user = g_user
        if(len(password) <= 0):
            password = g_password

        entity = HostInfo(ip, port, user, password, remark)
        key = ("%s:%d") % (ip, port)
        entity.key = key
        host_infos[key] = entity

    tmp_id = 0
    for key, value in host_infos.items():
        tmp_id = tmp_id + 1
        tmp_value = Data()
        tmp_value.host_key = value.key
        tmp_value.host_name = value.remark
        single_monitor_host_id_and_key[str(tmp_id)] = tmp_value

        check_mysql_is_slave(value)
        mysql_status_infos[key] = MySQLStatusInfo()
        mysql_innodb_infos[key] = MySQLInnodbInfo()
        mysql_replication_infos[key] = ReplicationInfo()

'''检测mysql是否是从库'''
def check_mysql_is_slave(host_info):
    result = executeToList("show global status like 'Slave_running';", host_info);

    if(result == None):
        host_info.is_slave = 0
        return
    if(len(result) <= 0):
        host_info.is_slave = 0
        return

    if(result[0].Value == "ON"):
        host_info.is_slave = 1
    else:
        host_info.is_slave = 0

    result = executeToShowStatus("show global variables where variable_name in ('datadir', 'pid_file', 'log_bin', 'log_bin_basename');", host_info);
    host_info.mysql_data_dir = result["datadir"]
    host_info.mysql_pid_file = result["pid_file"]

repl_string_format = "%-15s%-5s%-5s%-23s%-13s%-23s%-13s%-10s%-10s"
repl_print_title_string = repl_string_format % ("Name", "IO", "SQL", "M_File", "M_POS", "S_File", "S_POS", "D_POS", "Error_Msg")

'''获取mysql复制信息'''
def monitor_replication(host_info):
    if (host_info.is_slave == 0):
        return
    result = executeOneToDic("show slave status;", host_info);
    repl_info = mysql_replication_infos[host_info.key]
    repl_info.error_message = result["Last_Error"]
    repl_info.io_status = result["Slave_IO_Running"]
    repl_info.sql_status = result["Slave_SQL_Running"]
    repl_info.master_log_file = result["Master_Log_File"]
    repl_info.master_log_pos = int(result["Read_Master_Log_Pos"])
    repl_info.slave_log_file = result["Relay_Master_Log_File"]
    repl_info.slave_log_pos = int(result["Exec_Master_Log_Pos"])
    repl_info.slave_retrieved_gtid_set = result["Retrieved_Gtid_Set"]
    repl_info.slave_execute_gtid_set = result["Executed_Gtid_Set"]
    repl_info.delay_pos_count = repl_info.master_log_pos - repl_info.slave_log_pos

host_status_string_format = "%-15s%-8s%-8s%-8s%-9s%-9s%-9s%-7s%-8s%-7s%-7s%-7s%-7s%-7s%-7s"
host_status_print_title_string = host_status_string_format % ("Name", "CPU_1", "CPU_5", "CPU_15", "MySQL_C", "MySQL_M", "MySQL_D", "Disk_P", "Disk_T",
                                                              "Mem_T", "Mem_F", "SWAP_T", "SWAP_F", "Net_R", "Net_S")

'''监控主机状态'''
def monitor_host_status(host_info):
    linux_info = None
    host_client = None
    if(linux_infos.get(host_info.key) == None):
        linux_info = Data()
        linux_info.mysql_pid = 0
        linux_info.net_send_new = 0
        linux_info.net_receive_new = 0
        linux_infos[host_info.key] = linux_info
    else:
        linux_info = linux_infos[host_info.key]

    try:
        host_client = paramiko.SSHClient()
        host_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        host_client.connect(host_info.ip, port=22, username="root")

        #监测CPU负载
        monitor_host_for_cpu(host_client, linux_info)
        #监测网卡流量
        monitor_host_for_net(host_client, linux_info)
        #监测硬盘空间
        monitor_host_for_disk(host_client, linux_info)
        #监测linux内存使用情况
        monitor_host_for_memory(host_client, linux_info)
        #监控mysql的cpu和memory以及data大小
        monitor_host_for_mysql_cpu_and_memory(host_client, host_info, linux_info)
    finally:
        if (host_client != None):
            host_client.close()

def monitor_host_for_cpu(host_client, linux_info):
    stdin, stdout, stderr = host_client.exec_command("cat /proc/loadavg")
    cpu_value = stdout.readlines()[0].split()
    linux_info.cpu_1 = cpu_value[0]
    linux_info.cpu_5 = cpu_value[1]
    linux_info.cpu_15 = cpu_value[2]

def monitor_host_for_net(host_client, linux_info):
    net_send_byte, net_receive_byte = 0, 0
    stdin, stdout, stderr = host_client.exec_command("cat /proc/net/dev")
    for line in stdout.readlines():
        if(line.find("eth") >= 0):
            value_list = []
            for value in line.split(" "):
                if(len(value) > 0):
                    value_list.append(value)
            net_send_byte = net_send_byte + long(value_list[9])
            net_receive_byte = net_receive_byte + long(value_list[1])

    linux_info.net_send_old = linux_info.net_send_new
    linux_info.net_receive_old = linux_info.net_receive_new
    linux_info.net_send_new = net_send_byte
    linux_info.net_receive_new = net_receive_byte
    linux_info.net_send_byte = linux_info.net_send_new - linux_info.net_send_old
    linux_info.net_receive_byte = linux_info.net_receive_new - linux_info.net_receive_old

def monitor_host_for_disk(host_client, linux_info):
    id_tmp = 0
    max_disk_value = 0
    total_disk_value = 0
    stdin, stdout, stderr = host_client.exec_command("df")
    for line in stdout.readlines():
        id_tmp = id_tmp + 1
        if(id_tmp == 1):
            continue
        values = line.split()
        for value in values:
            if(value.find("%") >= 0):
                disk_value_int = int(value.replace("%", ""))
                if(max_disk_value == 0):
                    max_disk_value = disk_value_int
                else:
                    if(disk_value_int > max_disk_value):
                        max_disk_value = disk_value_int

        list_len = len(values)
        if(list_len >= 3):
            if(list_len == 6):
                total_disk_value = total_disk_value + int(values[1])
            elif(list_len == 5):
                total_disk_value = total_disk_value + int(values[0])
    linux_info.disk_value = str(max_disk_value) + "%"
    linux_info.total_disk_value = str(total_disk_value / 1024 / 1024)

def monitor_host_for_memory(host_client, linux_info):
    stdin, stdout, stderr = host_client.exec_command("cat /proc/meminfo")
    for line in stdout.readlines():
        values = line.split(":")
        if(len(values) >= 2):
            if(values[0].find("MemTotal") >= 0):
                linux_info.memory_total = change_byte_to_g(values[1])
            elif(values[0].find("MemFree") >= 0):
                linux_info.memory_free = change_byte_to_g(values[1])
            elif (values[0].strip().lstrip() == "Buffers"):
                linux_info.memory_buffers = change_byte_to_g(values[1])
            elif (values[0].strip().lstrip() == "Cached"):
                linux_info.memory_cache = change_byte_to_g(values[1])
            elif (values[0].find("SwapTotal") >= 0):
                linux_info.swap_total = change_byte_to_g(values[1])
            elif (values[0].find("SwapFree") >= 0):
                linux_info.swap_free = change_byte_to_g(values[1])
    linux_info.memory_free = linux_info.memory_free + linux_info.memory_buffers + linux_info.memory_cache

def monitor_host_for_mysql_cpu_and_memory(host_client, host_info, linux_info):
    if(linux_info.mysql_pid == 0):
        stdin, stdout, stderr = host_client.exec_command("cat %s" % host_info.mysql_pid_file)
        linux_info.mysql_pid = int(stdout.readlines()[0])

    stdin, stdout, stderr = host_client.exec_command("top -b -n1 | grep mysql")
    for line in stdout.readlines():
        values = line.split()
        if (int(values[0]) == linux_info.mysql_pid):
            if(float(values[8]) >= 1):
                #防止获取的CPU为0的情况
                linux_info.mysql_cpu = values[8]
            linux_info.mysql_memory = values[9]
            break

    #监测MySQL数据目录大小
    stdin, stdout, stderr = host_client.exec_command("du -h %s | tail -n1 | awk '{print $1'}" % host_info.mysql_data_dir)
    linux_info.mysql_data_size = stdout.readlines()[0].replace("\n", "").replace("G", "")

def change_byte_to_g(value):
    return int(value.replace("kB", "")) / 1024 / 1024

#T_S = Threads | T_Run = Thread_running | T_C_H = Thread_Cache_Hit | B_C_H = Binlog_Cache_Hit
mysql_status_string_format = "%-15s%-7s%-5s%-5s%-5s%-7s%-7s%-8s%-10s" \
                             "%-6s%-7s%-7s%-7s%-7s%-7s%-5s%-5s"
mysql_status_print_title_string = mysql_status_string_format % ("Name", "Select", "Ins", "Upd", "Del", "QPS", "TPS", "Commit", "Rollback",
                                                                "T_S", "T_Run", "T_C_H", "B_C_H", "Rec", "Send", "CTT", "CTDT")

'''监测mysql状态'''
def monitor_mysql_status(host_info):
    status_info = mysql_status_infos[host_info.key]
    innodb_info = mysql_innodb_infos[host_info.key]
    data = executeToShowStatus("show global status;", host_info)

    if(status_info.id == 0):
        status_info.select_last_count = int(data["Com_select"])
        status_info.insert_last_count = int(data["Com_insert"])
        status_info.update_last_count = int(data["Com_update"])
        status_info.delete_last_count = int(data["Com_delete"])
        status_info.send_last_bytes = int(data["Bytes_sent"])
        status_info.query_last_value = int(data["Questions"])
        status_info.commit_last_value = int(data["Com_commit"])
        status_info.rollback_last_value = int(data["Com_rollback"])
        status_info.receive_last_bytes = int(data["Bytes_received"])
        status_info.created_tmp_last_tables = int(data["Created_tmp_tables"])
        status_info.created_tmp_last_disk_tables = int(data["Created_tmp_disk_tables"])

        innodb_info.read_last_count = int(data["Innodb_rows_read"])
        innodb_info.updated_last_count = int(data["Innodb_rows_updated"])
        innodb_info.deleted_last_count = int(data["Innodb_rows_deleted"])
        innodb_info.inserted_last_count = int(data["Innodb_rows_inserted"])
    else:
        status_info.select_last_count = status_info.select_latest_count
        status_info.insert_last_count = status_info.insert_latest_count
        status_info.update_last_count = status_info.update_latest_count
        status_info.delete_last_count = status_info.delete_latest_count
        status_info.send_last_bytes = status_info.send_latest_bytes
        status_info.query_last_value = status_info.query_latest_value
        status_info.commit_last_value = status_info.commit_latest_value
        status_info.rollback_last_value = status_info.rollback_latest_value
        status_info.receive_last_bytes = status_info.receive_latest_bytes
        status_info.created_tmp_last_tables = status_info.created_tmp_latest_tables
        status_info.created_tmp_last_disk_tables = status_info.created_tmp_latest_disk_tables

        innodb_info.read_last_count = innodb_info.read_latest_count
        innodb_info.updated_last_count = innodb_info.updated_latest_count
        innodb_info.deleted_last_count =  innodb_info.deleted_latest_count
        innodb_info.inserted_last_count = innodb_info.inserted_latest_count

    status_info.id = status_info.id + 1
    status_info.binlog_cache_use = int(data["Binlog_cache_use"])
    status_info.binlog_cache_disk_use = int(data["Binlog_cache_disk_use"])
    status_info.connections = int(data["Connections"])
    status_info.thread_created = int(data["Threads_created"])
    status_info.open_files = int(data["Open_files"])
    status_info.opened_files = int(data["Opened_files"])
    status_info.open_tables = int(data["Open_tables"])
    status_info.openend_tables = int(data["Opened_tables"])
    status_info.send_latest_bytes = int(data["Bytes_sent"])
    status_info.query_latest_value = int(data["Questions"])
    status_info.select_latest_count = int(data["Com_select"])
    status_info.insert_latest_count = int(data["Com_insert"])
    status_info.update_latest_count = int(data["Com_update"])
    status_info.delete_latest_count = int(data["Com_delete"])
    status_info.commit_latest_value = int(data["Com_commit"])
    status_info.threads_count = int(data["Threads_connected"])
    status_info.threads_run_count = int(data["Threads_running"])
    status_info.rollback_latest_value = int(data["Com_rollback"])
    status_info.receive_latest_bytes = int(data["Bytes_received"])
    status_info.created_tmp_latest_tables = int(data["Created_tmp_tables"])
    status_info.created_tmp_latest_disk_tables = int(data["Created_tmp_disk_tables"])
    status_info.select_count = status_info.select_latest_count - status_info.select_last_count
    status_info.insert_count = status_info.insert_latest_count - status_info.insert_last_count
    status_info.update_count = status_info.update_latest_count - status_info.update_last_count
    status_info.delete_count = status_info.delete_latest_count - status_info.delete_last_count
    status_info.commit = (status_info.commit_latest_value - status_info.commit_last_value)
    status_info.rollback = (status_info.rollback_latest_value - status_info.rollback_last_value)
    status_info.qps = (status_info.query_latest_value - status_info.query_last_value) / time_interval
    status_info.create_tmp_table_count = status_info.created_tmp_latest_tables - status_info.created_tmp_last_tables
    status_info.create_tmp_disk_table_count = status_info.created_tmp_latest_disk_tables - status_info.created_tmp_last_disk_tables
    status_info.tps = ((status_info.rollback_latest_value + status_info.commit_latest_value) - (status_info.rollback_last_value + status_info.commit_last_value)) / time_interval

    status_info.send_bytes = (status_info.send_latest_bytes - status_info.send_last_bytes) / time_interval / 1024
    status_info.receive_bytes = (status_info.receive_latest_bytes - status_info.receive_last_bytes) / time_interval / 1024
    if(status_info.receive_bytes <= 1024):
        status_info.receive_bytes = str(status_info.receive_bytes) + "K"
    else:
        status_info.receive_bytes = str(status_info.receive_bytes / 1024) + "M"
    if (status_info.send_bytes <= 1024):
        status_info.send_bytes = str(status_info.send_bytes) + "K"
    else:
        status_info.send_bytes = str(status_info.send_bytes / 1024) + "M"
    status_info.thread_cache_hit = (1 - status_info.thread_created / status_info.connections) * 100
    if(status_info.binlog_cache_use > 0):
        #从库没有写binlog，所以这边要判断下
        status_info.binlog_cache_hit = (1 - status_info.binlog_cache_disk_use / status_info.binlog_cache_use) * 100
    else:
        status_info.binlog_cache_hit = 0


    innodb_info.read_latest_count = int(data["Innodb_rows_read"])
    innodb_info.updated_latest_count = int(data["Innodb_rows_updated"])
    innodb_info.deleted_latest_count = int(data["Innodb_rows_deleted"])
    innodb_info.inserted_latest_count = int(data["Innodb_rows_inserted"])
    innodb_info.page_dirty_count = int(data["Innodb_buffer_pool_pages_dirty"])
    innodb_info.page_free_count = int(data["Innodb_buffer_pool_pages_free"])
    innodb_info.page_total_count = int(data["Innodb_buffer_pool_pages_total"])
    if(data.get("Innodb_history_list_length") == None):
        #mysql官方5.6.28-log没这个状态
        innodb_info.history_list_length = 0
    else:
        #5.6.19-67.0-log Percona有这个状态
        innodb_info.history_list_length = int(data["Innodb_history_list_length"])
    innodb_info.buffer_pool_reads = int(data["Innodb_buffer_pool_reads"])
    innodb_info.buffer_pool_read_requests = int(data["Innodb_buffer_pool_read_requests"])
    innodb_info.read_count = innodb_info.read_latest_count - innodb_info.read_last_count
    innodb_info.updated_count = innodb_info.updated_latest_count - innodb_info.updated_last_count
    innodb_info.deleted_count = innodb_info.deleted_latest_count - innodb_info.deleted_last_count
    innodb_info.inserted_count = innodb_info.inserted_latest_count - innodb_info.inserted_last_count
    innodb_info.buffer_pool_hit = (1 - innodb_info.buffer_pool_reads / innodb_info.buffer_pool_read_requests) * 100

mysql_innodb_string_format = "%-15s%-9s%-6s%-6s%-6s%-10s%-10s%-6s%-7s%-10s%-10s%-12s"
mysql_innodb_print_title_string = mysql_innodb_string_format % ("Name", "Read", "Ins", "Upd", "Del", "Undo_H_L", "Pool_Hit", "Trxs", "Lock_W",
                                                                "P_Dirty", "P_Free", "P_Total")

'''监测innodb引擎'''
def monitor_innodb_status(host_info):
    innodb_info = mysql_innodb_infos[host_info.key]
    result = executeToList("select count(1) as count from information_schema.INNODB_TRX union all select count(1) as count from information_schema.INNODB_LOCK_WAITS;", host_info)
    innodb_info.trxs = result[0].count
    innodb_info.lock_waits = result[1].count

'''执行SQL返回List对象'''
def executeToList(sql, host_info):
    data = []
    conn = None
    cursor = None
    try:
        conn = getMySQLConnection(host_info)
        cursor = conn.cursor()
        cursor.execute(sql)
        for row in cursor.fetchall():
            rowData = Data()
            for key, value in row.items():
                setattr(rowData, key, value)
            data.append(rowData)
        return data
    finally:
        commit_and_close(cursor, conn)
    return None

'''返回一行数据转换成字典对象'''
def executeOneToDic(sql, host_info):
    conn = None
    cursor = None
    try:
        conn = getMySQLConnection(host_info)
        cursor = conn.cursor()
        cursor.execute(sql)
        return cursor.fetchone()
    finally:
        commit_and_close(cursor, conn)
    return None

'''执行Show Status返回字典对象'''
def executeToShowStatus(sql, host_info):
    data = {}
    conn = None
    cursor = None
    try:
        conn = getMySQLConnection(host_info)
        cursor = conn.cursor()
        cursor.execute(sql)
        for row in cursor.fetchall():
            data[row.get("Variable_name")] = row.get("Value")
        return data
    finally:
        commit_and_close(cursor, conn)
    return None

'''关闭数据库资源'''
def commit_and_close(cursor, conn):
    if (cursor != None):
        cursor.close()
    if (conn != None):
        conn.commit()
        conn.close()

'''获取MySQL链接'''
def getMySQLConnection(host_info):
    if(connection_pools.get(host_info.key) == None):
        pool = PooledDB(creator=MySQLdb, mincached=5, maxcached=20,
                        host=host_info.ip, port=host_info.port, user=host_info.user, passwd=host_info.password,
                        use_unicode=False, charset="utf8", cursorclass=DictCursor,reset=False)
        connection_pools[host_info.key] = pool
    return connection_pools[host_info.key].connection()

'''把操作装进线程池'''
def join_thread_pool(method_name):
    requests = []
    for host_info in host_infos.values():
        requests.extend(threadpool.makeRequests(method_name, [host_info], None))
    for request in requests:
        thread_pool.putRequest(request)
    thread_pool.poll()

'''监控MySQL状态的线程类'''
class ThreadMySQLStatus(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.setDaemon(True)

    def run(self):
        while (True):
            #aa = time.time()
            #for key, host_info in host_infos.items():
            #    monitor_mysql_status(host_info)
            #bb = time.time()
            #print(">>>>>>>>>>>>>>>>: %d", (bb - aa))
            join_thread_pool(monitor_mysql_status)
            time.sleep(time_interval)

'''监控MySQL复制线程类'''
class ThreadMySQLReplication(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.setDaemon(True)

    def run(self):
        while (True):
            #for key, host_info in host_infos.items():
            #    monitor_replication(host_info)
            join_thread_pool(monitor_replication)
            time.sleep(time_interval)

'''监控Linux主机状态'''
class ThreadLinuxHostStatus(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.setDaemon(True)

    def run(self):
        while (True):
            #for key, host_info in host_infos.items():
               #monitor_host_status(host_info)
            join_thread_pool(monitor_host_status)
            time.sleep(time_interval)

'''监控Innodb状态的线程类'''
class ThreadInnodbStatus(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.setDaemon(True)

    def run(self):
        while (True):
            #for key, host_info in host_infos.items():
            #    monitor_innodb_status(host_info)
            join_thread_pool(monitor_innodb_status)
            time.sleep(time_interval)

'''监控用户的屏幕输入用来切换选项'''
class ThreadMonitorInput(threading.Thread):
    str_format = "%-5s%-20s"

    def __init__(self):
        threading.Thread.__init__(self)
        self.setDaemon(True)

    def run(self):
        while (True):
            global current_mode, current_monitor_type, change_mode, current_host_id
            input_value = raw_input("").upper()

            change_mode = 1
            if(input_value == multi_monitor_mode):
                current_mode = multi_monitor_mode
                current_monitor_type = self.print_multi_monitor_options()
            elif(input_value == single_monitor_mode):
                current_mode = single_monitor_mode
                current_host_id = self.print_single_monitor_options()
            else:
                if(current_mode == multi_monitor_mode):
                    if(monitor_types.get(input_value) != None):
                        current_monitor_type = input_value
                    else:
                        print("选择错误，请重新选择：")
                elif(current_mode == single_monitor_mode):
                    if(single_monitor_host_id_and_key.get(input_value) != None):
                        current_monitor_type = input_value
                    else:
                        print("选择错误，请重新选择：")

            change_mode = 0

    def print_multi_monitor_options(self):
        print("-----------------进入多台监控模式------------------")
        print(self.str_format % ("id", "monitor_type"))
        for key, value in monitor_types.items():
            print(("%s:%s") % (key, value))
        return raw_input("请选择监控类型：").upper()

    def print_single_monitor_options(self):
        print("<<<<<<<<<<<<<<<<进入单台监控模式>>>>>>>>>>>>>>>>>>>")
        print(self.str_format % ("id", "host_name"))
        for key, value in single_monitor_host_id_and_key.items():
           print(self.str_format % (key, value.host_name))
        return raw_input("请选择要监控的机器，通过id来选择:").upper()

'''打印mysql状态信息'''
def print_status_infos(host_key):
    if(host_key == None):
        print("\n")
        print(mysql_status_print_title_string)
        for key, host_info in host_infos.items():
            print(print_status_info_by_host_key(key))
    else:
        print_single_host_info(mysql_status_print_title_string, print_status_info_by_host_key(host_key))

def print_status_info_by_host_key(host_key):
    host_info = host_infos[host_key]
    status_info = mysql_status_infos[host_key]
    return mysql_status_string_format % (host_info.remark, status_info.select_count, status_info.insert_count, status_info.update_count, status_info.delete_count,
                                         status_info.qps, status_info.tps, status_info.commit,
                                         status_info.rollback, status_info.threads_count, status_info.threads_run_count,
                                         status_info.thread_cache_hit, status_info.binlog_cache_hit,
                                         status_info.receive_bytes, status_info.send_bytes, status_info.create_tmp_table_count,
                                         status_info.create_tmp_disk_table_count)

'''打印mysql复制信息'''
def print_repl_infos(host_key):
    if(host_key == None):
        print("\n")
        print(repl_print_title_string)
        for key, host_info in host_infos.items():
            if (host_info.is_slave == 0):
               continue
            print(print_repl_info_by_host_key(key))
    else:
        print_single_host_info(repl_print_title_string ,print_repl_info_by_host_key(host_key))

def print_repl_info_by_host_key(host_key):
    host_info = host_infos[host_key]
    repl_info = mysql_replication_infos[host_key]
    return repl_string_format % (host_info.remark, repl_info.io_status, repl_info.sql_status,
                                 repl_info.master_log_file, repl_info.master_log_pos, repl_info.slave_log_file,
                                 repl_info.slave_log_pos, repl_info.delay_pos_count, repl_info.error_message)

'''打印linux主机信息'''
def print_linux_host_infos(host_key):
    if(host_key == None):
        print("\n")
        print(host_status_print_title_string)
        for key, host_info in host_infos.items():
            print(print_linux_host_info_by_host_key(key))
    else:
        print_single_host_info(host_status_print_title_string, print_linux_host_info_by_host_key(host_key))

def print_linux_host_info_by_host_key(host_key):
    host_info = host_infos[host_key]
    linux_info = linux_infos[host_key]
    return host_status_string_format % (host_info.remark, linux_info.cpu_1, linux_info.cpu_5,
                                        linux_info.cpu_15, linux_info.mysql_cpu, linux_info.mysql_memory, linux_info.mysql_data_size,
                                        linux_info.disk_value, linux_info.total_disk_value,
                                        linux_info.memory_total, linux_info.memory_free, linux_info.swap_total, linux_info.swap_free,
                                        linux_info.net_receive_byte, linux_info.net_send_byte)

'''打印Innodb状态信息'''
def print_innodb_infos(host_key):
    if(host_key == None):
        print("\n")
        print(mysql_innodb_print_title_string)
        for key, host_info in host_infos.items():
            print(print_innodb_info_by_host_key(key))
    else:
        print_single_host_info(mysql_innodb_print_title_string, print_innodb_info_by_host_key(host_key))

def print_innodb_info_by_host_key(host_key):
    host_info = host_infos[host_key]
    innodb_info = mysql_innodb_infos[host_key]
    return mysql_innodb_string_format % (host_info.remark, innodb_info.read_count, innodb_info.inserted_count, innodb_info.updated_count,
                                         innodb_info.deleted_count, innodb_info.history_list_length, innodb_info.buffer_pool_hit, innodb_info.trxs, innodb_info.lock_waits,
                                         innodb_info.page_dirty_count, innodb_info.page_free_count, innodb_info.page_total_count)

def print_single_host_info(print_title_string, print_string):
    global print_count
    if (print_count == 0):
        print(print_title_string)
    elif (print_count % 15 == 0):
        print("\n")
        print(print_title_string)
    else:
        print(print_string)
    print_count = print_count + 1

print("<<<<<<<<<<<<<<<监控模式如下：>>>>>>>>>>>>>>>>>")
print("M-多台监控")
print("S-单台监控")
print("<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>")
print("---------------监控类型如下：-----------------")
for key, value in monitor_types.items():
    print(("%s:%s") % (key, value))
print("---------------------------------------------")
print("等待3秒开始，每两秒钟刷新数据...")

load_all_host_infos()
ThreadMySQLStatus().start()
ThreadInnodbStatus().start()
ThreadMonitorInput().start()
ThreadLinuxHostStatus().start()
ThreadMySQLReplication().start()
time.sleep(3)

id = 0;
while(id < 300):
    id = id + 1
    if(change_mode == 0):
        if(current_mode == multi_monitor_mode):
              if(current_monitor_type == monitor_repl):
                  print_repl_infos(None)
              elif(current_monitor_type == monitor_status):
                  print_status_infos(None)
              elif(current_monitor_type == monitor_innodb):
                  print_innodb_infos(None)
              elif(current_monitor_type == monitor_host):
                  print_linux_host_infos(None)
        elif(current_mode == single_monitor_mode):
            host_key = single_monitor_host_id_and_key.get(current_host_id).host_key
            if (current_monitor_type == monitor_repl):
                print_repl_infos(host_key)
            elif (current_monitor_type == monitor_status):
                print_status_infos(host_key)
            elif (current_monitor_type == monitor_innodb):
                print_innodb_infos(host_key)
            elif (current_monitor_type == monitor_host):
                print_linux_host_infos(host_key)
    time.sleep(time_interval)


print("<<<<<<<<<<<<<<<<<<监控结束>>>>>>>>>>>>>>>>>>")