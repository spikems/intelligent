#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
    online predict

'''

from intelligent.dm.preprocess.cut import cut_text_plus
from intelligent.dm.learn.learner import Learner
import os
import sys
import logging
import traceback


class Predict(object):
    def __init__(self):
        self.predictors = {}
        self.lFeatureTemplate = []
        self.features = ""
        self.sProjectPath = os.path.dirname(os.path.realpath(__file__))
        self.load_model()
        self.load_template()

    def load_model(self):
        logger = logging.getLogger("intelligent")
        path = '%s/%s' % (self.sProjectPath, 'model')
        try:
            lFiles = os.listdir(path)
            for sfile in lFiles:
                if not sfile.find('pkl') == -1:
                    sfilename = sfile[:-4]
                    predictor = Learner(train=False)
                    predictor.load_model(path + "/" + sfilename)
                    self.predictors[sfilename] = predictor

                    # record log
                    logger.info("load model " + sfilename)
        except:
            sError = "load model file error.  traceback: %s" % traceback.format_exc()
            logger.error(sError)

    def load_template(self):
        logger = logging.getLogger("intelligent")
        path = '%s/%s' % (self.sProjectPath, 'conf/template')
        try:
            oReader = open(path, 'rb')
            for sLine in oReader.readlines():
                self.lFeatureTemplate.append(sLine.strip())

        except:
            sError = "load template file error.  traceback: %s" % traceback.format_exc()
            logger.error(sError)

    def predict(self, sClassifier, dBrand, sBrand):

        '''
           execute predict,include 
           1 pre process
           2 ext feature
           3 predict
           4 ret

        '''

        # pre process and feature extract
        sContext = dBrand[sBrand]
        isBrandWord, self.features = cut_text_plus(sContext, False, self.lFeatureTemplate, dBrand, sBrand)

        # predict
        bIsBrand = False
        sProb = ''
        if isBrandWord and sClassifier in self.predictors:
            pred, pred_prob = self.predictors[sClassifier].predict_one(self.features)
            return pred_prob[0][0]

        return 0.0


if __name__ == '__main__':
    bBrand = Predict().predict('car', "参观场天在楼下到宝马")
