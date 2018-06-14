# -*- coding: utf-8 -*-

import json
import logging
import traceback
import sys
import requests
import logging.config
import os
from intelligent.model.t_brands import TBrands
from intelligent.common.util import *

class BrandsStrategy:

    '''
            platform brands strategy configure 

    '''

    def __init__(self):

        self.oTBrands = TBrands()  
        self.dMessage = {1:'品牌策略添加成功！', 2 : '删除品牌策略成功!', 4 : '删除品牌策略失败，品牌库没有该品牌！', 5: '添加品牌策略失败，品牌库里没有该品牌，请联系品牌维护人员添加该品牌后再添加该策略！', 6 : '对不起，品牌库里没有该品牌，请联系品牌维护人员添加该品牌!'}

    def run(self, type = '', industry = '', keyword = '', andword = '', notword = '', action = ''):
        keyword = keyword.strip()
        industry = industry.strip()
        andword = andword.strip().strip('#').strip()
        notword = notword.strip().strip('#').strip()
        lRes = self.oTBrands.queryBrands(keyword, industry)
        if action == '添加':
            iRet = self.addBrandStrategy(lRes, keyword, andword, notword, industry)
            return iRet < 4, self.dMessage[iRet]

        elif action == '删除':
            iRet = self.deleteBrandStrategy(lRes, keyword, andword, notword, industry)
            return iRet < 4, self.dMessage[iRet]
        
        elif action == '查询':
            if len(lRes) == 0:
                iRetNumber = 6
                return False, self.dMessage[iRetNumber]

            dRet = lRes[0]
            del dRet['update_time']
            return True, dRet 
 
        return False, 'menu option error!'

    def deleteBrandStrategy(self, lRes, keyword, andword, notword, industry):
        iRetNumber = 2
        if len(lRes) == 0:
            iRetNumber = 4
            return iRetNumber
        record = lRes[0]
        ldb = [] if record['determiner'].strip() == '' else record['determiner'].split('#')
        lnew = [] if andword.strip() == '' else andword.split('#')
        determiner = "#".join([item for item in ldb if item not in lnew])

        ldb = [] if record['fdeterminer'].strip() == '' else record['fdeterminer'].split('#')
        lnew = [] if notword.strip() == '' else notword.split('#')
        fdeterminer = "#".join([item for item in ldb if item not in lnew])
        self.oTBrands.updateBrands(sBrand = keyword, sDeterminer = determiner, sFdeter = fdeterminer, sIndustry = industry)
        return iRetNumber
        
    def addBrandStrategy(self, lRes, keyword, andword, notword, industry):

        iRetNumber = 1
        if len(lRes) == 0:
            iRetNumber = 5
            return iRetNumber
        else:
            record = lRes[0]
            ldb = [] if record['determiner'].strip() == '' else record['determiner'].split('#')
            lnew = []
            for sWord in andword.strip().split('#'):
                if sWord.strip() != '':
                    lnew.append(sWord.strip())
            determiner = '#'.join(set(ldb + lnew))
                    
            ldb = [] if record['fdeterminer'].strip() == '' else record['fdeterminer'].split('#')
            lnew = []
            for sWord in notword.strip().split('#'):
                if sWord.strip() != '':
                    lnew.append(sWord.strip())
            fdeterminer = '#'.join(set(ldb + lnew))
            self.oTBrands.updateBrands(sBrand = keyword, sDeterminer = determiner, sFdeter = fdeterminer, sIndustry = industry)
            
        return iRetNumber

    def queryBrandStrategy(self, keyword, industry):
        lRes = self.oTBrands.queryBrands(sBrand = keyword, sIndustry = industry)
        return lRes[0]
 
    def getServers(self):
        pass

if __name__ == '__main__':
    ret, message = Strategy().run(
        type = '行业', 
        keyword = '母婴', 
        #andword = '',
        andword = '奶粉',
        notword = '',
        action = '添加'
        #action = '删除'
    )


    print ret, message
