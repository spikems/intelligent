#!/usr/bin/python
# -*- coding: utf-8 -*-
import json
import time
import sys, time
import requests

'''
    python access.py 3 intention

'''

no = sys.argv[1]
project = sys.argv[2]

ip = '192.168.241.' + no
requrl = "http://%s:8100/tumnus/dm/flm" % ip

for line in sys.stdin:

    #time.sleep(0.2)

    fs = line.strip().split('\t')
    if len(fs) < 3:
       continue
    sId = fs[0]
    sTitle = fs[1]
    sDocument = fs[2]

    sTest = [{"id" : sId, "title" : sTitle, "document": sDocument}]
    sJs = json.dumps(sTest)
    sData = {'project' : project, 'param' : sJs}
    try: 
        req = requests.post(requrl, data = sData)
	print req
        res = req.text
        req.close()
    except:
        logger.error("Raise exception: \n%s\n" % (traceback.format_exc()))
    res = json.loads(res)

    s = ""

    for item in res:
        if project == 'mzcbase':
            print sId, "\t", item['type'], "\t", item['prob']
        if project == 'tongxin':
            print sId, "\t", item['type'],"\t",item['prob']

        if project == 'intention':
            print sId, "\t", item['type']

        if project == 'brandfind':
            
            if item['type'] == 1:
                s = '%s\t%s\t%s\t' % (sId, sTitle, sDocument)
                s = s.decode('utf8')
                for ind in item['result']:
                    s = '%s%s' % (s, ind)
                    for brand in item['result'][ind]:
                        for b in brand:
                            s = '%s %s:%s' % (s, b, brand[b])
                    s = '%s\t' % s
                print s.encode('utf8')
	if project == 'ip':
	    for item in res:
                for name_datas in item['result']:   #{name1: [{},{}]}
		    for name in item['result'][name_datas]:    # [{},{}]
               	    	print item['id'], "\t", name_datas, "\t", name['type'], "\t", name['prob']
