#encode:utf-8
'''
    common function to dm project

'''


def singleton(cls, *args, **kw):
    instances = {}
    def _singleton():
        if cls not in instances:
            instances[cls] = cls(*args, **kw)
        return instances[cls]
    return _singleton


def strim(sText) :
    return sText.encode('utf-8').replace("\n", '').strip()

def trim(sText) :
    return sText.encode('utf-8').replace("\n", '').replace(' ', '').strip()

def trim_plus(sText) :
    return sText.replace("\n", '').replace(' ', '').strip()

def isContain(s, substr):
    if s.find(substr) == -1:
        return False
    return True

def _utf_string(s):
    if isinstance(s, unicode):
        return s.encode("utf-8", "ignore")
    return str(s)

def unicode_string(ss):
    if isinstance(ss,unicode):
	return ss
    else:
	return ss.decode('utf-8','ignore')                

def list_index(lis, elem):

    for index,item in enumerate(lis):
        if item == elem:
            return index

    return -1  

def lowerDBData(lDBInfo):
    lRetInfo = []
    for item in lDBInfo:
        dTmp = {}
        for key in item:
            if type(item[key]) == str:
                item[key] = item[key].lower()
            dTmp[key] = item[key]
        lRetInfo.append(dTmp)
    return lRetInfo

def list2Dict(srcList):
    srcDict = {}
    for item in srcList:
        srcDict[item] = 1
    return srcDict
