


import MySQLdb, time
import MySQLdb.converters

fyb_rent = "insert into fyb_rent(houseId, houseState, rentPrice, rentDate, rentFreeDate, rentTermDate, remark, " \
           "currPublishId, userId, currTaskId, actionType, checkNum, publishDate, resultDate, operatorId, status, source, subSource) VALUES "
fyb_rent_hims = "select houseId, houseState, rentPrice, rentDate, rentFreeDate, rentTermDate, remark, currPublishId, userId, currTaskId, actionType, checkNum, publishDate, resultDate, " \
                "operatorId, status, source, subSource from hims_1.houseresource where houseId >= %d and houseId < %d";
fyb_rent_hims_max_id = "select max(houseId) from hims_1.houseresource;"

fyb_rent_publish = "insert into fyb_rent_publish (id,createTime,updateTime,houseId,houseState,rentPrice,rentFreeDate,rentTermDate,spaceArea,balconySum,bedroomSum,livingRoomSum,wcSum,remark,userId,rentDate,landlordId," \
                   "actionType,checkNum,publishDate,resultDate,operatorId,afterCheckHouseState,note,status,checkFaildType,source,subSource,cityId,districtId,townId,estateId) VALUES"
fyb_rent_publish_hims = "select historyId,createTime,createTime,houseId,houseState,rentPrice,rentFreeDate,rentTermDate,spaceArea,balconySum,bedroomSum,livingRoomSum,wcSum,remark,userId,rentDate,landlordId," \
                        "actionType,checkNum,publishDate,resultDate,operatorId,afterCheckHouseState,note,status,checkFaildType,source,subSource,cityId,districtId,townId,estateId " \
                        "from hims_1.houseresourcehistory where historyId >= %d and historyId < %d;"
fyb_rent_publish_hims_max_id = "select max(historyId) from hims_1.houseresourcehistory;"


fyb_rent_down = "insert into fyb_rent_down(id,createTime,updateTime,houseId,publishId,userId,operatorId,type,note,source) VALUES "
fyb_rent_down_hims = "select id,createTime,createTime,houseId,historyId,userId,operatorId,type,if(isnull(note), '', note),source from hims_1.housedown WHERE id >= %d and id < %d;"
fyb_rent_down_hims_max_id = "select max(id) from hims_1.housedown;"

fyb_rent_contact = "insert into fyb_rent_contact(id,createTime,updateTime,houseId,publishId,hostName,hostMobile,hostMobileExt,status) VALUES "
fyb_rent_contact_hims = "select contactId,NOW(),NOW(),houseId,historyId,hostName,hostMobile,if(isnull(hostMobileExt), '', hostMobileExt),status from hims_1.houseresourcecontact where contactId >= %d and contactId< %d;"
fyb_rent_contact_hims_max_id = "select max(contactId) from hims_1.houseresourcecontact;"

def sync():
    use_name = "yangcg"
    password = "yangcaogui123!.+"
    group1_conn = None
    group2_conn = None
    try:
        group1_conn = MySQLdb.connect(host="db-master", port=3306, user=use_name, passwd=password)
        group2_conn = MySQLdb.connect(host="db-group2-master", port=3306, user=use_name, passwd=password)
        group1_cursor = group1_conn.cursor()
        group2_cursor = group2_conn.cursor()

        group1_cursor.execute(fyb_rent_hims_max_id);
        max_id = group1_cursor.fetchone()[0]

        start_id = 0
        id_interval = 2000
        end_id = start_id + id_interval

        while(end_id < max_id):
            group1_cursor.execute(fyb_rent_hims % (start_id, end_id))

            sql = fyb_rent
            for row in group1_cursor.fetchall():
                sql = sql + "(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s,%s,%s,%s,%s,%s,%s,%s)," % (row[0],row[1],row[2],convert_value_to_str(row[3]),
                                                                                                convert_value_to_str(row[4]),convert_value_to_str(row[5]), convert_value_to_str(row[6]),row[7],
                                                                                                row[8],row[9],row[10],row[11],
                                                                                                convert_value_to_str(row[12]),convert_value_to_str(row[13]), row[14], row[15],
                                                                                                row[16],row[17])

            sql = sql[0:len(sql)-1] + ";"
            group2_cursor.execute(sql)
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
    '''result = None
    if(value == None):
        result = MySQLdb.converters.None2NULL(value, result)
    else:
        result = ("'%s'" % value)'''
    result = ("'%s'" % value)
    return result

aa = time.time()
sync()
bb = time.time()
print(bb - aa)




