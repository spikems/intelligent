# coding:utf-8
import sys
import os
import json
import re
import jieba
reload(sys)
sys.setdefaultencoding('utf-8')
import logging
import datetime
from pyltp import Postagger
from pyltp import Parser
from pyltp import SentenceSplitter
from jieba.norm import norm_cut
from intelligent.platform.hotword.read_sql import mysqls
from intelligent.platform.hotword.meizhuang_prepare import PrepareForSql
from intelligent.platform.hotword.setting import *
dir_path = os.path.dirname(os.path.abspath(__file__))
jieba.load_userdict("%s/conf/jieba_lexicon" % dir_path)
LTP_DATA_DIR = '%s/ltp_data' % dir_path  # ltp模型目录的路径
pos_model_path = os.path.join(LTP_DATA_DIR, 'pos.model')  # 词性标注模型路径，模型名称为`pos.model`
par_model_path = os.path.join(LTP_DATA_DIR, 'parser.model')  # 依存句法分析模型路径，模型名称为`parser.model`
ins_mysql = mysqls()


class PhraseReconize(object):
    def __init__(self, moniter_word, Dsent, industry_id):
        self.moniter_word = moniter_word # 关键词
        self.Dsent = Dsent  # 原始数据
        self.industry = industry_id
        self.postagger = Postagger()  # 词性
        self.postagger.load_with_lexicon(pos_model_path, '%s/conf/posttags.txt' % dir_path)
        self.parser = Parser()  # 句法
        self.parser.load(par_model_path)  # 加载模型
        self.attribute, self.filter_word, self.sysn = PrepareForSql(industry_id).run()
        self.neg_word = c_neg_word  # 否定词
        self.adj_filter = c_adj_filter  # 不需要的形容词
        self.c_need_password = c_need_password  # 不需要的词
        self.ambigous_word= ins_mysql.ambiguous(self.moniter_word)
        self.c_no_meaningword = set(c_no_meaningword)  # 无意义的词
        self.evalue_sort = []  # ('省油','马自达'),('空间大','大众')

    def cut_word(self, sents):
        """
        分词
        """
        words = [i.encode('utf-8', 'ignore') for i in norm_cut(sents) if i not in self.c_need_password]  # HMM=False
        # 替换同义词
        num = 0
        for w in words:
            if w in self.sysn.keys():
                words[num] = self.sysn[w]
            num += 1
            # 寻找主语
        # if len(words) >= 1:
        #     if self.keyword and (words[0] in self.filter_word or words[0] in c_need_subject):
        #         if len(words) <= 4:
        #             words.insert(0, self.keyword)
        return words

    def word_sex(self, ):
        """
        获取词性
        """
        postags = list(self.postagger.postag(self.words))  # 词性标注
        return postags

    def parser_words(self, ):
        """
        输入：words:分词结果， postags:每个词的词性
        获取语法结构，其中arc.head是词的索引位置加一，arc.relation 是词语之间的关系
        """
        parser_dict = {}
        arcs = self.parser.parse(self.words, self.postags)  # 句法分析
        return arcs

    def deal_data(self, arcs):
        """
         输出：dword{'index1':[(relaindex1,relation),(relaindex2,relation)]}
               index1:词的索引，relaindex1:相关的索引 ，relation:两个词之间的关系，SBV等
        """
        dword = {}
        index = 0
        for arc in arcs:
            if arc.head == 0:
                rela_index = 0
            else:
                rela_index = arc.head - 1
            rela_word = self.words[rela_index]
            rela_postag = self.postags[rela_index]
            logging.debug('%s %s %s %s %s %s %s ' % (
                str(self.words[index]), str(self.postags[index]), str(index), str(rela_word), str(rela_postag),
                str(rela_index), str(arc.relation)))
            # 注意点：要相互的信息，不能只取其中一个,(大众，是):SBV
            if '%s_%s' % (index, arc.relation) not in dword.keys():
                dword['%s_%s' % (index, arc.relation)] = []
            dword['%s_%s' % (index, arc.relation)].append(rela_index)
            if '%s_%s' % (rela_index, arc.relation) not in dword.keys():
                dword['%s_%s' % (rela_index, arc.relation)] = []
            dword['%s_%s' % (rela_index, arc.relation)].append(index)
            index += 1
        return dword

    def dadv_deal(self, adjindex):
        kindex = '%s_ADV' % (adjindex)
        if kindex in self.dword.keys():
            for advindex in self.dword[kindex]:
                if adjindex in self.dword['%s_ADV' % advindex]:
                    self.dword['%s_ADV' % advindex].remove(adjindex)
                if self.words[advindex] in self.neg_word:
                    self.index_word.add(advindex)
                    return True
        return False

    def adj_deal(self, adjindex):
        try:
            if (self.postags[adjindex] in ['a'] \
                        or self.words[adjindex] in self.filter_word) and self.words[adjindex] not in self.adj_filter:
                if adjindex - 1 >= 0:
                    if self.postags[adjindex - 1] in ['n'] and int(adjindex - 1) not in self.index_word:
                        return False
                self.index_word.add(adjindex)
                # self.coo_deal(adjindex)
                return True
        except:
            logging.error('sent:%s,adjindex:%s' % (''.join(self.words), adjindex))
            return False
        return False

    def vob_deal(self, sbvindex):
        nkey = '%s_VOB' % sbvindex
        if nkey in self.dword.keys():
            for nindex in self.dword[nkey]:
                if sbvindex in self.dword['%s_VOB' % nindex]:
                    self.dword['%s_VOB' % nindex].remove(sbvindex)
                if self.adj_deal(nindex):
                    return True

                if self.words[nindex] in self.neg_word:
                    self.index_word.add(nindex)

                if self.cmp_deal(nindex):
                    return True
                if self.adv_deal(nindex):
                    return True
        return False

    def cmp_deal(self, sbvindex):
        nkey = '%s_CMP' % sbvindex
        if nkey in self.dword.keys():
            for nindex in self.dword[nkey]:
                if sbvindex in self.dword['%s_CMP' % nindex]:
                    self.dword['%s_CMP' % nindex].remove(sbvindex)
                if self.adj_deal(nindex):
                    # self.index_word.add(sbvindex)
                    return True
        return False

    def adv_deal(self, iniindex):
        nkey = '%s_ADV' % iniindex
        if nkey in self.dword.keys():
            for advindex in self.dword[nkey]:
                if iniindex in self.dword['%s_ADV' % advindex]:
                    self.dword['%s_ADV' % advindex].remove(iniindex)
                if self.adj_deal(advindex):
                    self.index_word.add(iniindex)
                    return True
        return False

    def vsbv_deal(self, iniindex):
        if self.postags[iniindex] in ['v']:
            if self.vob_deal(iniindex):
                return True
            if self.att_deal(iniindex):
                return True
            self.sbv_deal(iniindex)
            self.att_deal(iniindex)
        return False

    def sbv_deal(self, initindex):
        kindex = '%s_SBV' % initindex
        if kindex in self.dword.keys():
            for sbvindex in self.dword[kindex]:
                if initindex in self.dword['%s_SBV' % sbvindex]:
                    self.dword['%s_SBV' % sbvindex].remove(initindex)
                if self.adj_deal(sbvindex):
                    return True
                elif self.cmp_deal(sbvindex):
                    self.index_word.add(sbvindex)
                    return True
                elif self.vsbv_deal(sbvindex):
                    self.index_word.add(sbvindex)
                    return True
                elif self.adv_deal(sbvindex):
                    return True
        return False

    def coo_deal(self, relaindex):
        cooindex = '%s_COO' % relaindex
        if cooindex in self.dword.keys():
            for cooi in self.dword[cooindex]:
                return cooi
        return False

    def att_deal(self, attk):
        attindex = '%s_ATT' % attk
        if attindex in self.dword.keys():
            for att in self.dword[attindex]:
                if attk in self.dword['%s_ATT' % att]:
                    self.dword['%s_ATT' % att].remove(attk)
                if self.adj_deal(att) and att <= attk:
                    return True
                elif self.sbv_deal(att):
                    self.index_word.add(att)
                    return True
                elif self.vob_deal(att):
                    self.index_word.add(att)
                    return True
        return False

    def pob_deal(self, relaindex):
        pobmodel = '%s_POB' % relaindex
        if pobmodel in self.dword.keys():
            for pindex in self.dword[pobmodel]:
                if relaindex in self.dword['%s_POB' % pindex]:
                    self.dword['%s_POB' % pindex].remove(relaindex)
                if self.adv_deal(pindex):
                    self.index_word.add(pindex)
                    return True
        return False

    def deal_relation(self, index, relations, tag):
        for relation in relations:
            dwordkey = '%s_%s' % (index, relation)
            if dwordkey in self.dword.keys():
                for relaindex in self.dword[dwordkey]:
                    if self.postags[relaindex] in tag:
                        self.index_word.add(relaindex)
                        self.dword[dwordkey].remove(relaindex)
                        # if index in self.dword['%s_%s'%(relaindex,relation)]:
                        #     self.dword['%s_%s'%(relaindex,relation)].remove(index)
                        self.deal_relation(relaindex, relations, tag)

    def find_words(self, noun_key, is_main=True):
        # 找到所有形容词的关联
        if is_main:
            self.main_word = noun_key
        # tmpn =list(self.index_word)
        index = noun_key
        if noun_key + 1 < len(self.words):
            if self.adj_deal(noun_key + 1):
                self.index_word.add(self.main_word)
                return self.needword_deal(noun_key)
        if self.sbv_deal(index):  # [大众漏油 ,大众开着舒服]
            return self.needword_deal(noun_key)
        if self.att_deal(index):
            return self.needword_deal(noun_key)
        if self.vob_deal(index):
            return self.needword_deal(noun_key)
        if self.cmp_deal(index):
            return self.needword_deal(noun_key)
        if self.adv_deal(index):
            return self.needword_deal(noun_key)
        if self.pob_deal(index):
            return self.needword_deal(noun_key)

    def needword_deal(self, main_key):
        tmp_postag = [i for i in self.index_word if self.postags[i] in ['v', 'a', 'n']]
        for va_index in tmp_postag:
            self.dadv_deal(va_index)
            self.vob_deal(va_index)
        if len(self.index_word) > 1:
            tmp_index = sorted(self.index_word)
            posttag = [self.postags[i] for i in sorted(self.index_word)]
            if posttag[-1] in ['v', 'i'] and self.words[tmp_index[-1]] not in self.filter_word:
                logging.debug('word in v and not in dict')
                return
            words = [self.words[i] for i in sorted(self.index_word)]
            if words[0].encode('utf-8') in c_startword or words[-1].encode('utf-8') in c_endword:
                logging.debug('word in c_endword or c_startword')
                self.index_word = set()
                return
            if not set(posttag) & set(['a', ]) and not set(words) & set(self.filter_word):
                logging.debug('word not in adj and not in opinion_word')
                self.index_word = set()
                return
            # 将豪华宝马和宝马豪华转换成宝马豪华
            if len(words) == 2 and posttag == ['a', 'n']:
                word = words[1] + words[0]

            elif len(words) == 2 and posttag == ['n', 'n'] and words[1] == self.words[main_key]:
                word = words[1] + words[0]
            else:
                word = ''.join(
                    [self.words[i] for i in sorted(self.index_word) if self.words[i] not in c_need_removeword])

            if word.find(self.words[self.main_word]) == -1:
                logging.debug('main word not in phrase %s' % words)
                return
            if len(self.words[self.main_word].decode('utf-8', 'ignore')) <= 1:
                return
            self.startlocation = max(self.index_word)
            # 前面加一个主体名词
            if self.words[self.main_word] != self.keyword:

                evalue_sub = [word, self.keyword]
                self.evalue_sort.append(evalue_sub)
                word = self.keyword + '：' + word
            else:
                tmpword = word
                tmpword = tmpword.replace(self.keyword, '')
                evalue_sub = [tmpword, self.keyword]

            group = (self.words[self.main_word], word)
            self.need_words.add(group)

    def filter(self, ):
        # 过滤出我们想要的词
        self.need_words = set()
        self.startlocation = 0
        for key_index in range(len(self.words)):
            if key_index < self.startlocation:
                continue
            if self.words[key_index] in self.ambigous_word:
                self.keyword = ''
            if self.words[key_index] == self.moniter_word:
                self.keyword = self.words[key_index]
            if self.keyword:
                if (self.words[key_index] == self.moniter_word ) or (self.words[key_index] in self.attribute):
                    self.index_word = set()
                    self.main_word = ''
                    self.index_word.add(key_index)
                    self.find_words(key_index)
        return self.need_words

    def run(self, ):
        self.postags = self.word_sex()
        arcs = self.parser_words()
        self.dword = self.deal_data(arcs)
        need_word = self.filter()
        return need_word

    def prepare(self, ):
        attd = {}
        outlist = []
        allnum = 0

        for id, sentences in self.Dsent.items():
            self.keyword = ''
            wordlist = []
            upper_sentence = re.sub(r'\s', '', sentences.upper())
            split_sentence = re.split(ur'[,，、： …～。！. !]?', upper_sentence.decode('utf-8', 'ignore').strip())
            for sent in split_sentence:
                self.words = self.cut_word(sent.encode('utf-8', 'ignore'))
                if set(self.words) & set(self.c_no_meaningword):
                    for word in self.words:
                        if word == self.moniter_word:
                            self.keyword = word
                    continue
                need_word = self.run()
                if need_word:
                    for group in need_word:
                        mainword, word = group
                        wordlist.append(word)
                        if mainword not in attd.keys():
                            attd[mainword] = []
                        attd[mainword].append(word)
            if wordlist:
                allnum += 1
                line = '%s\t%s\t%s' % (id, sentences, ' '.join(wordlist))
                outlist.append(line)
                # else:
                #
                #     line = '%s\t%s\n' % (id, sentences)
                #     log_time = datetime.datetime.now().strftime('%Y-%m-%d')
        logging.info('have phrase num: %s' % allnum)
        # self.segmentor.release()  # 释放模型
        self.postagger.release()  # 释放模型
        self.parser.release()  # 释放模型
        return attd, outlist


if __name__ == "__main__":
    import logging.config
    program = os.path.basename(sys.argv[0])
    logger = logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s')
    logging.root.setLevel(level=logging.DEBUG)
    moniterword = '奥迪A4'
    # raw_data = es_query(moniterword, day=1)
    # sen_ins = MakeSentence(keyword=moniterword, raw_data=raw_data)
    # Dsents = sen_ins.extract_sentence()
    Dsents = {1: sys.argv[1]}
    ins = PhraseReconize(moniterword, Dsents, industry_id=2)
    attd, l = ins.prepare()
    print attd
    for attw, aagroup in attd.items():
        print '%s:%s' % (attw, ' '.join(aagroup))
