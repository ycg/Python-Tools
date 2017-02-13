

'''
print("aaaa")
age = 14
if age == 100:
    print("111111111")
else:
    print("222222")

print("你好，杨曹贵")

age=age+1000
print(age)

myname="yangcaogui"
print(myname)

a,b,c=1,2,3
print(a)
print(myname)

print(myname[0])
'''

#集合语法
mylist=[12,2321,321,321321]

#print(mylist[1])
#print(mylist)
#mylist[1]=88888
#print(mylist[1])
#print(type(mylist))

#print(mylist.count())

mylist.append(9999999)
#print(mylist[1])
#print(mylist[0])
#print(mylist[4])

#其实字典类似于json格式，这个好理解
'''
mydic={}
print(type(mydic))
mydic[0]="111111111"
print(mydic[0])
'''
mydic={"one":"1","two":"2"}
#print(mydic["one"])
#print(mydic.keys())
#print(mydic.values())
#print(10/2)
#print("the one is" + mydic[0])

'''
#练习条件语句
aa="123"
if( aa == "123" ):
    print("true")
elif aa == "1232":
    print("111111111")
elif(aa=="11111"):
    print("3333333333")
else:
    print("false")

#and条件就使用一个&
age = 88
if(age > 0 & age < 100):
    print(age)

#or条件使用一个竖杠 |
if(age > 0 | age < 100):
    print(age)
if(age > 0): print("aaaaaaaaa")

print("goodbye")
print("-----------------------------")

#循环语句while或者for
#循环控制语句break continue pass
while(age < 100):
    #age = age + 1
    age += 1
    print(age)
    if(age == 90):
        break

print("==============================")

#for num in range(10, 29):
    #print(num)

person = ["yang", "zhao", "cao", "gui"]
for myname in person:
    print(myname)

#range默认左开又闭
#就去左边，右边到了不取值
print(range(len(person)))

#使用for else语法
for num in range(0, 10):
    print(num)
else:
    print("循环结束")



#嵌套循环其实很好理解


print(abs(-1000))
'''

#字符串
var1 = "123"
print(var1[0])

#列表
mylist = [1, 2, 3, 4, "123", "name"]
print(mylist[1:5])