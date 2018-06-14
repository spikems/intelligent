#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
    online predict

'''

from intelligent.dm.preprocess.cut import cut_text
from intelligent.dm.learn.learner import Learner
import os
import sys
import logging
import traceback

class Predict(object):

    def __init__(self):

        self.predictors = {}   
        self.sProjectPath = os.path.dirname(os.path.realpath(__file__))
        self.errLogger = logging.getLogger("errinfo")
        self.logger = logging.getLogger("intelligent")
        self.load_model()


    def load_model(self):
                    
        path = '%s/%s' % (self.sProjectPath, 'model')
        try:
            lFiles =  os.listdir(path)  
            for sfile in lFiles:
                if not sfile.find('pkl') == -1:
                    sfilename = sfile[:-4]
                    predictor = Learner(train = False)
                    predictor.load_model(path + "/" + sfilename)
                    self.predictors[sfilename] = predictor
                    #record log
                    self.logger.info("load model " + sfile)
        except:
            sError = "load template file error.  traceback: %s" % traceback.format_exc()
            self.errLogger.error(sError)

    def predict(self, sText = ''):

        '''
           execute predict,include 
           1 pre process
           2 ext feature
           3 predict
           4 ret

        '''
        sClassifier = 'china_unicom_6_2'
        #pre process and feature extract
        self.features = cut_text(sText)
        #predict
        pred, pred_prob = self.predictors[sClassifier].predict_one(self.features)
        return pred[0], pred_prob[0][pred[0]], pred_prob

        return 0.0


if __name__ == '__main__':
    s2="园内有山有湖，亭桥曲径，联通佳境；花草树"  
    t1,t2,t3 = Predict().predict("s2")
    print t1 ,t2,t3 
