#!/usr/bin/python
# -*- coding: utf-8 -*-


'''
    Brand Filter by ESM
    ret:
       industry-brand-sText
'''

import json
import logging
import esm 
import os, sys 
from intelligent.common.util import *
from intelligent.dm.project.tongxin.predict import Predict

@singleton  
class TongxinServer(object):  

    def __init__(self):  
        self.lstrategy = [] 
        self.zwordindex = esm.Index()
        self.uniomindex = esm.Index()
        self.sProjectPath = os.path.dirname(os.path.realpath(__file__))
        self.sZaoyinPath = '%s/zaoyin.list' % (self.sProjectPath)
        self.unicomdetemeter = '%s/ChinaUniomDetermeter'%(self.sProjectPath)
        self.logger = logging.getLogger("intelligent")
        self.__loadStrategy()
        self.oPR = Predict()

    def __loadStrategy(self):
        f = open(self.sZaoyinPath, 'r')
        for zword in f:
            self.zwordindex.enter(zword.strip().lower()) 
        self.zwordindex.fix()
        self.logger.info("tongxin strategy ready ")
        
        determeterf = open(self.unicomdetemeter,'r')
        for dword in determeterf:
            if len(dword) > 1 :       #一个字的不要
               self.uniomindex.enter(dword.strip().lower())
        self.uniomindex.fix()               
    
 

    def run(self, lParams):

        '''
           recongise brand by strategy 

        '''
  
        lDocsRet = []
        
        for dDoc in lParams:
            
            self.sId = trim(dDoc['id'])
            self.sTitle = trim(dDoc['title']).replace(' ','')
            self.sDocument = trim(dDoc['document']).replace(' ','')
            sText = '%s。%s' % (self.sTitle, self.sDocument)
            bIsNormal = 1      #默认1为非噪音
            fprob = 0.11
             
            
            if not (isContain(sText, '电信') or isContain(sText, '移动')) :  
                bIsNormal = 0
       
            if isContain(sText, '电信') and ( isContain(sText, '日本') or isContain(sText, '瑞典') or isContain(sText, '美国')):
                #1、国外地名+电信视为噪音，如日本，瑞典，美国这种词和电信同时出现
                bIsNormal = 0
            #3, 4 , 5 index
            lPosition = self.zwordindex.query(sText)
            if len(lPosition) != 0:
                bIsNormal = 0
                  
            #联通的用模型判断
            iType, fProbR, tPredProb = self.oPR.predict(sText)
            length =  len(self.uniomindex.query(sText))
            if fProbR >0.60 and length ==0 : 
                bIsNormal = 1
                fprob = fProbR    
            else :
                bIsNormal = 0 
                fprob = fProbR   
            lDocsRet.append({'type': int(bIsNormal), 'id' : self.sId,'prob':fprob})

        jResult = json.dumps(lDocsRet)     
        return jResult

if __name__ == "__main__":
    sTitle = u"中国联通公司"
    sText = u'中国联通公司'
    bResult = TongxinServer().run([{'id' : u'1', 'title' : sTitle, 'document' : sText}])
    print bResult
