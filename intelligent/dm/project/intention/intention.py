#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
    A Classifier Project For Brand Find
    1. paramter check
    2. judge if is brand or not , and select dm or return sorry
    3. preprocess
    4. predict
    5. return result
'''

import json
import logging
from intelligent.dm.project.intention.predict import Predict
from intelligent.common.util import *
import traceback


@singleton  
class IntentionServer():
    
    def __init__(self):
        self.logger = logging.getLogger("intelligent")
        self.errLogger = logging.getLogger("errinfo")
        self.oPR = Predict()
    
    def run(self, lParams):
        
        lDocsRet = []    
 
        for dDoc in lParams:
            
            try:
                self.sId = trim(dDoc['id'])
                self.sTitle = trim(dDoc['title'])
                self.sDocument = trim(dDoc['document'])
             
                fProbP, fProbR  = self.__predict()

                iPurChase, iRecommend = self.__desicionMaking(fProbP, fProbR)

                sProbP = '%0.4f' % fProbP
                sProbR = '%0.4f' % fProbR
                lDocsRet.append({'id' : self.sId, 'type' : iRecommend, 'prob' : sProbR})

                sLog = '%s  |  %s  |  %s  |  is_buy:%s-%s  |  is_rec:%s-%s ' % (self.sId, self.sTitle, self.sDocument, iPurChase, sProbP, iRecommend, sProbR)
                self.logger.info(sLog)

            except:
                sError = "master for cycle : param : %s   traceback: %s" % (str(dDoc), traceback.format_exc())
                self.errLogger.error(sError)
                

        jResult = json.dumps(lDocsRet)     
        return jResult

    def __predict(self):
 
        fProbP = 0 #self.oPR.predict('purchase', lCorpusText[0])
        fProbR = self.oPR.predict('recommend', self.sTitle)
     
        return fProbP, fProbR
                    
    def __desicionMaking(self, fProbP, fProbR):

        iPurChase = 0
        iRecommend = 0
        if fProbP > 0.5:
            iPurChase = 1
        if fProbR > 0.5:
            iRecommend = 1

        return iPurChase, iRecommend

    def __check(self, sIndustry = ""):
      
        '''
           logistic check
 
        '''
        pass

