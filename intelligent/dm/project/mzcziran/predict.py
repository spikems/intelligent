#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
    online predict

'''

from intelligent.dm.preprocess.cut import cut_text
from intelligent.dm.learn.learner import Learner
from intelligent.dm.project.mzcziran.server_conf import *
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

    def zr_feature_add(self,result):

        num_word = [0,0,0,0,0]
        add_words = ''
        for word in result.split(' '):
            if word in dict_shopping:
                num_word[4]+=1
            if word in dict_news:
                num_word[0]+=1
            if word in dict_ask:
                num_word[1]+=1
            if word in dict_feeling:
                num_word[2]+=1
            if word in dict_else:
                num_word[3]+=1

        if num_word[0] == 1:
            add_words=' new_special_1'
        elif num_word[0] > 1:
            add_words=' new_special_2 new_special_1'
        if num_word[1] == 1:
            add_words=add_words + ' ask_special_1'
        elif num_word[1] > 1:
            add_words=add_words + ' ask_special_2 ask_special_1'
        if num_word[2] == 1:
            add_words=add_words + ' feeling_special_1'
        elif num_word[2] > 1:
            add_words=add_words + ' feeling_special_2 feeling_special_1'
        if num_word[3] == 1:
            add_words=add_words + ' else_special_1'
        elif num_word[3] > 1:
            add_words=add_words + ' else_special_2 else_special_1'
        if num_word[4] == 1:
            add_words=add_words + ' shopping_special_1'
        elif num_word[4] > 1:
            add_words=add_words + ' shopping_special_2 shopping_special_1'
        add_word = add_words.strip()
        result = '%s %s'%(result,add_word)
        return  result

    def predict(self, sText = ''):

        '''
           execute predict,include 
           1 pre process
           2 ext feature
           3 predict
           4 ret

        '''
        sClassifier = 'mzc-6'
        #pre process and feature extract
        self.features = self.zr_feature_add(cut_text(sText))

        pred, pred_prob = self.predictors[sClassifier].predict_one(self.features)
        if pred[0] == 5:
            return pred[0],pred_prob[0][4],pred_prob
        else:
            return pred[0], pred_prob[0][pred[0]], pred_prob


        return 0.0


if __name__ == '__main__':

    bBrand = Predict().predict("刚出生的宝宝你们给她（他）喝什么牌子的奶粉。备了荷兰牛栏2017-05-0815:01...")



