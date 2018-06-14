#!/usr/bin/python
# -*- coding: utf-8 -*-
from intelligent.dm.project.ip.ip_discern import IpDiscern
import json
import sys


def predict(json_data_param):  # 目前默认用影视处理
    list_data = json.loads(json_data_param)
    result_list_data = IpDiscern().run(list_data)
    result_json_data = json.dumps(result_list_data)
    return result_json_data

if __name__ == '__main__':
    param = [{'ip_type': 'all'}
            ]
    param = json.dumps(param)
    predict(param)
