#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import esm
import re
from intelligent.dm.project.semeval.server_conf import *


class RulePreprocess:
    '''
          semeval rule preprocess classifier
    '''

    def __init__(self, index, brand_index, text, dWordType, brand):

        self.brand_index = brand_index
        self.index = index
        self.text = text
        self.dWordType = dWordType
        self.brand = brand

    # 取出关键词前后的文本，截止到下一个监控词出现
    def getAfterTargetText(self):

        '''
                    extract text after keyword and ccombine the paral brand
        '''

        lRet = self.index.query(self.text)
        sentences = re.split('。|！|!|；|;|？|\?', self.text)
        target_texts = []
        for sentence in sentences:
            firstIsTarget = True
            start = 0
            end = -1
            preType = ''
            prePos = 0
            lRet = self.index.query(sentence)
            for item in lRet:
                word = item[1]
                pos = item[0][0]
                Type = self.dWordType[word]
                # print word, pos, Type

                if word.find(self.brand) != -1 or self.brand.find(word) != -1:
                    word = self.brand

                if Type == c_BRAND_FEAT:
                    if firstIsTarget:
                        if word == self.brand:
                            start = pos
                            preType = c_TARGET_FEAT
                        else:
                            preType = c_BRAND_FEAT
                        firstIsTarget = False
                    else:
                        if word == self.brand and preType != c_TARGET_FEAT:
                            start = pos
                            preType = c_TARGET_FEAT
                        elif word != self.brand and preType == c_TARGET_FEAT and (pos - prePos) > len(self.brand) + 3:
                            end = pos
                            out = sentence[start: end]
                            iLastP = self.findLastFuhao(out)
                            out = out if iLastP == -1 else out[: iLastP]
                            target_texts.append(out)
                            start = pos
                            end = -1
                            firstIsTarget = True
                    prePos = pos
            if end == -1 and preType == c_TARGET_FEAT:
                out = sentence[start:]
                target_texts.append(out)

        return "。".join(target_texts)

    def findLastFuhao(self, s):

        fuhaos = ['...', '，', ',']
        maxNum = -1
        for fuhao in fuhaos:
            pos = s.rfind(fuhao)
            if pos > maxNum:
                maxNum = pos
        return maxNum

    # 多个并列的品牌算一个
    def paralBrandDeal(self):

        '''
             paral brand to one brand or one target
        '''
        # strr = '【大众召回DSG故障车型明细】尚酷1.4TSI、高尔夫旅行车、CrossGolf ；新宝来1.4T、高尔夫A61.4T、高尔夫A61.6L、速腾1.4T、迈腾1.4T、CC1.8T、新速腾1.4T、新迈腾1.4T、新迈腾1.8T、奥迪A31.8T；途安5座1.4T、途安7座1.4T、明锐1.8T、明锐1.4T、朗逸1.4T、昊锐1.4T、新www.ttcw168.net萨特1.8T。'
        fs = self.text.split('、')
        st = 0
        et = 0
        icnt = 0
        paral_sents = []
        otherbrand = ''
        if len(fs) > 2:
            brands = self.brand_index.query(self.text)
            if len(brands) > 1:
                preBrand = brands[0][1]
                prePos = brands[0][0][0]
                st = prePos
                icnt = 1

                for brandinfo in brands[1:]:
                    feat = brandinfo[1]
                    iStartPos = brandinfo[0][0]
                    iEndPos = brandinfo[0][1]
                    if feat != self.brand:
                        otherbrand = feat

                    if iStartPos - prePos > 10 * 3:
                        if et != 0:
                            paral_sents.append([st, et, icnt])
                            # print 'para text:', self.text[st : et]
                            et = 0
                            icnt = 0
                        st = iStartPos
                        preBrand = feat
                        prePos = iStartPos
                        continue

                    # print feat, iStartPos, iEndPos
                    if self.isSymbolInText(self.text[prePos: iStartPos]):
                        # print 'fuhaofenge', feat, iStartPos, st, et
                        et = iEndPos
                        icnt += 1
                    elif prePos + len(preBrand) >= iStartPos:
                        et = iEndPos
                        continue
                    else:  # 没出现
                        # print 'brand', feat, iStartPos, st, et
                        if et != 0:
                            paral_sents.append([st, et, icnt])
                            # print 'para text:', self.text[st : et]
                            et = 0
                            icnt = 0
                        st = iStartPos

                    preBrand = feat
                    prePos = iStartPos
                if et != 0:
                    paral_sents.append([st, et, icnt])
                    # print 'final', st,et

        beg = 0
        result = ''
        for pos_ in paral_sents:
            st = pos_[0]
            et = pos_[1]
            piece = self.text[st: et]
            middle = self.brand if self.brand in piece else otherbrand
            result = '%s%s%s' % (result, self.text[beg: st], middle)
            beg = et
        result = '%s%s' % (result, self.text[beg: len(self.text)])
        # print 'result', result
        return result

    def isSymbolInText(self, text):
        symbols = ['、', '；']
        for sym in symbols:
            if sym in text:
                return True
        return False
