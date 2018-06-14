#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
    A Classifier Project For mzcziran
    1. paramter check
    2. judge if is brand or not , and select dm or return sorry
    3. preprocess
    4. predict
    5. return result
'''

import json
from intelligent.dm.project.mzcziran.mzcziran import MZCZiranServer


def predict(jParam):

    '''
       predict serivce 
    '''

    lParams = json.loads(jParam)
    return MZCZiranServer().run(lParams)

