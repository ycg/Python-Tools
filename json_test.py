__author__ = 'Administrator'


import json


data = {
'name' : 'ACME',
'shares' : 100,
'price' : 542.23
}

json_str = json.dumps(data)
print(json_str)

print(json.loads(json_str))