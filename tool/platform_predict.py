#encoding:utf-8
import sys
sys.path.insert(0, "/home/zzg/liuhongyu/anaconda2/lib/python2.7/site-packages/intelligent")
sys.path.insert(1, "/home/zzg/liuhongyu/anaconda2/lib/python2.7/site-packages")
sys.path.insert(2, "/home/liuhongyu/intelligent")
from intelligent.platform.predict.predict_server import PredictServer

input = sys.argv[1]

PredictServer().predict(
    projectname = '美赞臣基础预测服务', 
    brands = '夕阳#移动',
    input = input, 
    output = 'out.xlsx'
)

PredictServer().predict(
    projectname = '手机行业品牌识别', 
    input = input,
    output = 'out1.xlsx'
)

print PredictServer().getServers()
