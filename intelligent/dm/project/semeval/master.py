#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
    A Classifier Project For semeval
    1. paramter check
    2. judge if is brand or not , and select dm or return sorry
    3. preprocess
    4. predict
    5. return result
'''

import json
import msgpack
from intelligent.dm.project.semeval.semeval import SemevalServer
import logging
import traceback
import chardet


def predict(jParam):
    '''
       predict serivce 
    '''

    try:
        sParam = jParam.encode('ISO-8859-2', 'ignore')
        lParams = msgpack.unpackb(sParam)
    except:
        logger = logging.getLogger("error.log")
        sError = "   traceback: %s" % (traceback.format_exc())
        logger.error(sError)
    lDocsRet = SemevalServer().run(lParams)
    jResult = msgpack.packb(lDocsRet).decode('ISO-8859-2')
    return jResult


if __name__ == '__main__':
    sId = '1'
    sTitle = '汽车 召回'
    sDocument = '汽车 召回'
    sIndustry = '2'
    sType = 'weibo'
    sBrand = 'car'
    sTest = [{"id": sId, "title": sTitle, "document": sDocument, 'industry': sIndustry, 'type': sType, 'brand': sBrand}]
    sJs = msgpack.packb(sTest)
    ret = predict(sJs)
    print msgpack.unpackb(ret)
