
import time
import pymysql
from pymysqlreplication import BinLogStreamReader
from pymysqlreplication.row_event import (
    WriteRowsEvent,
    UpdateRowsEvent,
    DeleteRowsEvent
)
from pymysqlreplication.event import QueryEvent, RotateEvent, FormatDescriptionEvent

mysql_settings = {'host': '192.168.11.128', 'port': 3310, 'user': 'yancg', 'passwd': '123456'}

#stream = BinLogStreamReader(connection_settings = mysql_settings, server_id= 1283310)
#stream = BinLogStreamReader(connection_settings = mysql_settings, log_file='mysql_bin.000007', log_pos=0, resume_stream=True, server_id= 1283310)
stream = BinLogStreamReader(connection_settings = mysql_settings, log_file='mysql_bin.000010', log_pos=4, resume_stream=True, server_id= 1283310)


def sql_format(dic, split_value):
    list = []
    for key, value in dic.items():
        if(value == None):
            list.append("`%s`=null" % key)
            continue
        if(isinstance(value, int)):
            list.append("`%s`=%d" % (key, value))
        else:
            list.append("`%s`='%s'" % (key, value))
    return split_value.join(list)

def sql_format_2(values):
    list = []
    for value in values:
        if (value == None):
            list.append("null")
            continue
        if (isinstance(value, int)):
            list.append('%d' % value)
        else:
            list.append('\'%s\'' % value)
    return ', '.join(list)

aa = time.time()
sql_list = []
#my_file = open("C:\\Users\\Administrator\\Desktop\\binlog.sql", "w+")

#eStartPos, lastPos = stream.log_pos, stream.log_pos
#print(eStartPos, lastPos)
'''
for binlogevent in stream:
    pos = binlogevent.packet.log_pos
    #if(isinstance(binlogevent, QueryEvent)):
    #    continue
    if (isinstance(binlogevent, WriteRowsEvent) or isinstance(binlogevent, UpdateRowsEvent) or isinstance(binlogevent, DeleteRowsEvent)):
        if(pos >= 155608 and pos <= 156523):
            print(stream.log_pos)
            for row in binlogevent.rows:
                print(row)
        elif(pos > 156523):
            break
'''


for binlogevent in stream:
    binlogevent.dump()
    if (isinstance(binlogevent, WriteRowsEvent) or isinstance(binlogevent, UpdateRowsEvent) or isinstance(binlogevent, DeleteRowsEvent)):
        for row in binlogevent.rows:
            print(row)
    '''
    #print(binlogevent.packet.log_pos)
    if(isinstance(binlogevent, WriteRowsEvent)):
        #insert into db1.t1 (c1, c2) values ('aaa', 'bbb');
        #print("Wirte--------")
        print(binlogevent.extra_data)
        for row in binlogevent.rows:
            #print(row)
            #list.append()
            str123 = "insert into `{0}`.`{1}` ({2}) values ({3});".format(binlogevent.schema, binlogevent.table, ', '.join(map(lambda k: '`%s`'%k, row['values'].keys())), sql_format_2(row["values"].values()))
            #print(str)
            #my_file.write(str123+"\n")
            sql_list.append(str123+"\n")

    elif(isinstance(binlogevent, UpdateRowsEvent)):
        #update db1.t1 set c1 = 'aaa' where c1 = 'bbb';
        #print("Update+++++++++++++++++")
        #print(binlogevent.schema, binlogevent.table)
        for row in binlogevent.rows:
            #print(row)
            str123 = "update `{0}`.`{1}` set {2} where {3};".format(binlogevent.schema, binlogevent.table, sql_format(row['after_values'], ", "), sql_format(row['before_values'], " AND "))
            #list.append(str(str123))
            sql_list.append(str123+"\n")

    elif (isinstance(binlogevent, DeleteRowsEvent)):
        #delete from db1.t1 where c1 = 'bbb';
        #print("Delete>>>>>>>>>>>>>>>>>>>>")
        #print(binlogevent.schema, binlogevent.table)
        for row in binlogevent.rows:
            #print(row)
            str123 = "delete from `{0}`.`{1}` where {2};".format(binlogevent.schema, binlogevent.table, sql_format(row['values'], " AND "))
            #list.append(str(str123))
            sql_list.append(str123+"\n")

'''

stream.close()

bb = time.time()
print("binlog ok", bb - aa)

#my_file.writelines(sql_list)
#my_file.close()
bb = time.time()

print(bb - aa)
