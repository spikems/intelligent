# -*- coding: utf-8 -*-

import json
import logging
import traceback
import sys
import requests
import logging.config
import os
from intelligent.model.t_industrys import TIndustrys
from intelligent.common.util import *

class IndustrysStrategy:

    '''
            platform Industrys strategy configure 

    '''

    def __init__(self):

        self.oTIndustrys = TIndustrys()  
        self.dMessage = {1:'行业策略添加成功！', 2 : '删除行业策略成功!', 4 : '删除行业策略失败，没有该行业！', 5: '添加行业策略失败，品牌库里没有该行业，请联系品牌维护人员添加该行业后再添加该策略！', 6 : '对不起，品牌库里没有该品牌，请联系品牌维护人员添加该品牌!'}
        #self.lIndustrys = ['小米', '汽车', '手机数码', '母婴', '运动健身', '娱乐节目', '化妆品', '安利', '时尚']

    
    def run(self, type = '', keyword = '', andword = '', notword = '', action = ''):
        keyword = keyword.strip()
        andword = andword.strip().strip('#').strip()
        notword = notword.strip().strip('#').strip()
         
        lRes = self.oTIndustrys.queryIndustrys(keyword)
        if action == '添加':
            iRet = self.addIndustrystrategy(lRes, keyword, andword, notword)
            return iRet < 4, self.dMessage[iRet]

        elif action == '删除':
            iRet = self.deleteIndustrystrategy(lRes, keyword, andword, notword)
            return iRet < 4, self.dMessage[iRet]

        elif action == '查询':
            if len(lRes) == 0:
                iRetNumber = 6
                return False, self.dMessage[iRetNumber]

            dRet = lRes[0]
            del dRet['update_time']
            return True, dRet 
 
        return False, 'menu option error!'
 
    def deleteIndustrystrategy(self, lRes, keyword, andword, notword):
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
        self.oTIndustrys.updateIndustrys(sIndustry = keyword, sDeterminer = determiner, sFdeter = fdeterminer)
        return iRetNumber
        
    def addIndustrystrategy(self, lRes, keyword, andword, notword):

        iRetNumber = 1
        if len(lRes) == 0:
            iRetNumber = 5
            return iRetNumber
        else:
            record = lRes[0]
            ldb = [] if record['determiner'].strip() == '' else record['determiner'].split('#')
            lnew = [] if andword.strip() == '' else andword.split('#')
            determiner = '#'.join(set(ldb + lnew))
                    
            ldb = [] if record['fdeterminer'].strip() == '' else record['fdeterminer'].split('#')
            lnew = [] if notword.strip() == '' else notword.split('#')
            fdeterminer = '#'.join(set(ldb + lnew))
            self.oTIndustrys.updateIndustrys(sIndustry = keyword, sDeterminer = determiner, sFdeter = fdeterminer)
            
        return iRetNumber

    def queryIndustrystrategy(self, keyword):
        lRes = self.oTIndustrys.queryIndustrys(keyword)
        return lRes[0]
 
    def getIndustrys(self):
        pass
        #return self.lIndustrys

if __name__ == '__main__':
    ret, message = Strategy().run(
        type = '品牌', 
        keyword = '大众', 
        #andword = '',
        andword = '朗逸#迈腾',
        notword = '朋友',
        #action = '添加'
        action = '删除'
    )


    print ret, message
