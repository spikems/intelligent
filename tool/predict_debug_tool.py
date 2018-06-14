#encoding:utf-8
import sys
sys.path.insert(0, "/home/liuhongyu/intelligent")
sys.path.insert(1, "/home/liuhongyu/anaconda2/lib/python2.7/site-packages")
from intelligent.platform.predict.predict_server import PredictServer

#PredictServer().predict(
#    projectname = '美赞臣基础预测服务', 
#    brands = '夕阳#移动',
#    input = 'test.dat.xlsx', 
#    output = 'out.xlsx'
#)

PredictServer().predict(
    projectname = '通信行业识别(仅有策略)', 
    input = 'yidong8-14.xlsx',
    output = 'out1.xlsx'
)

print PredictServer().getServers()
