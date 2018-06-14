#!/usr/bin/python
# -*- coding: utf-8 -*-
import json
import msgpack
import time
import chardet
import sys, time
import requests
#from intelligent.dm.project.semeval.master import predict

'''
    python access.py 3 intention

'''

no = sys.argv[1]
ip = '192.168.241.' + no
requrl = "http://%s:8099/tumnus/dm/flm" % ip

for line in sys.stdin:

    #time.sleep(0.2)

    fs = line.strip().split('\t')
    if len(fs) < 4:
       continue
    sId = fs[0]
    sTitle = fs[1]
    sDocument = fs[2]
    sIndustry = fs[3]
    sType = fs[4]
    sBrand = fs[5]
    #link = fs[6]
    link = 'deal1er'
    print sId, sTitle, sDocument , sIndustry, sType, 'brand', sBrand 

    sTest = [{"id" : sId, "title" : sTitle, "document": sDocument, 'industry' : sIndustry, 'link' : link, 'type' : sType, 'brand' : sBrand}]
    sJs = msgpack.packb(sTest)
    #res = predict(sJs)
    dData = {'project' : 'semeval', 'param' : sJs.decode('ISO-8859-2')}
    try: 
        req = requests.post(requrl, data = dData)
        res = req.text
        req.close()
    except:
        logger.error("Raise exception: \n%s\n" % (traceback.format_exc()))

    sParam = res.encode('ISO-8859-2', 'ignore')
    res = msgpack.unpackb(sParam)

    s = ""

    for item in res:
        print sId, "\t", item['type'], "\t", item['prob']
