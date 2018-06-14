#coding:utf-8
import sys,os
import logging
from intelligent.platform.hotword.count_kword import DataStatistic
from intelligent.platform.hotword.make_sent import MakeSentence
from intelligent.platform.hotword.es_query import es_query
from intelligent.platform.hotword.parse_recon import PhraseReconize
from intelligent.common.exldeal import XLSDeal


def semevalword(moniterword,industry,attr_num,infile =False,is_marketing=True,is_dup=True,is_es=False,is_sitename=False,day=90):
    logging.info( 'Punctuation')

    if not is_es:
        raw_data = XLSDeal().XlsToList(infile)
    elif is_es:
        raw_data = es_query(moniterword,day)        
      
    sen_ins = MakeSentence(raw_data=raw_data,is_marketing=is_marketing,is_dup=is_dup)
    logging.info('find words')
    Dsents = sen_ins.extract_sentence()
    logging.info(moniterword)
    word_ins = PhraseReconize(moniter_word=moniterword , Dsent=Dsents,industry_id = industry)
    ddata,outlist = word_ins.prepare()
   #XLSDeal().toXlsFile(outlist, 'result_%s'%infile)
    count_ins = DataStatistic(ddata=ddata , attr_num=attr_num+1, word_num=1)
    result,regroup = count_ins.run()
    sort_result = []
    for attrword, group in result.items():
         attr, attnum = attrword
         sort_result.append(group[0])
    iresult = sorted(sort_result,key=lambda x: x[1],reverse=True)
    dealresult = []
    for word in iresult:
        words = word[0].split('：')
        if len(words) == 2:
           dealresult.append((words[1],word[1]))
         
    return dealresult


if __name__ == '__main__':

    logger = logging.getLogger(__name__)

    program = os.path.basename(sys.argv[0])
    logger = logging.getLogger(program)
    # logging configure
    import logging.config
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s')
    logging.root.setLevel(level=logging.INFO)

    moniterword = '哈弗H6'
    infile = sys.argv[1]
    attr_num = 10
    word_num = 1
    result = semevalword(moniterword = moniterword,industry = 2,attr_num = attr_num,is_es = True,is_marketing=False,day = 30)
    for group in result:
        word, num = group
        print word,num
    print '==================================='



