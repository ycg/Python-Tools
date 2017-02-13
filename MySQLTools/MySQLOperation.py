

def init_host_info():
    pass

def init_replication_info(host_id):
    sql_select = "select 1 from mysql_monitor.replication_infos where host_id = %d;" % host_id
    sql_insert = "insert into mysql_monitor.replication_infos (host_id) values (%d)'" % host_id

def init_status_info(host_id):
    sql_select = "select 1 from mysql_monitor.mysql_status_infos where host_id = %d;" % host_id
    sql_insert = "insert into mysql_monitor.mysql_status_infos (host_id) values (%d)'" % host_id

def init_innodb_info(host_id):
    sql_select = "select 1 from mysql_monitor.mysql_status_infos where host_id = %d;" % host_id
    sql_insert = "insert into mysql_monitor.mysql_status_infos (host_id) values (%d)'" % host_id

def init_linux_host__info(host_id):
    sql_select = "select 1 from mysql_monitor.linux_host_infos where host_id = %d;" % host_id
    sql_insert = "insert into mysql_monitor.linux_host_infos (host_id) values (%d)'" % host_id

def init_table_infos(host_id, table_name):
    sql_select = "select 1 from mysql_monitor.{0} where host_id = {1}".format(table_name, host_id)
    sql_insert = "insert into mysql_monitor.{0} (host_id) values ({1})".format(host_id)


def update_repl_info():
    pass

def update_status_info():
    pass

def update_linux_host_info():
    pass

def insert_repl_info_log():
    pass

def insert_status_info_log():
    pass

def insert_linux_host_info_log():
    pass