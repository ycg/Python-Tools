#主要是针对update，delete操作，防止误操作
#那么就要进行原始数据备份，然后再执行相关update和delete操作
#还有一个工具就是说自动识别主库还是从库，防止在从库执行误操作

import time, argparse

def check_arguments():
    global connection_settings
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", type=str, dest="host", help="mysql host")
    parser.add_argument("--port", type=int, dest="port", help="mysql port")
    parser.add_argument("--user", type=str, dest="user", help="mysql user")
    parser.add_argument("--password", type=str, dest="password", help="mysql password")
    parser.add_argument("--log-file", type=str, dest="log_file", help="")
    parser.add_argument("--start-file", type=str, dest="start_file", help="")
    parser.add_argument("--start-pos", type=int, dest="start_pos", help="")
    parser.add_argument("--end-pos", type=int, dest="end_pos", help="")
    parser.add_argument("--end-file", type=str, dest="end_file", help="")
    parser.add_argument("--out-file", type=str, dest="out_file", help="")
    parser.add_argument("--start-datetime", type=str, dest="start_datetime", help="")
    parser.add_argument("--end-datetime", type=str, dest="end_datetime", help="")
    parser.add_argument("-B", "--flashback", dest="flashback", help="", default=False, action='store_true')
    parser.add_argument('-d', '--databases', dest='databases', type=str, nargs='*', help='dbs you want to process', default='')
    parser.add_argument('-t', '--tables', dest='tables', type=str, nargs='*', help='tables you want to process', default='')
    args = parser.parse_args()
    return args


if(__name__ == "__main__"):
    args = check_arguments()
    start_time = time.time()