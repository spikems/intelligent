#encoding:utf8
#!/usr/bin/env python
from peewee import (Model, IntegerField, CharField, DateTimeField, TextField, PrimaryKeyField, ForeignKeyField, DateField, FloatField, BigIntegerField)
from peewee import MySQLDatabase
from modelbase import ModelBase 
import sys

class CogDupword(ModelBase):

    def __init__(self):
        self.dbname='cognitive_phrases'
        super(CogDupword,self).__init__(self.dbname)
        self.table = 'dupword'


    def addWord(self, sBrand = '', sDeterminer = ''):
     
        '''
             add brand
 
        '''
    
        sSql = "insert into %s(word, species) VALUES ('%s', '%s')" % (self.table, sBrand, sDeterminer)
        bRet = super(CogDupword,self).operate(sSql)
        return bRet

    def queryAll(self):
        
        '''
             query all brands

        '''

        sSql = 'select * from %s' % self.table
        lRet = super(CogDupword,self).query(sSql)
        return lRet


    def queryWord(self, sIndustry = ''):

        '''
             query brand by brandsname
 
        '''

        sSql = "select word from %s where  species = %s" % (self.table, sIndustry)
        lRet = super(CogDupword,self).query(sSql)
        return lRet

    def updateBrands(self, sBrand = '', sDeterminer = '', sFdeter = '', sIndustry = ''):

        '''
             update brand by brandsname

        '''

        sSql = "update %s set determiner = '%s', fdeterminer = '%s' where brands_name = '%s' and industry = %s" % (self.table, sDeterminer, sFdeter, sBrand, sIndustry)
        bRet = super(CogDupword,self).operate(sSql)
        return bRet

    def deleteBrands(self, sBrand = '', sDeterminer = '', sFdeter = ''):
        pass
if __name__ == '__main__':
    print CogDupword().queryAll()


#TBrands().addBrands(sBrand, sDeterminer, sFdeter, iSource, )
#print TBrands().addBrands('惠氏', '奶粉', '家族')
#print TBrands().updateBrands(sBrand = '美赞臣', sDeterminer = '奶粉#婴儿#母婴', sIndustry = '4')
#print TBrands().queryBrands(sBrand = '美赞臣', sIndustry = '4')
#for record in lRes:
#    print record['determiner'], "\t", record['fdeterminer']
#print ModelBase().operate("insert into brands(brands_name, positive_limit, reverse_limit, is_noise, remain2, remain1) values('b','a','a','a','a',1)")
#print ModelBase().operate("update brands set brands_name='c' where brands_name='b'")
#if len(self.queryBrands(sBrand)) == 0:
