#!/usr/bin/python
# -*- coding: utf-8 -*-
import json
import sys
import time

sys.path.insert(0, "/home/liuhongyu/intelligent/")
project = sys.argv[1]

for line in sys.stdin:

    fs = line.strip().split('\t')
    if len(fs) < 3:
       continue
    sId = fs[0]
    sTitle = fs[1]
    sDocument = fs[2]


    stest = [{"id" : sId, "title" : sTitle, "document" : sDocument}]
    js = json.dumps(stest)

    if project == 'intention':
        from intelligent.dm.project.intention.master import predict as intentionp
        res = intentionp(js)
    elif project == 'brandfind':
        from intelligent.dm.project.brandfind.master import predict as brandfindp
        res = brandfindp(js)
    
    res = json.loads(res)
    s = ""

    for item in res:

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


