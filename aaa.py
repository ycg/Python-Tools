import MySQLdb
import time
import commands
import threading

class Data:
    pass

class HostInfo:
    cpu = ""
    io = ""
    memory = ""

def execute(sql, host_name):
    conn = None
    try:
        columns = []
        pwd = "exoAzPw@3698XYz!)MZ12a"
        conn = MySQLdb.connect(host=host_name, port=3306, user="root", passwd=pwd, db="mysql")
        cursor = conn.cursor()
        result = cursor.execute(sql)
        if(cursor.description == None):
            return None

        for field in cursor.description:
            columns.append(field[0])

        data = []
        for index in range(len(columns)):
            setattr(rowData, columns[index], row[index])
        data.append(rowData)
    finally:
    if(conn != None):
        conn.close()
return None


master_host_list = ["DB-MASTER", "db-group2-master", "jr-dbmaster", "db-group3-master"]


thread_pool = {}
string_format = "%-23s%-8s%-8s%-10s%-5s%-5s%-23s%-17s%-23s%-17s%-10s"
thread_count_sql = "SELECT count(1) as counts FROM information_schema.processlist;"

def monitor_slaves():
    print(string_format  % ("Host", "CPU", "Memory", "Threads", "IO", "SQL", "Master_Log_File", "Master_Log_Pos", "Slave_Log_File", "Slave_Log_Pos", "delay_pos"))
    for host_name in slave_host_list:
        if(thread_pool.has_key(host_name) == False):
            t = threading.Thread(target = print_slave_info, args = (host_name,))
            t.setDaemon(True)
            thread_pool[host_name] = t
            thread_pool[host_name].start()
        else:
            t = thread_pool[host_name]
            t._target = print_slave_info(host_name)
            t._args = None
            t._kwargs = None
            t.run()

def print_slave_info(host_name):
    host_info = monitor_cpu_memory_io(host_name)
    thread_counts = execute(thread_count_sql, host_name)[0].counts
    if(host_name == "iw-db-datacenter"):
        result = execute("show all slaves status;", host_name)
        for slave_status in result:
            seconds = slave_status.Read_Master_Log_Pos - slave_status.Exec_Master_Log_Pos
    else:
        result = execute("show slave status;", host_name)
        seconds = result[0].Read_Master_Log_Pos - result[0].Exec_Master_Log_Pos

def monitor_masters():
    for host_name in master_host_list:
        if(thread_pool.has_key(host_name) == False):
            t = threading.Thread(target = print_master_info, args = (host_name,))
            t.setDaemon(True)
            thread_pool[host_name] = t
            thread_pool[host_name].start()
        else:
            t = thread_pool[host_name]
            t._target = print_master_info(host_name)
            t._args = None
            t._kwargs = None
            t.run()

def print_master_info(host_name):
    host_info = monitor_cpu_memory_io(host_name)
    thread_counts = execute(thread_count_sql, host_name)[0].counts
    result = execute("show master status;", host_name)
    print(string_format % (host_name, host_info.cpu, host_info.memory, thread_counts, "", "", result[0].File, result[0].Position, "", "", 0))


def monitor_cpu_memory_io(host_name):
    (status, output) = commands.getstatusoutput("ssh %s top -b -n1 | grep mysqld | head -n1 | awk \'{print $9, $10}\'" % (host_name))
    host_info = HostInfo()
    line_values = output.split("\n")
    top_value = line_values[len(line_values) - 1]

    items = top_value.split(" ")
    host_info.cpu = items[0]
    host_info.memory = items[1]
    return host_info


count = 1
while(count <= 300):
    print("\n")
    monitor_slaves()
    monitor_masters()
    time.sleep(3)
    count = count + 1