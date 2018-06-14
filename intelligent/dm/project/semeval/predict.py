#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
    online predict

'''

from intelligent.dm.preprocess.cut import cut_text
from intelligent.dm.learn.learner import Learner
from intelligent.dm.project.semeval.server_conf import *
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

    # 加载模型
    def load_model(self):

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
                    self.logger.info("load model " + sfile)
        except:
            sError = "load template file error.  traceback: %s" % traceback.format_exc()
            self.errLogger.error(sError)

    # 预测
    def predict(self, sText='', sClassifier=''):

        '''
           execute predict,include 
           1 pre process
           2 ext feature
           3 predict
           4 ret

        '''
        if sText.strip() == '':
            return c_NO_FEATURE, 0.8, [0.0, 0.0]

        if sClassifier in self.predictors:

            # pre process and feature extract
            # self.features = cut_text(sText)
            self.features = sText

            pred, pred_prob = self.predictors[sClassifier].predict_one(self.features)
            # 如果是2类的，直接返回
            if len(pred_prob[0]) == 2:
                fProb = pred_prob[0][pred[0]]
            else:
                # 如果是三类的，因为是-1，0， 1所以需要+1 ,得到0，1，2才能去列表中的元素
                fProb = pred_prob[0][pred[0] + 1]
            return pred[0], fProb, pred_prob

        return c_NO_VALIDAT, 0.0, [0.0, 0.0]


if __name__ == '__main__':
    bBrand = Predict().predict("刚出生的宝宝你们给她（他）喝什么牌子的奶粉。备了荷兰牛栏2017-05-0815:01...")
