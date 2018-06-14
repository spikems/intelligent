# -*- coding: utf-8 -*-

import json
import time
import uuid
import logging
import datetime
import traceback
import sys
import requests
import md5
import urllib
import urllib2
import hashlib

import dateformatting
from functools32 import lru_cache
from pykafka import KafkaClient
from pykafka.common import OffsetType
sys.path.insert(0, "/home/liuhongyu/intelligent/")
from intelligent.dm.project.intention.master import predict as intentionp
from intelligent.dm.project.brandfind.master import predict as brandfindp

DATA_MIXING_ENABLED = False

# logging configure

import logging.config
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s')
logging.root.setLevel(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def _interface(requrl, project, cache):
            
    sJs = json.dumps(cache)
    sData = {'project' : project, 'param' : sJs}
    try: 
        req = requests.post(requrl, data = sData)
        res = req.text
        req.close()
    except:
        logger.error("Raise exception: \n%s\n" % (traceback.format_exc()))
    return res
        

def _start(project, cache):

    sJs = json.dumps(cache)
    if project == 'intention':
        res = intentionp(sJs)
    elif project == 'brandfind':
        res = brandfindp(sJs)
    return res

def analyse(res, project): 
    res = json.loads(res)
    s = ""

    for item in res:

        if project == 'intention':
            print item['id'], "\t", item['type']

        if project == 'brandfind':
            
            if item['type'] == 1:
                #s = '%s\t%s\t%s\t' % (item['id'], sTitle, sDocument)
                s = '%s\t' % (item['id'])
                s = s.decode('utf8')
                for ind in item['result']:
                    s = '%s%s' % (s, ind)
                    for brand in item['result'][ind]:
                        for b in brand:
                            s = '%s %s:%s' % (s, b, brand[b])
                    s = '%s\t' % s
                print s.encode('utf8')

fpath = sys.argv[1]
way = sys.argv[2]
project = sys.argv[3]
ip = "8"
requrl = "http://192.168.241.%s:8099/tumnus/dm/flm" % ip
cache = []
fdata = open(fpath, 'r')
for line in fdata:
    line = line.strip()
    fs = line.split('\t')
    if line == '' or len(fs) < 3:
        continue
    
    id = fs[0]
    title = fs[1]
    document = fs[2]
    dParam = {'id' : id, 'title' : title, 'document' : document}
    cache.append(dParam)
    if len(cache) < 5:
        continue
    #time.sleep(1)

    try:
        if way == 'start':
            res = _start(project, cache)
        else:
            res = _interface(requrl, project, cache)
        analyse(res, project) 
    except:
        logger.error("Raise exception: \n%s\nWith data: \n%s" % (traceback.format_exc(), cache))

    cache = []
if len(cache) < 500:
    try:
        if way == 'start':
            res = _start(project, cache)
        else:
            res = _interface(requrl, project, cache)
        analyse(res, project) 
    except:
        logger.error("Raise exception: \n%s\nWith data: \n%s" % (traceback.format_exc(), cache))

