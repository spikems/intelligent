#encoding:utf8
#!/usr/bin/env python
from peewee import (Model, IntegerField, CharField, DateTimeField, TextField, PrimaryKeyField, ForeignKeyField, DateField, FloatField, BigIntegerField)
from peewee import MySQLDatabase
from modelbase import ModelBase 
import sys

STOPWORD = '1'
GENERALWORD = '0'

class TGeneralWord(ModelBase):

    def __init__(self):
 
        super(TGeneralWord, self).__init__()
        self.table = 'general_word'
    
    def queryAll(self, stopword = True):
        
        '''
             query all general word

        '''
        source = GENERALWORD
        if stopword:
            source = '%s, %s' % (STOPWORD, GENERALWORD)
            
        sSql = 'select * from %s where source in (%s)' % (self.table, source)
        lRet = super(TGeneralWord, self).query(sSql)
        return lRet



#ret = TGeneralWord().queryAll(stopword =  False)
#print ret[0], len(ret)
