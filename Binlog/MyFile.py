
import MySQLdb
import MySQLdb.converters
import paramiko, string

'''
print( "%9.2f" % (string.atof(1)/string.atof(1)))

print(int(round(12.34, 0)))'''

str = "update `houseresourcecontact` set rentId=houseId where houseId >= {0} and houseId < {1}; select sleep(1);"

first = 1
for a in range(1, 60):
    print(str.format(first, a * 100000))
    first = a * 100000


''' 49500000
host_client = paramiko.SSHClient()
host_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
host_client.connect("10.47.92.98", port=22, username="root")'''



'''
conn = None
cursor = None
try:
    conn = MySQLdb.connect(host="192.168.11.128", port=3310, user="yancg", passwd="123456")
    #cursor = conn.cursor()
    cursor = conn.cursor(cursorclass = MySQLdb.cursors.DictCursor)
    cursor.execute("select count(1) as count from information_schema.INNODB_TRX union all select count(1) as count from information_schema.INNODB_LOCK_WAITS;");
    #print(cursor.fetchone())
    for row in cursor.fetchall():
        print(row)
    print("----------------------------")
    cursor.execute("show slave status;");
    for row in cursor.fetchall():
        print(row)
finally:
    if(cursor != None):
        cursor.close()
    if (conn != None):
        conn.close()
'''