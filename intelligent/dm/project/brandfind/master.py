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
import json
from intelligent.dm.project.brandfind.brandfind import BrandFindServer


def predict(jParam, bFindHardBrand=False):
    '''
       predict serivce 
    '''

    lParams = json.loads(jParam)
    return BrandFindServer().run(lParams, bFindHardBrand)
