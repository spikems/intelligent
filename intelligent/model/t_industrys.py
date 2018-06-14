#encoding:utf8
#!/usr/bin/env python
from peewee import (Model, IntegerField, CharField, DateTimeField, TextField, PrimaryKeyField, ForeignKeyField, DateField, FloatField, BigIntegerField)
from peewee import MySQLDatabase
from modelbase import ModelBase 

class TIndustrys(ModelBase):

    def __init__(self):
 
        super(TIndustrys,self).__init__()
        self.table = 'industrys'


    def addIndustrys(self, sIndustry = '', sDeterminer = '', sFdeter = ''):
     
        '''
             add industry
 
        '''
    
        sSql = "insert into %s(industry_name, determiner, fdeterminer) VALUES ('%s', '%s', '%s')" % (self.table, sIndustry, sDeterminer, sFdeter)
        bRet = super(TIndustrys, self).operate(sSql)      
        return bRet

    def queryAll(self):
        
        '''
             query all industrys

        '''

        sSql = 'select * from %s' % self.table
        lRet = super(TIndustrys, self).query(sSql)
        return lRet


    def queryIndustrys(self, sIndustry = ''):

        '''
             query industry by industrysname
 
        '''

        sSql = "select * from %s where industry_name = '%s'" % (self.table, sIndustry)
        lRet = super(TIndustrys,self).query(sSql)
        return lRet

    def updateIndustrys(self, sIndustry = '', sDeterminer = '', sFdeter = ''):

        '''
             update industry by industrysname

        '''

        sSql = "update %s set determiner = '%s', fdeterminer = '%s' where industry_name = '%s'" % (self.table, sDeterminer, sFdeter, sIndustry)
        print sSql
        bRet = super(TIndustrys,self).operate(sSql)
        return bRet

    def deleteIndustrys(self, sIndustry = '', sDeterminer = '', sFdeter = ''):
        pass        

#print TIndustrys().addIndustrys('母婴', '奶粉', '家族')
#print TIndustrys().updateIndustrys(sIndustry = '母婴', sDeterminer = '奶粉#婴儿')
lRes = ModelBase().query('select * from industrys')
#for record in lRes:
#    print record['determiner'], "\t", record['fdeterminer']
#print ModelBase().operate("insert into industrys(industrys_name, positive_limit, reverse_limit, is_noise, remain2, remain1) values('b','a','a','a','a',1)")
#print ModelBase().operate("update industrys set industrys_name='c' where industrys_name='b'")
#if len(self.queryIndustrys(sIndustry)) == 0:
