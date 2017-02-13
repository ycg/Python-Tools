


import MySQLdb, time
import MySQLdb.converters

fyb_rent = "insert into fyb.fyb_rent(houseId, houseState, rentPrice, rentDate, rentFreeDate, rentTermDate, remark, " \
           "currPublishId, userId, currTaskId, actionType, checkNum, publishDate, resultDate, operatorId, status, source, subSource) VALUES "
fyb_rent_hims = "select houseId, houseState, if(isnull(rentPrice), 0, rentPrice), rentDate, rentFreeDate, rentTermDate, remark, currPublishId, userId, currTaskId, actionType, checkNum, publishDate, resultDate, " \
                "operatorId, status, source, subSource from hims_1.houseresource where houseId >= %d and houseId < %d";
fyb_rent_hims_max_id = "select max(houseId) from hims_1.houseresource;"

fyb_rent_publish = "insert into fyb.fyb_rent_publish (id,createTime,updateTime,houseId,houseState,rentPrice,rentFreeDate,rentTermDate,spaceArea,balconySum,bedroomSum,livingRoomSum,wcSum,remark,userId,rentDate,landlordId," \
                   "actionType,checkNum,publishDate,resultDate,operatorId,afterCheckHouseState,note,status,checkFaildType,source,subSource,cityId,districtId,townId,estateId) VALUES"
fyb_rent_publish_hims = "select historyId,createTime,createTime,houseId,houseState, if(isnull(rentPrice), 0, rentPrice),rentFreeDate,rentTermDate," \
                        "if(isnull(spaceArea), 0,spaceArea),balconySum,bedroomSum,livingRoomSum,wcSum,remark,userId,rentDate,landlordId," \
                        "actionType,checkNum,publishDate,resultDate,operatorId,afterCheckHouseState,note,status,if(isnull(checkFaildType), 0,checkFaildType),source,subSource,cityId,districtId,townId,estateId " \
                        "from hims_1.houseresourcehistory where historyId >= %d and historyId < %d;"
fyb_rent_publish_hims_max_id = "select max(historyId) from hims_1.houseresourcehistory;"


fyb_rent_down = "insert into fyb.fyb_rent_down(id,createTime,updateTime,houseId,publishId,userId,operatorId,type,note,source) VALUES "
fyb_rent_down_hims = "select id,createTime,createTime,houseId,historyId,userId,operatorId,type,note,source from hims_1.housedown WHERE id >= %d and id < %d;"
fyb_rent_down_hims_max_id = "select max(id) from hims_1.housedown;"

fyb_rent_contact = "insert into fyb.fyb_rent_contact(id,createTime,updateTime,houseId,publishId,hostName,hostMobile,hostMobileExt,status) VALUES "
fyb_rent_contact_hims = "select contactId,NOW(),NOW(),houseId,historyId,hostName,hostMobile,hostMobileExt,status from hims_1.houseresourcecontact where contactId >= %d and contactId< %d;"
fyb_rent_contact_hims_max_id = "select max(contactId) from hims_1.houseresourcecontact;"

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

        group1_cursor.execute(fyb_rent_contact_hims_max_id);
        max_id = group1_cursor.fetchone()[0]

        start_id = 0
        id_interval = 3000
        end_id = start_id + id_interval

        while(end_id < max_id):
            group2_conn.autocommit(0)
            group1_cursor.execute(fyb_rent_contact_hims % (start_id, end_id))

            sql = fyb_rent_contact
            rows_number = 0
            for row in group1_cursor.fetchall():
                rows_number = rows_number + 1

                str_tmp = ''
                if(row[5] != None):
                    str_tmp = MySQLdb.escape_string(row[5])

                sql = sql + "(%s, %s, %s, %s, %s, %s, %s, %s, %s)," % (row[0],convert_value_to_str(row[1]),convert_value_to_str(row[2]),row[3],
                                                                       row[4],convert_value_to_str(str_tmp),convert_value_to_str(row[6]), convert_value_to_str_two(row[7]),
                                                                       row[8])


            sql = sql[0:len(sql)-1] + ";"
            #sql = MySQLdb.escape_string(sql)
            #print(sql)
            if(rows_number >= 1):
                group2_cursor.execute(sql)
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




