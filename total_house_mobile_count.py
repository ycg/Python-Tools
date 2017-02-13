
import MySQLdb, time
import MySQLdb.converters

def sync():
    mobile = ""
    use_name = "yangcg"
    password = "yangcaogui123!.+"
    group1_conn = None
    #report_conn = None
    try:
        group1_conn = MySQLdb.connect(host="10.47.95.115", port=3306, user=use_name, passwd=password)
        #report_conn = MySQLdb.connect(host="db-report", port=3309, user=use_name, passwd=password)
        group1_cursor = group1_conn.cursor()
        #report_cursor = report_conn.cursor()

        group1_cursor.execute("select max(id) from hims_1.house_host_info");
        max_id = group1_cursor.fetchone()[0]

        start_id = 9140000
        id_interval = 5000
        end_id = start_id + id_interval

        while(end_id < max_id):
            '''
            #report_conn.autocommit(0)
            group1_cursor.execute("select hostMobile, count(1) from hims_1.house_host_info where id >= %d and id < %d and cityId in (2,12438) group by hostMobile;" % (start_id, end_id))

            #report_cursor.execute("start transaction;")
            for row in group1_cursor.fetchall():
                mobile = row[0]
                if(len(mobile) > 11):
                    print(mobile)
                #report_cursor.callproc('db1.check_mobile_count', (row[0]))
                sp_name = "call db1.check_mobile_count('{0}', {1});".format(row[0], row[1])
                #report_cursor.callproc(sp_name)
                report_cursor.execute(sp_name)
            '''
            #report_conn.commit()
            #report_cursor.execute("commit;")

            #group1_cursor.callproc('db1.check_mobile_count', (row[0]))
            sp_name = "call db1.check_mobile_count({0}, {1});".format(start_id, end_id)
            group1_cursor.execute(sp_name)

            start_id = end_id
            end_id = start_id + id_interval
            if(end_id > max_id):
                end_id = max_id
            print(start_id, end_id)
        #report_conn.commit()

        group1_conn.commit()
        group1_cursor.close()
        #report_cursor.close()
    #except:
    #    print(mobile)
    finally:
        if (group1_conn != None):
            group1_conn.close()
        #if (report_conn != None):
        #    report_conn.close()

print("start check data...")
aa = time.time()
sync()
bb = time.time()
print(bb - aa)