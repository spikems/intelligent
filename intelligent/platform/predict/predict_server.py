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
#sys.path.insert(0, "/home/liuhongyu/intelligent/")
from intelligent.platform.predict.server_conf import *
from intelligent.common.exldeal import XLSDeal
from intelligent.common.util import _utf_string
from intelligent.common.util import isContain


DATA_MIXING_ENABLED = False
BRANDFIND_SERVER_PREFIX = 'brandfind'

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

    def getServers(self):

        return c_servers.keys() 

    
    def __start(self, project, cache):

        sJs = json.dumps(cache)
        sImport = "intelligent.dm.project.%s.master" % project
        stringmodule = __import__(sImport, fromlist=["*"])
        if project.startswith(BRANDFIND_SERVER_PREFIX):
            sResult = stringmodule.predict(sJs, True)
        else:
            sResult = stringmodule.predict(sJs)
        return sResult


    def predict(self, projectname = '', brands = '', input = '', output = ''):

        '''
            inputs:
               projectname : project name
               brands : brands name under project 
               input : input file path, the first three columns must be id, title, abstract 
               output : output file path

            res:
                predict result: True success or False Failure

        '''

        if projectname == '' or input == '' or output == '':
            self.logger.error("parameter error !!!")
            return False
 
        lProjectinfo = c_servers[projectname.strip()].split('_')
        sProject = lProjectinfo[0]
        sIndustryno = lProjectinfo[1] if len(lProjectinfo) > 1 else ''
 
        try:
            #dump xls to txt
            lLines = XLSDeal().XlsToList(input)
        except:
            self.logger.error("Raise exception: \n%s\n" % (traceback.format_exc()))

        lText = []
        for sLine in lLines:
            sLine = sLine.strip()
            fs = sLine.split('\t')
            if sLine == '' or len(fs) < 3:
                continue
    
            sId = fs[0]
            sTitle = fs[1].replace(' ', '')
            sDocument = fs[2].replace(' ', '')
            
            dParam = {'id' : sId, 'title' : sTitle, 'document' : sDocument}

            #require more information project deal
            if sProject in c_more_project:
                dParam['other'] = fs[3].strip()

            if sIndustryno != '':
                dParam['industry'] = sIndustryno

            try:
                jRes = self.__start(sProject, [dParam])
                lRes = json.loads(jRes)
                dItem = lRes[0]
                if 'prob' in dItem:
                    sOut = '%s\t%s\t%s' % (c_labels[projectname][dItem['type']], _utf_string(dItem['prob']), sLine)
                elif 'nothit' in dItem and brands.strip() != '':
                    brand = brands.strip().decode('utf-8')
                    if brand in dItem['nothit']:
                        hothitprob = 1 - float(dItem['nothit'][brand])
                        sOut = '%s\t%s\t%s' % (c_labels[projectname][dItem['type']], _utf_string(str(hothitprob)), sLine)
                    elif 'result' in dItem:
                        prob = 0.5
                        for industry in dItem['result']:
                            for rec in dItem['result'][industry]:
                                if brand in rec:
                                    prob = rec[brand]
                                    break
                        sOut = '%s\t%s\t%s' % (c_labels[projectname][dItem['type']], _utf_string(prob), sLine)
                else:
                    sOut = '%s\t%s' % (c_labels[projectname][dItem['type']], sLine)
                
                if brands.strip() != '' :
                    bSpecific = False
                    for brand in brands.split('#'):
                        if isContain(sOut.replace(' ', ''), brand):
                            bSpecific = True
                            break
                    if bSpecific:
                        lText.append(sOut.strip())
                else:
                    lText.append(sOut.strip())

            except:
                self.logger.error("Raise exception: \n%s\nWith data: \n%s" % (traceback.format_exc(), sLine))
  
        try:              
            XLSDeal().toXlsFile(lText, output)
        except:
            self.logger.error("Raise exception: \n%s\n" % (traceback.format_exc()))
        return True

if __name__ == '__main__':
    usage = 'python predict_server.py  --projectname <projectname> --brands <brands> --input  <input> --output <output> '
    parser = OptionParser(usage)
    parser.add_option("--projectname", dest="projectname")
    parser.add_option("--brands", dest="brands")
    parser.add_option("--input", dest="input")
    parser.add_option("--output", dest="output")

    opt, args = parser.parse_args()
    sProjectname = '' if  opt.projectname is None else opt.projectname
    sBrands = '' if opt.brands is None else opt.brands
    sInput = '' if opt.input is None else opt.input
    sOutput =  '' if opt.output is None else opt.output

    PredictServer().predict(
            projectname = sProjectname, 
            brands = sBrands,
            input = sInput, 
            output = sOutput
    )

    
    #print Strategy().getServers()

   
