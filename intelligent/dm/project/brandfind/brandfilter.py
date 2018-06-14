#!/usr/bin/python
# -*- coding: utf-8 -*-


'''
    Brand Filter by ESM
    ret:
       industry-brand-text
'''

import json
import logging
import traceback
import esm
import os
import sys
from intelligent.dm.project.brandfind.conf.server_conf import c_project_path


# 过滤品牌的类，提取出品牌
class BrandFilter(object):
    def __init__(self, dIndustryBrand):
        self.index = ''
        self.sProjectPath = c_project_path
        self.dBrand = dIndustryBrand['brand_industry']
        self.__setup_filter()

    # 为每个品牌建立索引
    def __setup_filter(self):

        self.index = esm.Index()
        for sBrand in self.dBrand:
            self.index.enter(sBrand)
        self.index.fix()

    # 过滤品牌，极其相对应的文本
    def filter(self, sTitle, sDocument):

        '''
           recongise brand and extract brand info
           ret:
              industry => {brand1 => text, brand2 => text}

        '''
        sContext = '%s。%s' % (sTitle, sDocument)
        iLength = len(sContext)
        lPositionBrand = self.index.query(sContext)
        dBrandInfo = {}
        lBrandGap = {}
        dBrandi = {}
        dBrandj = {}
        iRange = 3 * 180

        for tPosition, sBrand in lPositionBrand:
            if not sBrand in lBrandGap:
                lBrandGap[sBrand] = []
                dBrandi[sBrand] = tPosition[0]
                dBrandj[sBrand] = tPosition[1]
            else:
                lBrandGap[sBrand].append([dBrandj[sBrand], tPosition[0], (tPosition[0] - dBrandj[sBrand])])
                dBrandj[sBrand] = tPosition[1]
        for sBrand in lBrandGap:
            sText = sTitle
            for iGs, iGe, iGap in lBrandGap[sBrand]:
                if iGap > iRange * 2:
                    iBeg = 0 if (dBrandi[sBrand] - iRange < 0) else dBrandi[sBrand] - iRange
                    iEnd = iGs + iRange
                    sText = "%s。%s" % (sText, sContext[iBeg: iEnd])
                    dBrandi[sBrand] = iGe

            iBeg = 0 if (dBrandi[sBrand] - iRange < 0) else dBrandi[sBrand] - iRange
            iEnd = dBrandj[sBrand] + iRange
            sText = "%s。%s" % (sText, sContext[iBeg: iEnd])

            for sIndustry in self.dBrand[sBrand]:
                if not sIndustry in dBrandInfo:
                    dBrandInfo[sIndustry] = {}
                if not sBrand in dBrandInfo[sIndustry]:
                    dBrandInfo[sIndustry][sBrand] = ""
                dBrandInfo[sIndustry][sBrand] = sText
        return dBrandInfo

    def exist_brand(self, sTitle, sDocument):

        '''
           judge weather brand exist or not
        '''
        sContext = '%s。%s' % (sTitle, sDocument)
        lPositionBrand = self.index.query(sContext)

        dBrand = {}
        for tPosition, sBrand in lPositionBrand:
            sIndustry = self.dBrand[sBrand]
            if sIndustry in ('汽车', '小米', '手机数码', '母婴'):
                dBrand[sBrand] = 1

        return dBrand

    def extract(self, sContext, tPosition, sBrand, ibefore=180, iafter=180):
        iStart = (tPosition[0] - ibefore) if (tPosition[0] - ibefore) > 0 else 0
        iEnd = tPosition[1] + ibefore + (ibefore - tPosition[0] + iStart)
        return sContext[iStart: iEnd]


if __name__ == "__main__":
    sT1 = ''
    sD1 = '亲怎么断的，我家啥奶粉都不吃，而且一哭就哭一夜，因为孩子以前有急性喉炎，怕嗓子哭哑了复发，试过几次断奶都不成功回复  Kay212  2017-04-03 21:00:41发表的一岁一个月断了。吃爱他美白金版的'
    sT2 = u'我的邻居'
    sD2 = u'以前的邻居有个奔驰'
    one = BrandFilter().filter(sT1, sD1)



# lBrandInfo = [{'industry':'xiaomi', 'brandsinfo' : {'小米' : '小米手机很好用'}, 'classifier' : 'xiaomi'}, {'industry':'car', 'brandsinfo' : {'奔驰' : '开着奔驰上高速', '大众':'大众汽车新闻发布会'}, 'classifier' : 'car'} ]
