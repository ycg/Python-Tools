


import MySQLdb, time
import MySQLdb.converters


fyb_rent_publish = "update fyb.fyb_rent_publish set note = {0} where id = {1};"
fyb_rent_publish_hims = "select historyId,note from hims_1.houseresourcehistory where historyId >= %d and historyId < %d;"
fyb_rent_publish_hims_max_id = "select max(historyId) from hims_1.houseresourcehistory;"


def sync():
    use_name = "yangcg"
    password = "yangcaogui123!.+"
    group1_conn = None
    group2_conn = None
    try:
        group1_conn = MySQLdb.connect(host="db-master", port=3306, user=use_name, passwd=password,charset='utf8')
        group2_conn = MySQLdb.connect(host="db-group2-master", port=3306, user=use_name, passwd=password,charset='utf8')
        group1_cursor = group1_conn.cursor()
        group2_cursor = group2_conn.cursor()

        group1_cursor.execute(fyb_rent_publish_hims_max_id);
        max_id = group1_cursor.fetchone()[0]

        start_id = 2595000
        id_interval = 3000
        end_id = start_id + id_interval

        while(end_id < max_id):
            group2_conn.autocommit(0)
            group1_cursor.execute(fyb_rent_publish_hims % (start_id, end_id))

            #sql = "start transaction;"
            rows_number = 0
            for row in group1_cursor.fetchall():
                rows_number = rows_number + 1
                str_tmp = ""
                if(row[1] == None):
                    str_tmp = "''"
                else:
                    str_tmp = convert_value_to_str_two(MySQLdb.escape_string(row[1]))
                #sql = sql + fyb_rent_publish.format(str_tmp, row[0]) + "\n"
                sql = fyb_rent_publish.format(str_tmp, row[0])
                group2_cursor.execute(sql)

            #sql = sql + "commit;"
            #if(rows_number > 0):
            #    print(sql)
            #   group2_cursor.execute(sql)
            group2_conn.commit()
            start_id = end_id
            end_id = start_id + id_interval
            if(end_id > max_id):
                end_id = max_id
            print(start_id, end_id)
        group2_conn.commit()
        group1_conn.commit()
    finally:
        if (group2_conn != None):
            group2_conn.close()
        if (group1_conn != None):
            group1_conn.close()

def convert_value_to_str(value):
    result = None
    if(value == None):
        result = MySQLdb.converters.None2NULL(value, result)
    else:
        result = ("'%s'" % value)
    return result

def convert_value_to_str_two(value):
    result = None
    if(value == None):
        result = "''"
    else:
        result = ("'%s'" % value)
    return result

aa = time.time()
sync()
bb = time.time()
print(bb - aa)




