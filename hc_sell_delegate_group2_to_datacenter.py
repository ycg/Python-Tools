


import MySQLdb, time
import MySQLdb.converters

def sync():
    use_name = "yangcg"
    password = "yangcaogui123!.+"
    group2_conn = None
    datacenter_conn = None
    try:
        group2_conn = MySQLdb.connect(host="db-group2-master", port=3306, user=use_name, passwd=password)
        datacenter_conn = MySQLdb.connect(host="iw-db-datacenter", port=3306, user=use_name, passwd=password)
        group2_cursor = group2_conn.cursor()
        datacenter_cursor = datacenter_conn.cursor()

        group2_cursor.execute("select max(id) from agent.hc_sell_delegate");
        max_id = group2_cursor.fetchone()[0]

        start_id = 0
        id_interval = 800
        end_id = start_id + id_interval

        while(end_id < max_id):
            datacenter_conn.autocommit(0)
            group2_cursor.execute("select id,agentId,houseId, createTime, auditStatus, recordNumber, auditTime, estateId "
                                  "from agent.hc_sell_delegate where id >= %d and id < %d" % (start_id, end_id))

            sql = "replace into agent.hc_sell_delegate (id,agentId,houseId,createTime,auditStatus,recordNumber,auditTime,estateId) values"
            for row in group2_cursor.fetchall():
                sql = sql + "(%s, %s, %s, %s, %s, %s, %s, %s)," % \
                            (row[0],row[1],row[2],convert_value_to_str(row[3]),row[4],convert_value_to_str(row[5]),convert_value_to_str(row[6]),row[7])
            sql = sql[0:len(sql)-1] + ";"
            datacenter_cursor.execute(sql)
            datacenter_conn.commit()
            start_id = end_id
            end_id = start_id + id_interval
            if(end_id > max_id):
                end_id = max_id
        datacenter_conn.commit()
    finally:
        if (group2_conn != None):
            group2_conn.close()
        if (datacenter_conn != None):
            datacenter_conn.close()

def convert_value_to_str(value):
    result = None
    if(value == None):
        result = MySQLdb.converters.None2NULL(value, result)
    else:
        result = ("'%s'" % value)
    return result

aa = time.time()
sync()
bb = time.time()
print(bb - aa)




