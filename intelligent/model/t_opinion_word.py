#encoding:utf8
#!/usr/bin/env python
from peewee import (Model, IntegerField, CharField, DateTimeField, TextField, PrimaryKeyField, ForeignKeyField, DateField, FloatField, BigIntegerField)
from peewee import MySQLDatabase
from modelbase import ModelBase 
import sys

class TOpinionWord(ModelBase):

    def __init__(self):
 
        super(TOpinionWord, self).__init__()
        self.table = 'opinion_word'

    def queryAll(self):
        
        '''
             query all brands

        '''

        sSql = 'select * from %s' % self.table
        lRet = super(TOpinionWord, self).query(sSql)
        return lRet


if __name__ == '__main__':
    print TOpinionWord().queryAll()














