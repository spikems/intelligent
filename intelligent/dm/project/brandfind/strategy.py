#!/usr/bin/python
# -*- coding: utf-8 -*-


'''
    Brand Filter by ESM
    ret:
       industry-brand-text
'''

import json
import logging
import esm
import os, sys
from intelligent.dm.project.brandfind.conf.brand_strategy import dBrandStrategy
from intelligent.model.t_brands import TBrands
from intelligent.model.t_industrys import TIndustrys


class Strategy(object):
    def __init__(self, dBrandInfo):
        self.lBrandStrategy = dBrandInfo['strategy']
        self.dNoIndustry = dict((v, k) for k, v in dBrandInfo['industry'].iteritems())
        self.dBrandDeterIndex = {}
        self.dBrandFdeterIndex = {}
        self.dIndustryDeterIndex = {}
        self.dIndustryFdeterIndex = {}

        self.__load_strategy()

    def __load_strategy(self):
        '''
            build strategy 

        '''
        lAllIndustrys = self.lBrandStrategy[0]
        self.dIndustryDeterIndex, self.dIndustryFdeterIndex = self.__setup_strategy(lAllIndustrys)

        lAllBrands = self.lBrandStrategy[1]
        self.dBrandDeterIndex, self.dBrandFdeterIndex = self.__setup_strategy(lAllBrands)

    def __setup_strategy(self, lRule):

        # setup brands strategy
        dDeter = {}
        dFdeter = {}
        for dRule in lRule:
            oiDeterminer = esm.Index()
            oiFdeterminer = esm.Index()
            if 'brands_name' in dRule:
                if str(dRule['industry']) == '-1':
                    continue
                sKeyword = '%s-%s' % (self.dNoIndustry[str(dRule['industry'])], dRule['brands_name'].strip())
            else:
                sKeyword = dRule['industry_name'].strip()

            sDeterminer = dRule['determiner'].strip().strip('#').strip()
            sFdeterminer = dRule['fdeterminer'].strip().strip('#').strip()
            lDeter = [] if sDeterminer == '' else sDeterminer.split('#')
            lFDeter = [] if sFdeterminer == '' else sFdeterminer.split('#')

            if 'noise_brand' in dRule and dRule['noise_brand'] == 0:
                lDeter = [dRule['brands_name'].strip()]

            # set up index
            if len(lDeter) == 0:
                oiDeterminer = None
            else:
                for sWord in lDeter:
                    oiDeterminer.enter(sWord.lower())
                oiDeterminer.fix()

            if len(lFDeter) == 0:
                oiFdeterminer = None
            else:
                for sWord in lFDeter:
                    oiFdeterminer.enter(sWord.lower())
                oiFdeterminer.fix()

            dDeter[sKeyword] = oiDeterminer
            dFdeter[sKeyword] = oiFdeterminer

        return dDeter, dFdeter

    def excute(self, sIndustry, sBrand, sContext):

        '''
           recongise brand by strategy 

        '''

        lPositionDeter = []
        lPositionFdeter = []
        bBrand = False
        sKeyword = '%s-%s' % (sIndustry, sBrand)
        if not bBrand and sKeyword in self.dBrandDeterIndex:
            lPositionDeter = [] if self.dBrandDeterIndex[sKeyword] is None else self.dBrandDeterIndex[sKeyword].query(
                sContext)
            lPositionFdeter = [] if self.dBrandFdeterIndex[sKeyword] is None else self.dBrandFdeterIndex[
                sKeyword].query(sContext)
            #    bBrand = len(lPositionDeter) and (len(lPositionFdeter) == 0)

            # if not bBrand and sIndustry in self.dIndustryDeterIndex:
            #    lPositionDeter = [] if self.dIndustryDeterIndex[sIndustry] is None else self.dIndustryDeterIndex[sIndustry].query(sContext)
            #    lPositionFdeter = [] if self.dIndustryFdeterIndex[sIndustry] is None else self.dIndustryFdeterIndex[sIndustry].query(sContext)
            # bBrand = len(lPositionDeter) and (len(lPositionFdeter) == 0)

        # fProb = 0.8 if bBrand else 0.0
        return lPositionDeter, lPositionFdeter
        # return fProb


if __name__ == "__main__":
    sT1 = u'参观马场'
    sD1 = u'哎呀，今天在楼下看到了宝马，我老家倒是有养马的'
    sT2 = u'我的邻居'
    sD2 = u'以前的邻居有个奔驰'
    b = '前途'
    c = '哎呀，汽车今天在楼下看到了宝马'
    bStrategyBrand, bResult = BrandStrategy().excute(b, c)
    print bStrategyBrand, bResult
