import pymysql, time, argparse, sys

def check_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", type=str, dest="host", help="mysql host")
    parser.add_argument("--port", type=int, dest="port", help="mysql port")
    parser.add_argument("--user", type=str, dest="user", help="mysql user")
    parser.add_argument("--password", type=str, dest="password", help="mysql password")
    parser.add_argument("--log-file", type=str, dest="log_file", help="")
    parser.add_argument("--start-file", type=str, dest="start_file", help="")
    parser.add_argument("--start-pos", type=int, dest="start_pos", help="mysql password")
    parser.add_argument("--end-pos", type=int, dest="end_pos", help="")
    parser.add_argument("--end-file", type=str, dest="end_file", help="")
    parser.add_argument("--out-file", type=str, dest="out_file", help="")
    args = parser.parse_args()
    if not args.host or not args.port or not args.user or not args.password or not args.log_file or not args.start_pos or not args.end_pos:
        print(parser.format_usage())
        sys.exit(1)

    return args

class BinlogProcess():
    def __init__(self):
        pass

    def check_log_file(self):
        pass

    def convert_binlog_to_sql(self):
        pass

    def sql_format(self, dic, split_value):
        list = []
        for key, value in dic.items():
            if (value == None):
                list.append("`%s`=null" % key)
                continue
            if (isinstance(value, int)):
                list.append("`%s`=%d" % (key, value))
            else:
                list.append("`%s`='%s'" % (key, value))
        return split_value.join(list)

    def sql_format_2(self, values):
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

if(__name__ == "__main__"):
    print("test")