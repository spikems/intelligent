#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import esm
import re
from intelligent.dm.project.semeval.server_conf import *
from intelligent.dm.project.semeval.preprocess_semevalrule import RulePreprocess

# 文本中只有一个品牌
TEXT_SINGLE_BRAND = 1
# 文本中有多个品牌，且并行
TEXT_MANY_BRAND_PARAL = 2
# 文本中有多个品牌，且不并行
TEXT_MANY_BRAND_NO_PARAL = 3
# 文本中无品牌
TEXT_OTHER = 4

# 短文本标记
TEXT_SHORT_TEXT = 1
# 近似短文本标记
TEXT_SIMILAR_SHORT_TEXT = 2
# 长文本文本标记
TEXT_LONG_TEXT = 3

# 字段默认值
DEFAULT_VALUE = -1


class SemevalRule:
    '''
        
        A Strategy Platform About Semeval.


        定义条件A：
            提取comp前边的内容 或者 全部内容后，提取内容中有target or opinion

        定义条件B1: 短距离
          brand + 正面opinion （短距离），  中间存在否定词

        定义条件B2：
          brand + 负面opinion（短距离），  中间不存在否定词


    '''

    def __init__(self, dSemevalInfo):

        self.id = dSemevalInfo[c_ID]
        self.industry = dSemevalInfo[c_INDUSTRY]
        self.text = self.__text_deal(dSemevalInfo[c_SHORTSENT])
        self.type = dSemevalInfo[c_TYPE]
        self.brand = dSemevalInfo[c_BRAND]
        self.link = dSemevalInfo[c_LINK]
        self.dSemevalWords = dSemevalInfo[c_SEMEVAL_OPINION]
        self.dWordType = dSemevalInfo[c_WORDTYPE]
        self.dOpinionSource = dSemevalInfo[c_OPINION_SOURCE]
        self.dOpinionPosition = dSemevalInfo[c_OPINION_POSITION]
        self.index = dSemevalInfo[c_INDEX]
        self.brand_index = dSemevalInfo[c_BRAND_INDEX]
        self.dWords = dSemevalInfo[c_SENT_WORDS]
        self.dRuleNegInfo = dSemevalInfo[c_WORDNEGINFO]
        self.dRuleInquireInfo = dSemevalInfo[c_WORDINQUIREINFO]
        self.bHighPrecision = False
        self.fProb = 0.51
        self.sSentence = ""
        self.oRP = RulePreprocess(self.index, self.brand_index, self.text, self.dWordType, self.brand)

        # extract text after target
        self.text = self.oRP.paralBrandDeal()
        # self.targetText =  self.oRP.getAfterTargetText()

        self.iShortLevel = DEFAULT_VALUE
        self.getShortText()
        self.bManyBrands = DEFAULT_VALUE
        self.isManyBrandText()

    # 特殊疑问词替换成常见的疑问词，特征提取时使用
    def __text_deal(self, text):
        return text.replace('么?', '怎么样?').replace('么？', '怎么样？').replace('?', '问号?').replace('？', '问号？')

    # 准备为一些变量初始化赋值
    def prepare(self):

        self.lValidFeatInfo = []
        self.lValidPosInfo = []
        self.dValidFeatInfo = {}
        self.bValidText_A = DEFAULT_VALUE
        self.sTargetText = DEFAULT_VALUE
        self.iTextType = DEFAULT_VALUE
        self.bValid_B1 = DEFAULT_VALUE
        self.bValid_B2 = DEFAULT_VALUE
        self.feat_B2 = DEFAULT_VALUE
        self.feat_B1 = DEFAULT_VALUE
        self.inquire = DEFAULT_VALUE

    # 执行规则
    def executeRule(self, sText):

        self.prepare()
        self.getCurFeatInfo(sText)
        self.getTextType()

        bRuleValid = False
        iType = c_NEGTIVE
        fProb = self.fProb
        reason = ''
        fs = dir(SemevalRule)

        # 判断用的是高精度规则，还是低精度规则
        func_exec = 'rule_high' if self.bHighPrecision else 'rule_low'
        for name in fs:
            # 如果存在该规则，并且规则也在线上，就执行
            if name.find(func_exec) != -1 and name in c_semeval_rule_industry[self.industry]:
                bRuleValid, iType, fProb, reason = getattr(self, name)()
                fProb = self.__getProb(reason, name)
                reason = '%s_%s' % (name, reason)
                # 返回值，bRuleValid为true，表示当前正在执行的规则失效，返回结果。
                if bRuleValid:
                    return bRuleValid, iType, fProb, reason
        return bRuleValid, iType, fProb, reason

    # 把传进来的长句子进行切分。转换成逗号间粒度的短句
    def getSents(self):

        sentences = []
        # print 'process text', self.text
        # print 'single text', self.iShortLevel, self.iShortLevel == TEXT_SIMILAR_SHORT_TEXT, self.bManyBrands
        # 如果 本身是短句 并且 是单品牌，则把该文本放到sentences中
        if not self.industry in c_semeval_rule_douhao_separator and (
                self.iShortLevel == TEXT_SHORT_TEXT or self.iShortLevel == TEXT_SIMILAR_SHORT_TEXT) and not self.bManyBrands:
            # print 'single text', self.iShortLevel, self.iShortLevel == TEXT_SIMILAR_SHORT_TEXT, self.bManyBrands
            sentences = [self.text]
        else:
            # 如果是长句，则按照标点符号切分，得到逗号间粒度的短句rawsents
            if not self.industry in c_semeval_rule_douhao_separator:
                self.targetText = self.oRP.getAfterTargetText()
                # print 'target text', self.targetText
                sentences = re.split('。', self.targetText)
            # print 'text', self.text
            rawsents = re.split('\...|。|；|;|？|\?|！|!|，|,|、', self.text)
            sentences.extend(rawsents)
            # sentences = re.split('。|；|;|？|\?|！|!|，|,', self.text)
            # sentences.append(self.targetText)

        # 返回逗号间粒度的短句集合
        return sentences

    def run(self, high_precision=False):

        self.bHighPrecision = high_precision

        # 将长句子切分为逗号间粒度短句子集合
        sentences = self.getSents()
        bRuleValid = False

        # 对于每一个逗号间粒度短句子，执行规则
        for sentence in sentences:
            if sentence.strip() == '':
                continue

            self.sSentence = sentence
            bRuleValid, iType, fProb, reason = self.executeRule(sentence)
            # 如果被规则命中生效，则 马上返回
            if bRuleValid:
                reason = '%s_%s' % (reason, sentence)
                return bRuleValid, iType, fProb, reason
        return bRuleValid, iType, fProb, reason

    # 概率， 按照不同情况返回不同的概率
    def __getProb(self, opinion, name):

        # 命中高精度规则，为0.51
        if name.find('rule_high') != -1:
            return c_PROB_DM_OPINION
        if opinion in self.dOpinionSource:
            source = self.dOpinionSource[opinion]
            # 命中挖掘组特征词，概率为0.51
            if source == c_DM_OPINION:
                return c_PROB_DM_OPINION
            # 命中数据组特征词，概率为0.50
            if source == c_DATA_OPINION:
                return c_PROB_DATA_OPINION_RULE
        return c_PROB_DM_OPINION

    def rule_high_1(self):

        '''
            dealer 处理
        '''

        bRuleValid = False
        iType = c_NEUTRAL
        fProb = self.fProb
        if self.link.strip() != '' and self.link.find(c_DEALER) != -1:
            bRuleValid = True
        return bRuleValid, iType, fProb, self.link

    def rule_high_2(self):

        '''
             教学维修类处理

        '''
        bRuleValid = False
        iType = c_NEUTRAL
        fProb = self.fProb
        reason = ''

        if not self.industry in c_semeval_rule2_feature:
            return bRuleValid, iType, fProb, reason

        keywords = c_semeval_rule2_feature[self.industry]
        for words in keywords:
            bRuleValid = True
            for word in words:
                if self.text.find(word) == -1:
                    bRuleValid = False
                    break
            if bRuleValid:
                reason = " ".join(words)
                break
        return bRuleValid, iType, fProb, reason

    def rule_high_3(self):

        '''
            滴滴网通社
        '''

        bRuleValid = False
        iType = c_NEUTRAL
        fProb = self.fProb
        if self.type.strip() != '' and self.type.find("网通社") != -1:
            bRuleValid = True
        return bRuleValid, iType, fProb, self.type

    def rule_low_29(self):

        '''
            @ + 吐槽
        '''

        bRuleValid = False
        iType = c_NEUTRAL
        fProb = self.fProb
        tcword = '吐槽'
        if self.type.find("微博") == -1:
            return bRuleValid, iType, fProb, tcword

        at_pos = self.text.find('@')
        if at_pos == -1:
            return bRuleValid, iType, fProb, tcword
        tucao_pos = self.text.find(tcword)
        if tucao_pos == -1:
            return bRuleValid, iType, fProb, tcword
        if tucao_pos - at_pos - 1 <= 3 * 6:
            bRuleValid = True
        return bRuleValid, iType, fProb, tcword

    def rule_low_30(self):

        '''
            只有一个品牌的.  +  A  +  B1
        '''
        bRuleValid = False
        iType = c_NEGTIVE
        fProb = self.fProb

        bValid, sFeat = self.B1()
        if (self.iTextType == TEXT_SINGLE_BRAND) and self.A() and bValid:
            bRuleValid = True

        return bRuleValid, iType, fProb, sFeat

    def rule_low_31(self):

        '''
            很短的内容内，只有一个品牌的.   + A  +  B2
        '''
        bRuleValid = False
        iType = c_NEGTIVE
        fProb = self.fProb

        bValid, sFeat = self.B2(level=1)
        # print bValid, sFeat
        if (self.iTextType == TEXT_SINGLE_BRAND) and self.A() and bValid:
            bRuleValid = True

        return bRuleValid, iType, fProb, sFeat

    def rule_low_32(self):
        '''
           很短的内容内，多个品牌，并列关系（、发你开）.   + A  +  B1
        '''
        bRuleValid = False
        iType = c_NEGTIVE
        fProb = self.fProb

        bValid, sFeat = self.B1()
        if (self.iTextType == TEXT_MANY_BRAND_PARAL) and self.A() and bValid:
            bRuleValid = True

        return bRuleValid, iType, fProb, sFeat

    def rule_low_33(self):
        '''
           很短的内容内，多个品牌，并列关系（、发你开）.   + A  +  B2
        '''

        bRuleValid = False
        iType = c_NEGTIVE
        fProb = self.fProb
        sFeat = ""

        bValid, sFeat = self.B2()
        # print 'rule_6', self.iTextType, self.iTextType == TEXT_MANY_BRAND_PARAL,  self.A() , self.isInquireText() ,  bValid
        if (self.iTextType == TEXT_MANY_BRAND_PARAL) and self.A() and bValid:
            bRuleValid = True
        # print self.dValidFeatInfo

        # print self.iTextType == TEXT_MANY_BRAND_PARAL, self.isInquireText(),  self.A(), bValid
        return bRuleValid, iType, fProb, sFeat

    def rule_low_34(self):

        '''
                single brand  + opinion (level 1) , no neg word
                :return:
        '''

        bRuleValid = False
        iType = c_NEGTIVE
        fProb = self.fProb
        sFeat = ""
        bValid, sFeat = self.B2(level=1)
        # print 'rule_7', self.bManyBrands,  self.A() , self.isInquireText() ,  bValid
        if not self.bManyBrands and bValid:
            bRuleValid = True
        return bRuleValid, iType, fProb, sFeat

    def A(self):

        '''
            判断提取后的短内容是否有target or opinion
        '''

        if not self.bValidText_A == DEFAULT_VALUE:
            return self.bValidText_A

        self.bValidText_A = False
        if c_OPINION_FEAT in self.dValidFeatInfo and c_TARGET_FEAT in self.dValidFeatInfo:
            self.bValidText_A = True
        # print 'A()', c_OPINION_FEAT in  self.dValidFeatInfo, c_TARGET_FEAT in self.dValidFeatInfo

        return self.bValidText_A

    def B1(self):

        '''
            target + 正面opinion，  中间存在否定词, 且有效距离
        '''

        if not self.bValid_B1 == DEFAULT_VALUE:
            return self.bValid_B1, self.feat_B1

        self.bValid_B1 = False
        if not c_NEG_FEAT in self.dValidFeatInfo:
            return self.bValid_B1, self.feat_B1

        if not c_TARGET_FEAT in self.dValidFeatInfo:
            return self.bValid_B1, self.feat_B1

        target_ind = self.dValidFeatInfo[c_TARGET_FEAT][0]
        for index in self.dValidFeatInfo[c_NEG_FEAT]:
            if index + 1 < len(self.lValidFeatInfo):
                opinion = self.lValidFeatInfo[index + 1]
                neg = self.lValidFeatInfo[index]

                # good distance between target and opinion
                if not self.nearTargetOpinionDis(self.brand, opinion, target_ind, index + 1):
                    continue

                # good distance between neg and OpinionDis
                if not self.nearNegOpinionDis(neg, opinion, index, index + 1) or not self.goodNegOpinionPos(neg, index,
                                                                                                            index + 1):
                    continue

                # if has opinion and inquire relation
                if c_INQUIRE_FEAT in self.dValidFeatInfo and self.hasInqireOpinionRelation(index + 1):
                    continue

                # if opinion word is good cut word
                if len(opinion) <= 6 and not opinion in self.dWords:
                    continue

                # neg not in opinion
                if opinion.find(neg) != -1 or neg.find(opinion) != -1:
                    continue

                # opinion is positive word
                if opinion in self.dSemevalWords and self.dSemevalWords[opinion] == c_POSITIVE:
                    self.bValid_B1 = True
                    self.feat_B1 = '%s_%s' % (neg, opinion)
                    break

        return self.bValid_B1, self.feat_B1

    def B2(self, level=0):

        '''
              target + 负面opinion  中间不存在否定词 且有效距离
              level : distance between target and opinion
        '''
        if not self.bValid_B2 == DEFAULT_VALUE:
            return self.bValid_B2, self.feat_B2
        # print '--------1'

        self.bValid_B2 = False
        if not c_OPINION_FEAT in self.dValidFeatInfo or not c_TARGET_FEAT in self.dValidFeatInfo:
            return self.bValid_B2, self.feat_B2
        # print '--------2'

        target_ind = self.dValidFeatInfo[c_TARGET_FEAT][-1]
        opinions = self.dValidFeatInfo[c_OPINION_FEAT]

        # print self.dValidFeatInfo
        for opinion_ind in opinions:

            opinion = self.lValidFeatInfo[opinion_ind]
            target = self.lValidFeatInfo[target_ind]
            # print opinion, target
            # good position between target and opinion
            if not self.goodPositionRelation(opinion, opinion_ind, target_ind):
                continue

            # good distance between target and opinion
            if not self.nearTargetOpinionDis(target, opinion, target_ind, opinion_ind, level):
                continue
            # print '--------2-1'

            # far distance between neg and opinion
            if c_NEG_FEAT in self.dValidFeatInfo:
                for neg_ind in self.dValidFeatInfo[c_NEG_FEAT]:
                    # print 'neg, opinon', neg_ind, opinion_ind
                    ret = False
                    neg_word = self.lValidFeatInfo[neg_ind]
                    opinion_word = self.lValidFeatInfo[opinion_ind]
                    near = self.nearNegOpinionDis(neg_word, opinion_word, neg_ind, opinion_ind)
                    ret = near and self.goodNegOpinionPos(neg_word, neg_ind, opinion_ind)
                    if ret:
                        break
                if ret:
                    # if self.nearNegOpinionDis(neg_word, neg_ind, opinion_ind) and self.goodNegOpinionPos(neg_word, neg_ind, opinion_ind):
                    continue
            # if has opinion and inquire relation
            if c_INQUIRE_FEAT in self.dValidFeatInfo and self.hasInqireOpinionRelation(opinion_ind):
                continue
            # print '--------2-2'

            # good cut opinion
            # opinion = self.lValidFeatInfo[opinion_ind]
            # if len(opinion) <= 6 and not opinion in self.dWords:
            #    continue
            # print '--------2-3'
            if opinion in self.dSemevalWords and self.dSemevalWords[opinion] == c_NEGTIVE:
                self.bValid_B2 = True
                self.feat_B2 = opinion
                return self.bValid_B2, self.feat_B2

        return self.bValid_B2, self.feat_B2

    # 评价词和监控词位置关系判断
    def goodPositionRelation(self, opinion, opinion_ind, target_ind):
        pos = self.dOpinionPosition[opinion]
        if pos == 'q':
            return opinion_ind < target_ind
        if pos == 'h':
            return opinion_ind > target_ind
        return True

    # 评价词和监控词有效距离判断
    def nearTargetOpinionDis(self, target, opinion, ind_A, ind_B, level=0):

        '''
        :param level:  0  high level (most near distance), 1  low level second serious
        return:
        '''
        dis = self.getDistance(target, opinion, ind_A, ind_B)
        thre = c_VALID_TARGET_OPINION_DISTANCE_HIGHLEVEL
        if level != 0:
            thre = c_VALID_TARGET_OPINION_DISTANCE_LOWLEVEL
        if dis < thre:
            return True
        return False

    # 评价词和否定词位置关系判断
    def nearNegOpinionDis(self, negword, opinion, ind_negword, ind_opinion):
        dis = self.getDistance(negword, opinion, ind_negword, ind_opinion)
        threshold = self.dRuleNegInfo[negword][1]
        threshold = c_VALID_NEG_OPINION_DISTANCE if threshold == 1000 else threshold
        # print 'dis comp', dis, threshold
        if dis <= threshold:
            return True
        return False

    # 疑问词和评价词的位置关系判断
    def hasInqireOpinionRelation(self, opinion_ind):

        hasRel = False
        for inquire_ind in self.dValidFeatInfo[c_INQUIRE_FEAT]:
            if self.isInquireOpinionRelation(opinion_ind, inquire_ind):
                hasRel = True
                break
        return hasRel

    # 是否是合理的疑问词和评价词位置关系
    def isInquireOpinionRelation(self, ind_opinion, ind_inquire):
        pos_Opi = self.lValidPosInfo[ind_opinion]
        pos_Inq = self.lValidPosInfo[ind_inquire]
        # print 'isInquireOpinionRelation', pos_Opi, pos_Inq
        inquire_word = self.lValidFeatInfo[ind_inquire]
        iMax, iMin = (pos_Inq, pos_Opi) if pos_Opi < pos_Inq else (pos_Opi, pos_Inq)
        symbols = [',', '，', '...', '。', '；', ';', '？', '?', '！', '!', '、']
        has = True
        # print '---zhongjian', iMin, iMax, self.sSentence, self.sSentence[iMin : iMax]
        for sym in symbols:
            if sym in self.sSentence[iMin: iMax]:
                # print 'sym', sym
                has = False
                break
        # print 'has', has
        if has and inquire_word in self.dRuleInquireInfo:
            opinion = self.lValidFeatInfo[ind_opinion]
            dis = self.getDistance(inquire_word, opinion, ind_inquire, ind_opinion)
            threshold = self.dRuleInquireInfo[inquire_word][1]
            pos = self.dRuleInquireInfo[inquire_word][0]
            has1 = True
            has2 = True
            if pos == 'q':
                has1 = ind_inquire < ind_opinion
            if pos == 'h':
                has1 = ind_inquire > ind_opinion
            if dis > threshold:
                has2 = False
            has = has1 and has2
        return has

    # 是不是合理的否定词评价词位置关系
    def goodNegOpinionPos(self, negword, ind_neg, ind_opinion):

        pos = self.dRuleNegInfo[negword][0]
        if pos == 'q':
            return ind_neg < ind_opinion
        if pos == 'h':
            return ind_neg > ind_opinion
        return True

    # 算距离，任意两个词wordA，位置ind_A，wordB，位置ind_B
    def getDistance(self, wordA, wordB, ind_A, ind_B):
        pos_A = self.lValidPosInfo[ind_A]
        pos_B = self.lValidPosInfo[ind_B]
        # print pos_A, pos_B
        if pos_A > pos_B:
            dis = pos_A - pos_B - len(wordB)
        else:
            dis = pos_B - pos_A - len(wordA)
        return dis

    def getTextType(self):

        '''
              1. single brand
              2. many brands, 并列关系
              3. many brands, 非并列关系
              4. 其他无效信息

        '''
        if self.iTextType != DEFAULT_VALUE:
            return

        if not c_BRAND_FEAT in self.dValidFeatInfo:
            self.iTextType = TEXT_OTHER
            return

        if len(self.dValidFeatInfo[c_BRAND_FEAT]) == 1:
            self.iTextType = TEXT_SINGLE_BRAND
            return

        if not c_BUT_FEAT in self.dValidFeatInfo:
            self.iTextType = TEXT_MANY_BRAND_PARAL
            return
        iMin = self.dValidFeatInfo[c_BRAND_FEAT][0]
        iMax = self.dValidFeatInfo[c_BRAND_FEAT][-1]
        for ind in self.dValidFeatInfo[c_BUT_FEAT]:
            if ind > iMin and ind < iMax:
                self.iTextType = TEXT_MANY_BRAND_NO_PARAL
                return

        self.iTextType = TEXT_MANY_BRAND_PARAL

    # 获得短文本级别信息
    def getShortText(self):

        iLength = len(self.text.replace(' ', '').decode('utf-8'))
        if iLength < c_SHORT_TEXT_LENGTH:
            self.iShortLevel = TEXT_SHORT_TEXT
        elif iLength < c_SIMILAR_SHORT_TEXT_LENGTH:
            self.iShortLevel = TEXT_SIMILAR_SHORT_TEXT
        else:
            self.iShortLevel = TEXT_LONG_TEXT

    # 是否是疑问形式文本
    def isInquireText(self):
        if not self.inquire == DEFAULT_VALUE:
            return self.inquire
        self.inquire = True if c_INQUIRE_FEAT in self.dValidFeatInfo else False
        # print self.inquire
        return self.inquire

    # 对待预测文本的进行解析，将其一些特征存为字典
    def getCurFeatInfo(self, sText):

        if len(self.lValidFeatInfo) != 0:
            return
            # extract feature info
        ret = self.index.query(sText)
        ind = 0
        for item in ret:
            feat = item[1]
            iStartPos = item[0][0]
            Type = self.dWordType[feat]
            # print feat,  Type, iStartPos
            if Type == c_COMP_FEAT and feat in self.dWords:
                break

            # lValidFeatInfo存储每个特征， lValidPosInfo存储每个特征的位置。在计算距离时会用到。
            self.lValidFeatInfo.append(feat)
            self.lValidPosInfo.append(iStartPos)

            # 每种特征类型做key， value为其出现的位置
            if not Type in self.dValidFeatInfo:
                self.dValidFeatInfo[Type] = []
            self.dValidFeatInfo[Type].append(ind)

            # 监控词出现的位置
            if Type == c_BRAND_FEAT and (feat in self.brand or self.brand in feat):
                if not c_TARGET_FEAT in self.dValidFeatInfo:
                    self.dValidFeatInfo[c_TARGET_FEAT] = []
                self.dValidFeatInfo[c_TARGET_FEAT].append(ind)
            ind += 1

        # 提取comp前边的内容，或者全部内容。
        ind = -1
        if c_COMP_FEAT in self.dValidFeatInfo:
            ind = self.dValidFeatInfo[c_COMP_FEAT][0]
        self.sTargetText = sText[:ind]

    # 判断是否是多品牌文本
    def isManyBrandText(self):

        i = 0
        j = 0
        ret = self.index.query(self.text)
        prePos = 0
        preBrand = ''
        first = True
        dBrand = {}
        for item in ret:
            feat = item[1]
            iStartPos = item[0][0]
            Type = self.dWordType[feat]
            if Type != c_BRAND_FEAT:
                continue
            # print feat, iStartPos, Type, prePos, preBrand

            if first:
                prePos = iStartPos
                preBrand = feat
                i = i + 1
                dBrand[feat] = 1
                # print prePos, len(preBrand), preBrand, iStartPos, feat, i
                first = False
                continue

            bIngore = False
            for brand in dBrand:
                if feat in brand:
                    bIngore = True
                    break
            if bIngore:
                continue

            # 距离两个字之外才算新字
            if prePos + len(preBrand) + 3 * 2 < iStartPos:
                i = i + 1
                # print prePos, len(preBrand), iStartPos, prePos, preBrand, feat, i
                # elif prePos + len(preBrand) + 3 * 2 >= iStartPos:
                # j = j - 1
                # print 'near', prePos, len(preBrand), preBrand, iStartPos, feat, j
            prePos = iStartPos
            preBrand = feat
            dBrand[feat] = 1
        # print 'brand cnt', i
        # print prePos, len(preBrand), preBrand, iStartPos, feat, i
        self.bManyBrands = (i + j) > 1
