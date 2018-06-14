#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
    A Classifier Project For MZC base 
    1. paramter check
    2. judge if is brand or not , and select dm or return sorry
    3. preprocess
    4. predict
    5. return result
'''
import sys
import json
import logging
sys.path.insert(0, "/home/zzg/liuhongyu/anaconda2/lib/python2.7/site-packages/intelligent")
sys.path.insert(0, "/home/zzg/liuhongyu/anaconda2/lib/python2.7/site-packages/")
from intelligent.common.util import *
from intelligent.model.t_feature_word import TFeatureWord
from intelligent.model.t_opinion_word import TOpinionWord
from intelligent.model.t_intelligent_log import TIntelligentLog
from intelligent.common.exldeal import XLSDeal
import traceback

SERVER = 'server'
LOGTYPE = 'logtype'
INDUSTRY = 'industry'
LINK = 'link'
TARGET = 'target'
SOURCE = 'source'
TILTE = 'title'
ABSTRACT = 'abstract'
CONTEXT = 'context'
REASON = 'reason'
PREDTYPE = 'predtype'
PREDPROB = 'predprob'
PREDALL = 'predall'
RETAIN = 'retain'

@singleton  
class SemevalStrategy():
    
    def __init__(self):
        self.errLogger = logging.getLogger("platform.error")
        self.TFW = TFeatureWord()
        self.TOW = TOpinionWord()
        self.TIL = TIntelligentLog()
    
    def querylog(self, url, target):
       
        target = target.strip()
        url = url.strip()
        if target == '':
            ret = self.TIL.queryby_url(url)
        else:
            ret = self.TIL.queryby_url_target(url, target)
        res = []
        for item in ret:
            for key in item:
                elem = '%s:%s' % (key, str(item[key]))
                res.append(elem)
        #res = json.dumps(res)
            res.append('\n----------------------------------------\n')
        return res
   
   
    def __jcard(self, s1, s2):
        s1= set(s1.decode('utf-8'))
        s2= set(s2.decode('utf-8'))
        sim = float(len(s1 & s2)) / float(len(s1 | s2))
        return sim

    def __getBestReason(self, abst, ret):
        simin = -1
        bestreason = 'not find'
        for item in ret:
            abst0 = item['abstract']
            reason = item['reason']
            sim = self.__jcard(abst0, abst)
            if sim > simin:
                simin = sim
                bestreason = reason
        return bestreason
            

    def querymanylog(self, input = '' , output = ''):

        lText = []
        try:
            #dump xls to txt
            lLines = XLSDeal().XlsToList(input)
            for line in lLines:
                fs = line.strip().split('\t')
                if len(fs) < 3:
                    continue
                entryid = fs[0].strip()
                url = fs[1].strip()
                abst = fs[2].strip()
                ret = self.TIL.query_by_entryidurl(entryid, url)
                reason = self.__getBestReason(abst, ret)
                fs.insert(0, reason)
                lText.append("\t".join(fs).strip())
        except:
            print traceback.format_exc()
            self.errLogger.error("Raise exception: \n%s\n" % (traceback.format_exc()))
  
        try:              
            XLSDeal().toXlsFile(lText, output)
        except:
            self.errLogger.error("Raise exception: \n%s\n" % (traceback.format_exc()))
    
if __name__ == "__main__":
    ret = SemevalStrategy().querymanylog(input = 'maixun_2017-12-05.xlsx' , output = 'result.xlsx')
    #ret = SemevalStrategy().querylog('http://www.chinatodayclub.com/news/keji/39020.html', '滴滴')
    print ret
