




import threadpool
import time


def test(aa):
    print(aa)

def result():
    print("end")

pool = threadpool.ThreadPool(90)
#requests = None
#requests = threadpool.makeRequests(test, [["11", "111"], ["222", "222222"]], result())
#requests = threadpool.makeRequests(test, ["222222", "111111"], result())
#[pool.putRequest(req) for req in requests]
#pool.wait()


def join_threads(method_name, args):
    #global requests
    requests = threadpool.makeRequests(method_name, args, None)
    [pool.putRequest(req) for req in requests]
    pool.poll()

def run_threads():
    global requests
    [pool.putRequest(req) for req in requests]
    pool.wait()

join_threads(test, ["111"])
join_threads(test, ["222"])
join_threads(test, ["333"])
join_threads(test, ["444"])

print("join ok")
time.sleep(2)
print("end")
#run_threads()