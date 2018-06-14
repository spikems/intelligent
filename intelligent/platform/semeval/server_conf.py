#!/usr/bin/python
# -*- coding: utf-8 -*-

import os

#
#每个行业对应着一个编号，方便用户按照编号请求某个行业服务。
#
c_industrys = {
    '汽车正负面预测' : '2',
    '网约车正负面预测' : '11'
}

#
#每个行业对应着一个编号，方便用户按照编号请求某个行业服务。
#
c_labels = {
    0 : '中立',
    -2 : '无效',
    1 : '正面',
    -1 : '负面'
}

#
#require more information
#
c_more_project = {
    
}
