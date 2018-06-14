#encoding:utf8
#!/usr/bin/env python
from peewee import (Model, IntegerField, CharField, DateTimeField, TextField, PrimaryKeyField, ForeignKeyField, DateField, FloatField, BigIntegerField)
from peewee import MySQLDatabase
from modelbase import ModelBase 
import sys

class TBrandDetail(ModelBase):

    def __init__(self):
 
        super(TBrandDetail,self).__init__()
        self.table = 'brands_detail'

    def queryAll(self):
        
        '''
             query all brands

        '''

        sSql = 'select * from %s' % self.table
        lRet = super(TBrandDetail,self).query(sSql)
        return lRet


if __name__ == '__main__':
    print TBrandDetail().queryAll()














