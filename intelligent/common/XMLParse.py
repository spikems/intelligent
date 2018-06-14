#coding=utf-8
import xml.etree.ElementTree as ET

class XMLParse:

    '''
         xml parse task:
         parse all the server project
         1. configure server.xml item to add server
         2. add global server function 
         
         note:
         global server functon must be the same with server name in server.xml
  
    '''

    def __init__(self):
        pass
    
    def parsexml(self, serverXmlPath):
        
        tree = ET.ElementTree(file = serverXmlPath)
        self.dXml = {}
        
        for elem in tree.iter(tag='server'):
            serverf = elem.attrib['name']
            self.dXml[serverf] = eval(serverf)(elem)
        return self.dXml
            

def brandfind(elem):
    '''

      brandfind server analyse
      ret: server configure

    '''

    dServerConf = {}
    for item in elem:
        if item.tag == 'models':
            dServerConf['industry'] = [0] * (len(item) + 1)
            dServerConf['industry_model'] = {}
            dServerConf['model'] = []
            for model in item:
                fs = model.text.split('#')
                dServerConf['model'].append(fs[0])
                dServerConf['industry'][int(fs[2])] = fs[1]
                dServerConf['industry_model'][fs[1]] = fs[0]
        else:
            dServerConf[item.tag] = item.text
    return dServerConf
 

def intention(elem):

    '''

      intention server analyse
      ret: server configure

    '''

    dServerConf = {}
    for item in elem:
        if item.tag == 'models':
            dServerConf['model'] = []
            if item.tag == 'models':
                 for model in item:
                     dServerConf['model'].append(model.text)
        else:
            dServerConf[item.tag] = item.text
 
    return dServerConf

#XMLParse().parsexml('project.xml')
