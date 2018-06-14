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
import msgpack
import esm
import logging
from intelligent.dm.project.semeval.preprocess import PreDeal
from intelligent.dm.project.semeval.predict import Predict
from intelligent.common.util import *
from intelligent.dm.project.semeval.server_conf import *
from intelligent.model.t_feature_word import TFeatureWord
from intelligent.model.t_opinion_word import TOpinionWord
from intelligent.model.t_intelligent_log import TIntelligentLog
from intelligent.dm.project.semeval.semevalrule import *
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
class SemevalServer():
    def __init__(self):
        self.logger = logging.getLogger("semeval")
        self.errLogger = logging.getLogger("errinfo")
        self.oPR = Predict()
        self.TFW = TFeatureWord()
        self.TOW = TOpinionWord()
        self.TIL = TIntelligentLog()
        self.dWordMap = {}
        self.dIndex = {}
        self.dBrandIndex = {}
        self.dRuleWordType = {}
        self.dIndustryOpinionSource = {}
        self.dIndustryOpinionPosition = {}
        self.short_sent = ''
        self.dRuleNegInfo = {}
        self.dRuleInquireInfo = {}
        self.dIndustryOpinion = {}
        self.dWords = {}
        self.lRuleResult = []
        self.kongIndex = esm.Index()
        self.kongIndex.fix()
        self.__load_features()
        self.__load_rule_feature()

    # 加载特征
    def __load_features(self):
        lRet = self.TFW.queryAll()
        dSyntax = {}
        for record in lRet:
            name = record['name'].lower()
            Type = record['type'].lower()
            industry = str(record['industry'].lower())
            if industry == '500':
                dSyntax[name] = [Type]
            else:
                if not industry in self.dWordMap:
                    self.dWordMap[industry] = {}
                self.dWordMap[industry][name] = [Type]
        for industry in self.dWordMap:
            self.dWordMap[industry] = dict(self.dWordMap[industry].items() + dSyntax.items())

    # 加载规则需要使用的特征
    def __load_rule_feature(self):

        # laod opinion word
        lRet = self.TOW.queryAll()
        for item in lRet:
            industry = str(item['industry'])
            Type = item['type']
            word = item['word'].lower().strip()
            source = item['source']
            pos = item['position']

            if not industry in self.dRuleWordType:
                self.dRuleWordType[industry] = {}
                self.dIndustryOpinion[industry] = {}
                self.dIndustryOpinionSource[industry] = {}
                self.dIndustryOpinionPosition[industry] = {}
                self.dIndex[industry] = esm.Index()
            self.dRuleWordType[industry][word] = 'opinion'
            self.dIndustryOpinion[industry][word] = Type
            self.dIndustryOpinionSource[industry][word] = source
            self.dIndustryOpinionPosition[industry][word] = pos
            self.dIndex[industry].enter(word)

        # load brand word
        lRet = self.TFW.queryAll()
        for record in lRet:
            name = record['name'].lower().strip()
            Type = record['type'].lower().strip()
            industry = record['industry'].lower().strip()
            if Type != 'brand':
                continue
            if not industry in self.dRuleWordType:
                self.dRuleWordType[industry] = {}
            if not industry in self.dIndex:
                self.dIndex[industry] = esm.Index()
            if not industry in self.dBrandIndex:
                self.dBrandIndex[industry] = esm.Index()
            self.dRuleWordType[industry][name] = Type
            self.dIndex[industry].enter(name)
            self.dBrandIndex[industry].enter(name)

        # load common feature
        sRuleFeatDir = '%s/%s' % (c_project_path, c_RULE_FEATURE)
        featfiles = ['inquire.dict', 'but.dict', 'comp.dict', 'neg.dict']
        try:
            # load general feature
            for industry in self.dIndex:
                for featFile in featfiles:
                    path = '%s/%s' % (sRuleFeatDir, featFile)
                    with open(path, 'r') as fr:
                        for line in fr:
                            fs = line.strip().split('\t')
                            Type = fs[0].strip()
                            word = fs[1].strip().lower()
                            if not industry in self.dRuleWordType:
                                self.dRuleWordType[industry] = {}
                            self.dRuleWordType[industry][word] = Type
                            self.dIndex[industry].enter(word)
                            # neg threshod
                            if Type == c_NEG_FEAT:
                                pos = fs[2].strip()
                                thre = int(fs[3].strip())
                                self.dRuleNegInfo[word] = [pos, thre]
                            # inquire threshod
                            if Type == c_INQUIRE_FEAT:
                                pos = fs[2].strip()
                                thre = int(fs[3].strip())
                                self.dRuleInquireInfo[word] = [pos, thre]

            for industry in self.dIndex:
                self.dIndex[industry].fix()
            for industry in self.dBrandIndex:
                self.dBrandIndex[industry].fix()
        except:
            sError = "load neg feature file error.  traceback: %s" % traceback.format_exc()
            self.errLogger.error(sError)

    def run(self, lParams):

        lDocsRet = []

        for dDoc in lParams:

            try:
                self.sId = trim_plus(dDoc['id'])
                self.sIndustry = trim_plus(dDoc['industry']).lower()
                self.sTitle = dDoc['title'].replace("\n", '').strip().lower()
                self.sDocument = dDoc['document'].replace("\n", '').strip().lower()
                self.sSource = trim_plus(dDoc['type']).lower()
                self.sBrand = trim_plus(dDoc['brand']).lower()
                self.link = trim_plus(dDoc['link']).lower()
                self.entryid = trim_plus(dDoc['entryid']).lower()

                sent = '%s 。 %s' % (self.sTitle, self.sDocument)

                # 提取文本，提取文本sent中所有所有出现监控词sent前后200个字，然后返回
                self.short_sent = PreDeal().getSent(self.sBrand, sent, 200)

                # 将分词得到的所有词转换成字典的key，后面使用
                self.dWords = list2Dict(self.short_sent.strip().split())

                iType = c_NEUTRAL
                fProb = c_PROB_DM_OPINION
                tPredProb = c_NO_INDUSTRY_RESULT
                reason = '没有监控词或者评价词'

                # 检查结果，如果通过，进行预测。得到预测类型，概率，原因。
                if self.__check():
                    iType, fProb, tPredProb, reason = self.__predict(self.short_sent)

                sProb = '%0.4f' % fProb
                lDocsRet.append({'id': self.sId, 'type': iType, 'prob': sProb, 'reason': reason})

                # 打日志
                self.__log([iType, fProb, tPredProb, reason])

                # 如果时模拟状态，则记录日志
                # simulate
                if len(self.lRuleResult) > 0:
                    self.__log(self.lRuleResult, 'simulate')

            except:
                sError = "master for cycle : param : %s   traceback: %s" % (str(dDoc), traceback.format_exc())
                self.errLogger.error(sError)
        return lDocsRet

    # 记录日志
    def __log(self, loginfo, logtype='product'):
        iType = '%s' % loginfo[0]
        tPredProb = '%s' % loginfo[2]
        reason = loginfo[3]
        sProb = '%0.4f' % loginfo[1]
        dR = {
            SERVER: 'semeval',
            LOGTYPE: logtype,
            INDUSTRY: self.sIndustry,
            LINK: self.link,
            TARGET: self.sBrand,
            SOURCE: self.sSource,
            TILTE: self.sTitle,
            ABSTRACT: self.sDocument,
            CONTEXT: self.short_sent,
            REASON: reason,
            PREDTYPE: iType,
            PREDPROB: sProb,
            PREDALL: tPredProb,
            RETAIN: self.entryid
        }
        # insert to mysql log
        self.TIL.insertone(dRecord=dR)

        # record log
        sLog = '  %s  |  industry:%s  |  %s  |  %s  |  %s  |  %s  |  %s  |  %s  |  %s  |  %s  |  type:%s-%s  |  %s ' % (
        logtype, self.sIndustry, self.link, self.entryid, self.sBrand, self.sSource, self.sTitle, self.sDocument,
        self.short_sent, reason, iType, sProb, tPredProb)
        self.logger.info(sLog)

    # 过规则
    def __rules(self, short_sent, high_precision=False):
        # 准备规则
        dSemevalInfo = self.__rule_prepare(short_sent)
        oSR = SemevalRule(dSemevalInfo)
        # 过规则,是否命中，预测类别，概率，命中原因
        bRuleValid, iType, fProb, reason = oSR.run(high_precision)
        return bRuleValid, iType, fProb, reason

    def __rule_prepare(self, short_sent):

        # 下面即那个所有需要过规则的信息封装成一个dict，传递给dSemevalInfo。然后
        sIndustry = self.sIndustry
        dWordType = {} if not sIndustry in self.dRuleWordType else self.dRuleWordType[sIndustry]
        indu_index = self.dIndex[sIndustry] if sIndustry in self.dIndex else self.kongIndex
        brand_index = self.dBrandIndex[sIndustry] if sIndustry in self.dBrandIndex else self.kongIndex
        indu_opinion = {} if not sIndustry in self.dIndustryOpinion else self.dIndustryOpinion[sIndustry]
        dOpinionSource = {} if not sIndustry in self.dIndustryOpinionSource else self.dIndustryOpinionSource[sIndustry]
        dOpinionPosition = {} if not sIndustry in self.dIndustryOpinionPosition else self.dIndustryOpinionPosition[
            sIndustry]
        dSemevalInfo = {
            c_ID: self.sId,
            c_INDUSTRY: self.sIndustry,
            c_SHORTSENT: short_sent.replace(' ', ''),
            c_TYPE: self.sSource,
            c_BRAND: self.sBrand,
            c_LINK: self.link,

            c_SENT_WORDS: self.dWords,
            c_WORDTYPE: dWordType,
            c_OPINION_SOURCE: dOpinionSource,
            c_OPINION_POSITION: dOpinionPosition,
            c_WORDNEGINFO: self.dRuleNegInfo,
            c_WORDINQUIREINFO: self.dRuleInquireInfo,
            c_INDEX: indu_index,
            c_BRAND_INDEX: brand_index,
            c_SEMEVAL_OPINION: indu_opinion
        }
        return dSemevalInfo

    def __predict(self, short_sent):

        iType = c_NEUTRAL
        reason = ''
        fProb = c_PROB_DM_OPINION
        bRuleValid = False
        self.lRuleResult = []

        # high precision rule
        if self.sIndustry in c_semeval_rule and 'high' in c_semeval_rule[self.sIndustry]:
            bRuleValid, iType0, fProb0, reason0 = self.__rules(short_sent, high_precision=True)
            tPredProb0 = c_RULE_PRED_RESULT
            # if rule valid, then get the result.
            if bRuleValid:
                if c_semeval_rule[self.sIndustry]['high'] == 'prod':
                    iType = iType0;
                    reason = reason0;
                    fProb = fProb0;
                    tPredProb = tPredProb0
                    return iType, fProb, tPredProb, reason
                else:
                    self.lRuleResult = [iType0, fProb0, tPredProb0, reason0]

        # model predict
        if self.sIndustry in c_semeval_model:
            feattype = c_semeval_model_feattype[self.sIndustry]
            self.feats = PreDeal().getModelFeats(short_sent, self.dWordMap[self.sIndustry], self.sBrand, feattype)
            reason = self.feats
            tPredProb = c_NO_TARGET_OR_OPINION_RESULT
            if self.feats.strip() != '':
                sClassifier = c_semeval_model[self.sIndustry]
                iType, fProbR, tPredProb = self.oPR.predict(sText=self.feats, sClassifier=sClassifier)
                iType, fProb = self.__desicionMaking(iType, fProbR)

        # low precision predict
        # 1. 这个行业有规则
        # 2. 模型和高精度的规则没有预测出负面
        # 3. 高精度的规则没有被命中，即没有后生效
        # 4. 这个行业有低精度的规则
        if self.sIndustry in c_semeval_rule and iType in (c_POSITIVE, c_NEUTRAL) and not bRuleValid and 'low' in \
                c_semeval_rule[self.sIndustry]:
            bRuleValid, iType0, fProb0, reason0 = self.__rules(short_sent)
            tPredProb0 = c_RULE_PRED_RESULT
            # if rule valid, then get the result.
            if bRuleValid:
                if c_semeval_rule[self.sIndustry]['low'] == 'prod':
                    iType = iType0;
                    reason = reason0;
                    fProb = fProb0;
                    tPredProb = tPredProb0
                else:
                    self.lRuleResult = [iType0, fProb0, tPredProb0, reason0]
            elif self.sIndustry != '11' and self.sIndustry in self.dIndex:
                index = self.dIndex[self.sIndustry]
                ret = index.query(short_sent)
                for item in ret:
                    opinion = item[1]
                    if opinion in self.dIndustryOpinionSource[self.sIndustry] and \
                                    self.dIndustryOpinionSource[self.sIndustry][opinion] == c_DATA_OPINION:
                        iType = c_NEGTIVE;
                        reason = 'rule_datagroup_opinion_%s' % opinion;
                        fProb = c_PROB_DATA_OPINION_NO_RULE;
                        tPredProb = tPredProb0
        return iType, fProb, tPredProb, reason

    def __desicionMaking(self, iType, fProb):

        if iType == c_NO_VALIDAT:
            return iType, fProb
        if iType == c_NO_FEATURE:
            return c_NEUTRAL, fProb

        if self.sIndustry in c_3_class:
            return iType, fProb

        else:
            # 默认的为两类，0.5为阈值
            fNegThre = 0.5
            fNeuThre = 0.5
            # 拿到每一类的阈值
            if self.sIndustry in c_industry_neg_thre:
                # 负面预测概率>=fNegThre为负面，[fNeuThre,fNegThre)为中立，小于fNeuThre为正面
                fNegThre = c_industry_neg_thre[self.sIndustry][-1]
                fNeuThre = c_industry_neg_thre[self.sIndustry][0]

            # 负面预测概率
            fNegPredit = fProb if iType == 0 else (1 - fProb)

            if fNegPredit >= fNegThre:
                return c_NEGTIVE, fNegPredit
            elif fNegPredit >= fNeuThre:
                return c_NEUTRAL, fNegPredit
            else:
                return c_POSITIVE, (1 - fNegPredit)

    def __check(self):

        '''
           logistic check
 
        '''
        # 文本中没有品牌
        if self.short_sent.find(self.sBrand) == -1:
            return False

        # 行业模型或者规则没有准备好
        if self.sIndustry in c_semeval_model or self.sIndustry in c_semeval_rule:
            return True
        return False


if __name__ == "__main__":

    for line in sys.stdin:
        fs = line.strip().split('\t')
        # if len(fs) < 6:
        #    continue
        semeval = '1'
        id = '1'
        target = '路虎'
        title = ''
        link = 'dea1ler'
        abst = '路虎被坑惨'
        industry = '2'
        dText = {'entryid': '1', 'link': link, 'id': id, 'industry': industry, 'title': title, 'document': abst,
                 'brand': target, 'type': '论坛'}
        bResult = SemevalServer().run([dText])
        out = '%s\t%s\t%s\t%s\t%s\t%s\t%s' % (
        semeval, bResult[0]['type'], id, bResult[0]['reason'], target, title, abst.replace(' ', ''))
        print out


        # sTitle = "但是宝马丰田 没 安全性高 了 汽车"
        # sText = '宝马丰田 没 安全性高 了 汽车'
        # bResult = SemevalServer().run([{'link' : 'deal1er', 'id' : '1', 'industry' : '2', 'title' : sTitle, 'document' : sText, 'brand' : '丰田', 'type' : '论坛'}])
        # print bResult
