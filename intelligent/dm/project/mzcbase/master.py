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
from intelligent.dm.project.mzcbase.mzcbase import MZCBaseServer


def predict(jParam):

    '''
       predict serivce 
    '''

    lParams = json.loads(jParam)
    return MZCBaseServer().run(lParams)

