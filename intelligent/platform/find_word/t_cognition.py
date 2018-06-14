#!/usr/bin/env python
#-*- coding:utf-8 -*-
import sys
import logging
import traceback
reload(sys)
sys.setdefaultencoding('utf-8')
from intelligent.model.t_cog_category import CogCategory
from intelligent.model.t_cog_attribute import CogAttribute
from intelligent.model.t_cog_brands import CogBrand
from intelligent.model.t_cog_dupword import CogDupword
# from intelligent.model.t_cog_evalue import CogEvalue

class mysqls(object):

    def __init__(self,):
        self.read_category = CogCategory()
        self.read_attr = CogAttribute()
        self.read_brand = CogBrand()
        self.dupword = CogDupword()
        # self.read_evalue=CogEvalue()

    def insert(self,industy_id,lword):
        for w in lword:
            word=w.strip()
            self.dupword.addWord(word,int(industy_id))

    def run(self,industry_id):
        sysn_dict = {}  # word===>sysnon
        attword = []
        dupword = []  #duplicated word 
        # opinionword = []
        for group in self.dupword.queryWord(int(industry_id)):
            dupword.append(group['word'].encode('utf-8','ignore'))

        for wgroup  in self.read_category.queryAll():
            if wgroup['industry']==int(industry_id):
                attword.append(wgroup['category'])
                for w in wgroup['synonyms'].decode('utf-8').split('|'):
                    if w:
                        sysn_dict[w.encode('utf-8')]=wgroup['category']

        for group in self.read_attr.queryAll():
            if group['industry_id'] in [0,int(industry_id)]:
                attword.append(group['word'])
                if group['synonyms']:
                    for w in group['synonyms'].decode('utf-8').split('|'):
                        sysn_dict[w.encode('utf-8')]=group['word']

        for brand in self.read_brand.queryAll():
            if brand['industry']==industry_id:
                attword.append(brand['brand_name'].strip())

        # for group in json.loads(self.read_evalue):
        #     if group['industry_id'] in ['0',industry_id]:
        #         opinionword.append(group['evaluation'])
        #     if group['sysnonyms'] :
        #         for w in group['sysnonyms'].split('|'):
        #             sysn_dict[w]=group['evaluation']
        return attword,sysn_dict,dupword

if __name__ == "__main__":
    ins = mysqls()
    # sql = 'select brands_name from brands where industry ;'
    attword, sysn =ins.run(1)
    print attword[:2]
    print sysn.items()[:2]
    # for i,j in result.items():
    #     print i,j
