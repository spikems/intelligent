#encoding:utf8
#!/usr/bin/env python
from peewee import (Model, IntegerField, CharField, DateTimeField, TextField, PrimaryKeyField, ForeignKeyField, DateField, FloatField, BigIntegerField)
from peewee import MySQLDatabase
from modelbase import ModelBase 
import sys

class TIndustryDetail(ModelBase):

    def __init__(self):
 
        super(TIndustryDetail,self).__init__()
        self.table = 'industrys_detail'


 
    def queryAllToMap(self):
        
        '''
             query all industrys

        '''

        dRet = {}
        sSql = 'select * from %s' % self.table
        lRet = super(TIndustryDetail,self).query(sSql)
        for item in lRet:
            dRet[item['id']] = item
        return dRet

#print TIndustryDetail().queryAllToMap()
