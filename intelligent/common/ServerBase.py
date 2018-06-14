#encoding:utf-8
from XMLParse import XMLParse
from intelligent.dm.learn.learner import Learner
import logging
import traceback
import os

class ServerBase(object):

    def __init__(self):

        self.sBaseDir = "/home/liuhongyu/intelligent/intelligent/dm/project/"
        self.errLogger = logging.getLogger("errinfo")
        self.logger = logging.getLogger("intelligent")
        self.sServersConf = XMLParse().parsexml(self.sBaseDir + "conf/project.xml")
        self.predictors = {}
        
    def init_server(self):
        self.loadModel('*')


    def loadModel(self, sServerName = '*'):
        print "enter"
        
        for sServer in self.sServersConf:
            if sServerName == '*' or sServer == sServerName:
                dServerConf = self.sServersConf[sServer]
                sModelPath = '%s%s' % (self.sBaseDir, dServerConf['modelpath'])
                print sModelPath 
                print dServerConf

                try:
                    lFiles =  os.listdir(sModelPath)
                    print lFiles
                    for sfile in lFiles:
                        sfilename = sfile[:-4]
                        if not sfile.find('pkl') == -1 and sfilename in dServerConf['model']:
                            predictor = Learner(train = False)
                            predictor.load_model(sModelPath + "/" + sfilename)
                            if not sServer in self.predictors:
                                self.predictors[sServer] = {}
                            self.predictors[sServer][sfilename] = predictor

                            #record log
                            print sModelPath + "/" + sfilename
                            self.logger.info("%s load model %s" % (sServer, sfilename))
                except:
                    sError = "%s load model file error.  traceback: %s" % (sServer, traceback.format_exc())
                    self.errLogger.error(sError)



#ServerBase().init_server()
