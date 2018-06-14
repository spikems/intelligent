#encoding:utf8
#!/usr/bin/env python
from peewee import (Model, IntegerField, CharField, DateTimeField, TextField, PrimaryKeyField, ForeignKeyField, DateField, FloatField, BigIntegerField)
from peewee import MySQLDatabase
from modelbase import ModelBase 
import logging
import sys

SERVER = 'server'
LOGTYPE = 'logtype'
INDUSTRY = 'industry'
LINK = 'link'
TARGET = 'target'
SOURCE = 'source'
TILTE = 'title'
ABSTRACT = 'abstract'
CONTEXT = 'context'
REASON = 'reason'
PREDTYPE = 'predtype'
PREDPROB = 'predprob'
PREDALL = 'predall'
RETAIN = 'retain'

class TIntelligentLog(ModelBase):

    def __init__(self):
 
        super(TIntelligentLog, self).__init__()
        self.table = 'intelligent_log'

    def queryAll(self):
        
        '''
             query all brands

        '''

        sSql = 'select * from %s' % self.table
        lRet = super(TIntelligentLog, self).query(sSql)
        return lRet

    def query_by_entryidurl(self, entryid, url):
        url = url.replace('%', '').replace('\'', '').replace('"', '')
        sSql = "select reason, abstract from %s where logtype = 'product' and link = '%s' and retain = '%s'" % (self.table, url, entryid)
        print sSql
        lRet = super(TIntelligentLog, self).query(sSql)
        return lRet

    def queryby_url_target(self, url, target):
        url = url.replace('%', '').replace('\'', '').replace('"', '')
        target = target.replace('%', '').replace('\'', '').replace('"', '')
        sSql = "select logtype,link,target,source,title,abstract,reason,predtype,predprob,predall,create_Time from %s where link = '%s' and target = '%s'" % (self.table, url, target)
        lRet = super(TIntelligentLog, self).query(sSql)
        return lRet

    def queryby_url(self, url):
        sSql = "select logtype,link,target,source,title,abstract, reason,predtype,predprob,predall,create_Time from %s where link = '%s'" % (self.table, url)
        lRet = super(TIntelligentLog, self).query(sSql)
        return lRet

    def insertone(self, dRecord = {}):
        '''
             insert one record        

        '''
        dRecord1 = {
            SERVER : '',
            LOGTYPE : '',
            INDUSTRY : '-1',
            LINK : '',
            TARGET : '',
            SOURCE : '',
            TILTE : '',
            ABSTRACT : '',
            CONTEXT : '',
            REASON : '',
            PREDTYPE : '',
            PREDPROB : '',
            PREDALL : '',
            RETAIN : ''
        }
        for field in dRecord:
            dRecord1[field] = dRecord[field].replace('%', '').replace('\'', '').replace('"', '')

        fields = (",").join(dRecord1.keys())
        vals = "'%s'" % ("','").join(dRecord1.values())
        sSql = "insert into %s(%s) values (%s);" % (self.table,fields,vals)
        super(TIntelligentLog, self).operate(sSql)

if __name__ == '__main__':
    dR = {'server' : 'product'}
    print TIntelligentLog().insertone(dRecord = dR)














