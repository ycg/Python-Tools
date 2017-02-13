#! /usr/bin/python

#import MySQLdb


import time

print(time.time())

localtime = time.localtime(time.time())
print(localtime)


def mymethod():
    print("这个不是类")

#mymethod()

#构造函数_init_()
#这里self参数就会告诉方法是哪个对象来调用的.这称为实例引用。
#构造函数是两个下划线组成的，使用一个下划线就报错
class people:
    def __init__(self):
        print("这类似于构造函数")
    def say(self, value):
        #print(self)
        print(value)
    def __str__(self):
        #msg = self.age
        return "这类似于C#的tostring方法";

yangcg = people()
#yangcg.say("yang cao gui")
#yangcg.age = 888
#print(yangcg.age)
print(yangcg)

zhaotl = people()
zhaotl.say("zhao tian li")

#print占位符的用法
print("my name is %s age is %d" % ("yangcg", 8888))

'''
class MySQLHelper:
    def _init_(self, host, port, user, pwd):
        self.host = host
        self.port = port
        self.user = user
        self.pwd = pwd

    def executeSql(self, sql):
        conn = getconnection()
        cursor = conn.cursor()
        result = cursor.execute(sql)
        conn.close()
        return cursor.fetchall()

    def get

    def getconnection(self):
        print("aaa")
        #return MySQLdb.connect(host=self.host, port=self.port, user=self.user, passwd=self.pwd)
'''

print("------------------------------------")

#可以把[]作为一个对象集合
class MyClass:
    pass

dd = []
for num in range(0, 10):
    class1 = MyClass()
    class1.name = "yang"
    class1.age = num
    dd.append(class1)

for i in dd:
    print("name is %s, age is %d" % (i.name, i.age))

class Data:
    pass


def executeForList(self, sql):
    conn = None
    try:
        columns = []
        conn = self.getconn()
        cursor = conn.cursor()
        result = cursor.execute(sql)
        for field in cursor.description:
            columns.append(field[0])

        data = []
        for row in cursor.fetchall():
            rowData = Data()
            for index in range(len(field)):
                rowData.__setattr__(field[index], row[0])

        return data
    finally:
        if (conn != None):
            conn.close
    return None



