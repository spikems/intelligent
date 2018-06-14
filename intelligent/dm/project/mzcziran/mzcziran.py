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

import json
import logging
from intelligent.dm.project.mzcziran.predict import Predict
from intelligent.dm.project.mzcziran.shuijun import *
from intelligent.common.util import *
import traceback


@singleton  
class MZCZiranServer():
    
    def __init__(self):
        self.logger = logging.getLogger("intelligent")
        self.errLogger = logging.getLogger("errinfo")
        self.oPR = Predict()
            
    def run(self, lParams):
        
        lDocsRet = []    

        #deal shuijun
        lParams,shuijun = shuijun_deal(lParams)
 
        for dDoc in lParams:
            
            try:
                self.sId = trim(dDoc['id'])
                self.sTitle = trim(dDoc['title'])
                self.sDocument = trim(dDoc['document'])
                      
                iType, fProb, tPredProb  = self.__predict()
                sProb = '%0.4f' % fProb

                lDocsRet.append({'id' : self.sId, 'type' : iType, 'prob' : sProb})

                sLog = '%s  |  %s  |  %s  |  type:%s-%s  |  %s ' % (self.sId, self.sTitle, self.sDocument, iType, sProb, tPredProb)
                self.logger.info(sLog)

            except:
                sError = "master for cycle : param : %s   traceback: %s" % (str(dDoc), traceback.format_exc())
                print sError
                self.errLogger.error(sError)
                
	lDocsRet = lDocsRet + shuijun
        jResult = json.dumps(lDocsRet)
        return  jResult

    def __predict(self):
          
        sText = '%s。%s' % (self.sTitle, self.sDocument)
        iType, fProbR, tPredProb = self.oPR.predict(sText)
        
        return iType, fProbR, tPredProb
                    
    def __desicionMaking(self, fProbP, fProbR):
        pass


    def __check(self, sIndustry = ""):
      
        '''
           logistic check
 
        '''
        pass

if __name__ == "__main__":
      
    sTitle = u"刚出生的宝宝你们给她（他）喝什么牌子的奶粉"
    sText =u'备了荷兰牛栏2017-05-0815:01...'
    bResult = MZCZiranServer().run([{'id' : u'1', 'title' : sTitle, 'document' : sText}])
    print bResult




