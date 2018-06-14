#coding:utf-8
from intelligent.platform.hotword.M_sql import mysqls
import logging
import os,sys

class PrepareForSql(object):
    def __init__(self,industry):
        # self.brand = brand.encode('utf-8','ignore').strip()
        self.industry = industry
        self.sysn_dict = {}  # word===>sysnon
        self.attword = set([])
        self.AP_phrase = set([])
        self.opinionword = set([])
        self.sql = mysqls()

    def deal_syn(self,v_word,syn_data):
        if not syn_data:
            return
        for syn in syn_data.decode('utf-8','ignore').split('|'):
            syn = syn.encode('utf-8', 'ignore').strip()
            valword = v_word.encode('utf-8', 'ignore').strip()
            self.sysn_dict[syn.upper()] = valword.upper()


    # def product(self,):
    #     result = self.sql.read_product(self.brand,self.industry)
    #     for sub in result:
    #         product = sub['product'].encode('utf-8','ignore').strip().upper()
    #         self.attword.add(product)
    #         self.deal_syn(sub['product'],sub['synonyms'])

    def component(self):
        result = self.sql.read_component(self.industry)
        for sub in result:
            component =  sub['component'].encode('utf-8','ignore').strip().upper()
            self.attword.add(component)

    def brands(self):
        # self.attword.add(self.brand)
        result = self.sql.read_brands(self.industry)
        for sub in result:
            self.deal_syn(sub['brand_name'],sub['synonyms'])

    def category(self,):
        result = self.sql.read_category(self.industry)
        for sub in result:
            cateword = sub['category'].encode('utf-8','ignore').strip().upper()
            self.attword.add(cateword)
            self.deal_syn(sub['category'], sub['synonyms'])

    def attr(self):
        result = self.sql.read_attr(self.industry)
        for sub in result:
            word = sub['word'].encode('utf-8','ignore').strip().upper()
            self.attword.add(word)
            self.deal_syn(sub['word'],sub['synonyms'])

    def evalue(self):
        result = self.sql.read_evalue(self.industry)
        for sub in result:
            word = sub['evaluation'].encode('utf-8', 'ignore').strip().upper()
            self.opinionword.add(word)
            self.deal_syn(sub['evaluation'], sub['synonyms'])

    def phrase(self):
        result =self.sql.read_phrase()
        for w in self.attword:
            for o in self.opinionword:
                wp = w +o
                self.AP_phrase.add(wp.strip())

        for sub in result:
            if sub['industry'] in ['0',str(self.industry)]:
                self.AP_phrase.add(sub['phrase'].encode('utf-8', 'ignore').strip() )
                self.attword.add(sub['att_word'].encode('utf-8', 'ignore').strip() )
                self.opinionword.add(sub['opinion_word'].encode('utf-8', 'ignore').strip())

    def syn(self):
        result = self.sql.read_syn()
        for sub in result:
            self.deal_syn(sub['key'],sub['value'])

    def run(self):
        # self.brands()
        self.category()
        self.attr()
        self.evalue()
        # self.product()
        self.component()
        # self.phrase()
        self.syn()
        logging.info('attword num :%s'%len(self.attword))
        logging.info('opinionword num :%s' % len(self.opinionword))
        logging.info('phrase num :%s' % len(self.AP_phrase))
        logging.info('synonword num :%s' % len(self.sysn_dict))

        self.attword = [ i.upper() for i in self.attword]
        self.opinionword = [i.upper() for i in self.opinionword]
        return self.attword,self.opinionword,self.sysn_dict

if __name__ == '__main__':
    program = os.path.basename(sys.argv[0])
    logger= logging.getLogger(program)
    logging.basicConfig(format='%(asctime)s,%(levelname)s,%(message)s')
    logger.setLevel(level=logging.INFO)
    logger.info('parse prepare is starting')
    brand = '兰蔻'
    industry = 1
    ins = PrepareForSql(brand,industry)
    attword ,opiword,phrase ,sysn_dict = ins.run()




