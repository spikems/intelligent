#coding:utf-8
import sys
#sys.path.append('/home/liuhongyu/intelligent')
#from  intelligent.platform.hotword.phrase_recon import PhraseReconize
from collections import Counter
import heapq

class  DataStatistic(object):
    def __init__(self,ddata,attr_num,word_num):
        self.ddata =ddata
        self.attr_num =attr_num
        self.top_num = int(word_num)

    def idf_count(self,ldata):
        cdata = Counter(ldata)
        sdata = heapq.nlargest(self.top_num,cdata.items(),key=lambda x:x[1])
        return sdata

    def attri_count(self):
        attri_result = heapq.nlargest(self.attr_num,self.ddata.items(),key=lambda x:len(x[1]))
        return  attri_result

    def idf2_count(self,ldata):
        cdata = Counter(ldata)
        sdata = heapq.nlargest(20,cdata.items(),key=lambda x:x[1])
        return sdata

    def run(self):
        attr_ressult = self.attri_count()
        fina_result = {}
        lgroup=[]
        # outfile = open('count_keword.txt','wb')
        for attword,group in self.ddata.items():
            # outfile.write('%s\t%s\n'%(attword,' '.join(group)))
            lgroup.extend(group)
        print 'all semeval word num:%s'%len(lgroup)
        relgroup = self.idf2_count(lgroup)
        for key ,word in attr_ressult:
            result = self.idf_count(word)
            fina_result[(key,len(self.ddata[key]))]=result
        # outfile.close()
        return fina_result,relgroup

if __name__ == "__main__":
    ddata ={1: [1,2,3,4,1,1],2:[2,1,3,4,2]}
    ins =DataStatistic(ddata=ddata , attr_num=2, word_num=2)
    fina_result = ins.run()
    for attword,wordphrase in fina_result.items():
        att,attnum =attword
        print att ,attnum
        for opinion in wordphrase:
            word,num=opinion
            print word,num

    # for w_n in fina_group:
    #     w,n = w_n
    #     print w,n






