# -*- coding: utf-8 -*-

import json
import logging
import traceback
import sys
import requests
import logging.config
from optparse import OptionParser
sys.path.insert(0, "/home/zzg/liuhongyu/anaconda2/lib/python2.7/site-packages/intelligent")
sys.path.insert(1, "/home/zzg/liuhongyu/anaconda2/lib/python2.7/site-packages")
sys.path.insert(2, "/home/zzg/liuhongyu/anaconda2/lib/python2.7/site-packages/xgboost-0.6-py2.7.egg")
#sys.path.insert(0, "/home/liuhongyu/intelligent/")
from intelligent.platform.semeval.server_conf import *
from intelligent.common.exldeal import XLSDeal
from intelligent.common.util import _utf_string
from intelligent.common.util import isContain
import msgpack
import chardet
from intelligent.model.t_feature_word import TFeatureWord
import jieba
from jieba.norm import norm_cut, norm_seg

DATA_MIXING_ENABLED = False

# logging configure
class PredictServer:

    '''
            platform predict service 

    '''

    def __init__(self):

        
        self.sLogPath = '%s/../../../logs/platform.error' % (os.path.dirname(os.path.realpath(__file__)))
        self.servers = []
        logging.basicConfig(format='%(asctime)s : %(filename)s[line:%(lineno)d] : %(message)s', filename = self.sLogPath)
        logging.root.setLevel(level=logging.ERROR)
        self.logger = logging.getLogger(__name__)
        self.TFW = TFeatureWord()
        self.__loadFeature()

    def __loadFeature(self):
        fw = open('features', 'w')
        lRet = self.TFW.queryAll() 
        dSyntax = {}
        dAppear = {}
        for record in lRet:
            name = '%s 100000 n\n' % record['name'].lower().replace(' ', '')
            if name in dAppear:
                continue
            dAppear[name] = 1
            fw.write(name)
        fw.close()
        jieba.load_userdict('features')

    def getServers(self):

        return c_industrys.keys() 

    
    def __start(self, project, cache):

        sImport = "intelligent.dm.project.%s.semeval" % project
        stringmodule = __import__(sImport, fromlist=["*"])
        lResult = stringmodule.SemevalServer().run(cache)
        return lResult

    def __cut(self, text):
        words = jieba.cut(text)
        result = []
        for it in words:
            word = it.encode('utf-8')
            result.append(word)
        return " ".join(result)
        
    def predict(self, industry = '', target = '', input = '', output = ''):

        '''
            inputs:
               industry : industry name
               input : input file path, the first three columns must be id, target, title, abstract 
               output : output file path

            res:
                predict result: True success or False Failure

        '''

        if industry == '' or input == '' or output == '':
            self.logger.error("parameter error !!!")
            return False
 
        sIndustryNo = c_industrys[industry.strip()]
        sProject = 'semeval'
 
        try:
            #dump xls to txt
            lLines = XLSDeal().XlsToList(input)
        except:
            self.logger.error("Raise exception: \n%s\n" % (traceback.format_exc()))

        lText = []
        for sLine in lLines:
            sLine = sLine.strip()
            fs = sLine.split('\t')
            if sLine == '' or len(fs) < 5:
                continue
    
            sId = fs[0]
            sTarget = fs[1].replace(' ', '').strip()
            sTitle = self.__cut(fs[2].replace(' ', '').strip())
            sDocument = self.__cut(fs[3].replace(' ', '').strip())
            sLink = fs[4].replace(' ', '').strip()

            
            
            dParam = {'id' : sId, 'title' : sTitle, 'document' : sDocument,  "type" : "weibo", "brand" : sTarget, "industry" : sIndustryNo, 'link' : sLink}

            #require more information project deal
            try:
                lRes = self.__start(sProject, [dParam])
                dItem = lRes[0]
                if 'prob' in dItem:
                    sOut = '%s\t%s\t%s' % (c_labels[dItem['type']], _utf_string(dItem['prob']), sLine)
                else:
                    sOut = '%s\t%s' % (c_labels[projectname][dItem['type']], sLine)
                
                lText.append(sOut.strip())

            except:
                self.logger.error("Raise exception: \n%s\nWith data: \n%s" % (traceback.format_exc(), sLine))
  
        try:              
            XLSDeal().toXlsFile(lText, output)
        except:
            self.logger.error("Raise exception: \n%s\n" % (traceback.format_exc()))
        return True

if __name__ == '__main__':
    usage = 'python predict_server.py  --industryname <industryname> --input  <input> --output <output> '
    parser = OptionParser(usage)
    parser.add_option("--industryname", dest="industryname")
    parser.add_option("--input", dest="input")
    parser.add_option("--output", dest="output")

    opt, args = parser.parse_args()
    sIndustry = '' if  opt.industryname is None else opt.industryname
    sInput = '' if opt.input is None else opt.input
    sOutput =  '' if opt.output is None else opt.output

    PredictServer().predict(
            industry = sIndustry, 
            input = sInput, 
            output = sOutput
    )

    
    #print Strategy().getServers()

   
