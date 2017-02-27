import pymysql

def execute(host, user, password, sql, port=3306, charset="utf8"):
    try:
        connection, cursor = execute_for_db(host, port, user, password, charset, sql)
        cursor.execute(sql)
    finally:
        close(connection, cursor)

def fetchone(host, user, password, sql, port=3306, charset="utf8"):
    try:
        connection, cursor = execute_for_db(host, port, user, password, charset, sql)
        cursor.execute(sql)
        return cursor.fetchone()
    finally:
        close(connection, cursor)

def fetchall(host, user, password, sql, port=3306, charset="utf8"):
    try:
        connection, cursor = execute_for_db(host, port, user, password, charset, sql)
        return cursor.fetchall()
    finally:
       close(connection, cursor)

def close(connection, cursor):
    if(cursor != None):
        cursor.close()
    if(connection != None):
        connection.close()

def execute_for_db(host, port, user, password, charset, sql):
    connection = pymysql.connect(host=host, port=port, user=user, password=password, charset=charset, cursorclass=pymysql.cursors.DictCursor)
    cursor = connection.cursor()
    cursor.execute(sql)
    return connection, cursor


print(fetchall("192.168.11.130", "yangcg", "yangcaogui", "show slave status;"))

