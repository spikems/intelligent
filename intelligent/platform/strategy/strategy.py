# -*- coding: utf-8 -*-

import json
import logging
import traceback
import sys
import requests
import logging.config
import os
from intelligent.common.util import *
from intelligent.platform.strategy.brands_strategy import BrandsStrategy 
from intelligent.platform.strategy.industrys_strategy import IndustrysStrategy 
from optparse import OptionParser

class Strategy:

    '''
            platform strategy configure 

    '''

    def __init__(self):

        self.oBS = BrandsStrategy()
        self.oIS = IndustrysStrategy()  
        self.industry_no = {
            '小米' : '1', 
            '汽车' : '2',
            '数码' : '3',
            '母婴' : '4', 
            '运动' : '5', 
            '电视' : '6', 
            '美妆' : '7',
            '安利' : '8',
            '时尚' : '9',
            '电商' : '10',
            '网约车' : '11',
            '共享单车' : '12',
            '美食' : '13',
            '教育' : '16'
        }
        self.sLogPath = '%s/../../../logs/platform.error' % (os.path.dirname(os.path.realpath(__file__)))
        self.servers = []
        logging.basicConfig(format='%(asctime)s : %(filename)s[line:%(lineno)d] : %(message)s', filename = self.sLogPath)
        logging.root.setLevel(level=logging.ERROR)
        self.logger = logging.getLogger(__name__)

    def run(self, type = '', industry = '', keyword = '', andword = '', notword = '', action = ''):
        keyword = keyword.strip()
        andword = andword.strip().strip('#').strip()
        notword = notword.strip().strip('#').strip()
        ret = False
        message = ''

        try:
            if type.strip() == '品牌':
                industry = self.industry_no[industry.strip()]
                ret, message = self.oBS.run(industry = industry, keyword = keyword, andword = andword, notword = notword, action = action)
            elif type.strip() == '行业':
                ret, message = self.oIS.run(keyword = keyword, andword = andword, notword = notword, action = action)
        except:
            self.logger.error("Raise exception: \n%s\n" % (traceback.format_exc()))
            
        return ret, message 

    def getServers(self):

        return self.industry_no.keys() 

if __name__ == '__main__':
    #usage = 'python strategy.py  --type <brand or industry> --keyword  <keyword> --andword <andword> --notword <notword> --action <action>'
    #parser = OptionParser(usage)
    #parser.add_option("--type", dest="type")
    #parser.add_option("--keyword", dest="keyword")
    #parser.add_option("--andword", dest="andword")
    #parser.add_option("--notword", dest="notword")
    #parser.add_option("--action", dest="action")
    #opt, args = parser.parse_args()
    #sType = opt.type
    #sKeyword = opt.keyword
    #sAndword = '' if opt.andword is None else opt.andword
    #sNotword = '' if opt.notword is None else opt.notword
    #sAction = opt.action

    #bRet, message = Strategy().run(type = sType, keyword = sKeyword, andword = sAndword, notword = sNotword, action = sAction)
    #print bRet, message
    print Strategy().getServers()
 
    ret, message = Strategy().run(
        type = '行业', 
        keyword = '汽车', 
        #industry = '汽车',
        #andword = '',
        andword = '迈腾',
    #    andword = '迈腾',
    #    notword = '',
        action = '查询'
        #action = '删除'
    )
    print ret, message
