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

import re
import esm
import json
import logging
from intelligent.model.t_brands import TBrands
from intelligent.model.t_industrys import TIndustrys
from intelligent.model.t_brands_detail import TBrandDetail
from intelligent.model.t_industrys_detail import TIndustryDetail
from intelligent.dm.project.brandfind.brandfilter import BrandFilter
from intelligent.dm.project.brandfind.strategy import Strategy
from intelligent.dm.project.brandfind.predict import Predict
from intelligent.dm.project.brandfind.conf.brand_strategy import dBrandStrategy
from intelligent.dm.project.brandfind.conf.server_conf import *
from intelligent.dm.project.brandfind.didi_rule import DiDiNoiseRule
from intelligent.common.util import *
import traceback
import sys

reload(sys)
sys.setdefaultencoding('utf8')


@singleton
class BrandFindServer():
    def __init__(self):
        self.sModelPath = c_model_path
        self.sProjectPath = c_project_path
        self.logger = logging.getLogger(c_log)
        self.errLogger = logging.getLogger(c_errlog)

        # load brand info from db
        self.dBrandInfo = {}
        self.oTIndustrys = TIndustrys()
        self.oTBrands = TBrands()
        self.dBrandDetailIndex = {}
        self.oInudstryDetail = {}
        self.__load_brand()

        self.oBF = BrandFilter(self.dBrandInfo)
        self.oBS = Strategy(self.dBrandInfo)
        self.oPR = Predict()
        self.oDiDi = DiDiNoiseRule()

        self.sId = ""
        self.sTitle = ""
        self.sDocument = ""
        self.iIndustry_r = ""
        self.dBrandThre = {}

    def __load_brand(self):

        try:

            # load all industry
            lAllIndustrys = lowerDBData(self.oTIndustrys.queryAll())
            # load brand info
            lAllBrands = lowerDBData(self.oTBrands.queryAll())

            # load strategy
            self.dBrandInfo['strategy'] = [lAllIndustrys, lAllBrands]

            # load industry
            dIndustryInfo = {}
            for dIndustry in lAllIndustrys:
                dIndustryInfo[dIndustry['industry_name']] = str(dIndustry['industry_id'])
            self.dBrandInfo['industry'] = dIndustryInfo

            # load brands
            dNoIndustry = dict((v, k) for k, v in dIndustryInfo.iteritems())
            dBrandThre = {}
            dBrandIndustry = {}
            for dBrand in lAllBrands:
                sBrand = dBrand['brands_name']
                fThre = float(dBrand['threshold'])

                if dBrand['industry'] == -1:
                    continue
                sIndustry = dNoIndustry[str(dBrand['industry'])]

                sBrandIndustry = '%s-%s' % (sIndustry, sBrand)
                dBrandThre[sBrandIndustry] = fThre
                if not sBrand in dBrandIndustry:
                    dBrandIndustry[sBrand] = []
                dBrandIndustry[sBrand].append(sIndustry)
            self.dBrandInfo['threshold'] = dBrandThre
            self.dBrandInfo['brand_industry'] = dBrandIndustry

            # load brands detail info
            lBrandDetail = TBrandDetail().queryAll()
            dIndusDetail = TIndustryDetail().queryAllToMap()
            for dBrandDetail in lBrandDetail:
                sBrand = dBrandDetail['brands_name'].strip()
                lTypes = dBrandDetail['types'].strip().split('#')
                indexTmp = esm.Index()
                for sType in lTypes:
                    iType = int(sType)
                    sTypeName = dIndusDetail[iType]['name'].strip()
                    if sTypeName == '':
                        continue
                    self.oInudstryDetail[sTypeName] = sTypeName
                    indexTmp.enter(sTypeName)
                    for name in dIndusDetail[iType]['synonym'].split('#'):
                        if name.strip() != '':
                            self.oInudstryDetail[name.strip()] = sTypeName
                            indexTmp.enter(name.strip())
                indexTmp.fix()
                self.dBrandDetailIndex[sBrand] = indexTmp

        except:
            sError = "load brand error.  traceback: %s" % traceback.format_exc()
            self.errLogger.error(sError)

    def run(self, lParams, bFindHardBrand=False):
        """
        brand finder entry point
        :param lParams:
        :param bFindHardBrand:
        :return:
        """

        lDocsRet = []

        for dDoc in lParams:

            try:
                self.sId = strim(dDoc['id'])
                self.sTitle = strim(dDoc['title'])
                self.sDocument = strim(dDoc['document'])
                self.sIndustry_r = strim(dDoc['industry']) if 'industry' in dDoc else '0'

                dDocRet = {}
                dNotBrandHit = {}
                lResLog = []

                # 文本小写并过滤文本，提取品牌及其相关的文本
                dBrandInfo = self.oBF.filter(self.sTitle.lower(), self.sDocument.lower())
                for sIndustry in dBrandInfo:

                    if not self.__check(sIndustry=sIndustry):
                        continue

                    dBrand = dBrandInfo[sIndustry]
                    sClassifier = c_industry_model[sIndustry]

                    for sBrand in dBrand:
                        fProb = 0.0

                        # 难识别的品牌，放弃识别
                        if sBrand in c_hard_brands and not bFindHardBrand:
                            continue

                        # 对于每一个品牌，用其对应的该行业模型，进行识别
                        if sBrand in c_zheng_brand:  # 先过正向品牌
                            fProb = self.__predict_zheng(sIndustry=sIndustry, sBrand=sBrand, dBrand=dBrand,
                                                         sClassifier=sClassifier)
                        else:
                            fProb = self.__predict(sIndustry=sIndustry, sBrand=sBrand, dBrand=dBrand,
                                                   sClassifier=sClassifier)

                        slog = '%s-%s-%0.4f' % (sIndustry, sBrand, fProb)
                        sText = dBrand[sBrand]

                        if self.__desicionMaking(fProb, sIndustry, sBrand, sText):
                            sProb = '%0.4f' % fProb
                            if not sIndustry in dDocRet:
                                dDocRet[sIndustry] = []
                            # 预测后的品牌，有可能打上细分标签。
                            lBrand = self.__afterPredictDeal(sBrand, sText)
                            for sBrand in lBrand:
                                # 对于模拟待观察的品牌，直接放过,只打日志，不放到返回的字典里。
                                if sBrand in c_simulate_brand:
                                    continue
                                dDocRet[sIndustry].append({sBrand: sProb})
                            slog = '%s-1' % slog
                        else:
                            # not hit
                            dNotBrandHit[sBrand] = fProb
                        lResLog.append(slog)
                lDocsRet.append(
                    {'type': int(len(dDocRet) > 0), 'id': self.sId, 'result': dDocRet, 'nothit': dNotBrandHit})

                sLog = '%s  |  %s  |  %s  | %s |  %s' % (
                self.sId, self.sTitle, self.sDocument, int(len(dDocRet) > 0), " ".join(lResLog))
                self.logger.info(sLog)

            except:
                sError = "cycle | param : %s   traceback: %s" % (str(dDoc), traceback.format_exc())
                self.errLogger.error(sError)

        jResult = json.dumps(lDocsRet)
        return jResult

    # 后处理，对于细分的某些行业细分的品类的，要对返回的品牌加上品类作为返回的结果。比如将识别出来的兰蔻转换成 兰蔻_爽肤水 返回
    def __afterPredictDeal(self, sBrand, sText):

        setBrand = set([sBrand])
        if sBrand in c_brand_transform:
            sBrand = c_brand_transform[sBrand]
            setBrand = set([sBrand])

        if sBrand in self.dBrandDetailIndex:
            lSubText = re.split('。|；|？|！', sText)
            dAppear = {}
            for subText in lSubText:
                if subText.find(sBrand) == -1:
                    continue
                lRet = self.dBrandDetailIndex[sBrand].query(subText)
                for item in lRet:
                    sType = item[1]
                    if sType in dAppear:
                        continue
                    dAppear[sType] = 1
                    sTag = self.oInudstryDetail[sType]
                    sTagBrand = '%s-%s' % (sBrand, sTag)
                    setBrand.add(sTagBrand)

        return setBrand

    def __predict_zheng(self, sIndustry="", sBrand="", dBrand={}, sClassifier=""):

        # 正向 识别非噪音,返回高概率
        lPositionDeter, lPositionFdeter = self.oBS.excute(sIndustry, sBrand, dBrand[sBrand])
        if len(lPositionDeter) > 0:
            return c_strategy_brand_score

        # 模型 识别非噪音，返回概率
        fProb = 0.0
        if (fProb < 0.5) and (not sIndustry in c_only_strategy) and (not sBrand in c_only_strategy_brand):
            fProb = self.oPR.predict(sClassifier, dBrand, sBrand)

        sBrandIndustry = '%s-%s' % (sIndustry, sBrand)
        if fProb > self.dBrandInfo['threshold'][sBrandIndustry]:
            return fProb

        # 模型和正向都没识别出来是非品牌，即都认为是噪音，返回低概率
        # 反向命中 0.0
        if len(lPositionFdeter) > 0:
            return 0.0

        # special for didi
        # 规则命中，返回0.1
        if sBrand == SPECIAL_NOISE_BRAND_DIDI and self.sDocument.strip() != '':
            bNoise, reason = self.oDiDi.run(self.sDocument)
            if bNoise:
                return 0.0

        # 任何规则都没命中，直接返回模型打得分数
        return fProb

    def __predict(self, sIndustry="", sBrand="", dBrand={}, sClassifier=""):

        fProb = 0.0
        lPositionDeter, lPositionFdeter = self.oBS.excute(sIndustry, sBrand, dBrand[sBrand])
        if len(lPositionFdeter) > 0:
            return fProb

        if (fProb < 0.5) and (not sIndustry in c_only_strategy) and (not sBrand in c_only_strategy_brand):
            fProb = self.oPR.predict(sClassifier, dBrand, sBrand)

        sBrandIndustry = '%s-%s' % (sIndustry, sBrand)
        if fProb > self.dBrandInfo['threshold'][sBrandIndustry]:
            return fProb

        if len(lPositionDeter) and (len(lPositionFdeter) == 0):
            return c_strategy_brand_score

        return fProb

    # 根据识别概率，与该品牌阈值，作对比，返回是否是品牌结果
    def __desicionMaking(self, fProb, sIndustry, sBrand, sText):
        if sBrand in c_after_model and all(
                map(lambda x: unicode_string(x) not in unicode_string(sText), c_after_model[sBrand])):
            return False

        sBrandIndustry = '%s-%s' % (sIndustry, sBrand)
        if fProb > self.dBrandInfo['threshold'][sBrandIndustry]:
            return True

        return False

    def __check(self, sIndustry=""):

        '''
           logistic check
 
        '''
        # if server is ready
        # if industry model has no model for sIndustry then return False
        if sIndustry not in c_industry_model:
            return False

        # require specfic industry
        if '0' in self.sIndustry_r.split('#'):
            return True

        if sIndustry not in self.dBrandInfo['industry']:
            return False

        if not self.dBrandInfo['industry'][sIndustry] in self.sIndustry_r.split('#'):
            return False

        return True
