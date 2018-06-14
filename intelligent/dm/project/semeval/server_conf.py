# -*-  coding:utf-8 -*-
import os

# when add a industry, you must configure c_semeval_model\c_semeval_rule\c_semeval_rule_control\c_semeval_model_feattype\c_industry_neg_thre\c_3_class

# model configure
# c_semeval_model or semeval rule configure, 线上行业id及对应的模型名字
c_semeval_model = {
    '2': 'car_xgb',
    '11': 'didi_xgb',
}

# semval model feature combine type， 模型用的特征提取方法
c_semeval_model_feattype = {
    '2': 1,
    '11': 2
}

# industry neg threshold which works when c_semeval_model is configured, also, which for two class
c_industry_neg_thre = {

    '2': {-1: 0.52, 0: 0.04},  # prob>=0.52 负面， frob >= 0.04 && frob < 0.51 中立, frob
    # '11' : { -1 : 0.8, 0 : 0.5}, # prob>=0.8 负面,  frob >= 0.5 && frob < 0.8 中立,
}

# three class industry
c_3_class = {
    '11': 1
}

####rule configure
# simu is simulate or prod is product
c_semeval_rule = {
    '2': {'high': 'prod', 'low': 'prod'},
    '11': {'high': 'prod', 'low': 'prod'}
}

# industry sentence configure
c_semeval_rule_douhao_separator = {
}
# industry rule configure
c_semeval_rule_industry = {
    '2': ['rule_high_1', 'rule_high_2', 'rule_low_31', 'rule_low_33', 'rule_low_34'],
    '11': ['rule_high_1', 'rule_high_2', 'rule_high_3', 'rule_low_31', 'rule_low_33', 'rule_low_34']
}

# semeval rule1 feature word filter
c_semeval_rule2_feature = {
    '2': [
        ['投诉与建议致电96998'], ['投诉电话'], ['举报违规检举侵权投诉'], ['投诉热线'], ['教你'], ['学习', '知识'], ['教学'], ['教程'], ['统理论'],
        ['技术', '解读'], ['故障案例']
    ],
    '11': [
        ['滴滴打人'], ['可拨打'], ['投诉电话'], ['举报违规检举侵权投诉'], ['低头'], ['投诉咨询'], ['投诉热线']
    ]
}

c_project_path = os.path.dirname(os.path.realpath(__file__))

# 预测结果，规则预测和参数或文本出问题的结果
c_RULE_PRED_RESULT = [1.0, 1.0]
c_NO_INDUSTRY_RESULT = [2.0, 2.0]
c_NO_TARGET_OR_OPINION_RESULT = [3.0, 3.0]

# 预测类型几种情况，无效，没特征，正面，中立，负面
c_NO_VALIDAT = -2
c_NO_FEATURE = -3
c_POSITIVE = 1
c_NEUTRAL = 0
c_NEGTIVE = -1

# 高精度规则1，用的url中含有dealer这个单词，就是中立
c_DEALER = 'dealer'

# field key name about rule class param init
c_ID = 'id'
c_INDUSTRY = 'industry'
c_TITLE = 'title'
c_DOCUMENT = 'document'
c_TYPE = 'type'
c_BRAND = 'brand'
c_LINK = 'link'
c_NEGTVIE_FEAT = 'negtive_feat'
c_WORDMAP = 'wordmap'
c_SENT_WORDS = 'sent_words'
c_SEMEVAL_OPINION = 'opinion'
c_WORDTYPE = 'wordtype'
c_WORDNEGINFO = 'c_neg_thre'
c_WORDINQUIREINFO = 'c_inquire_thre'
c_INDEX = 'index'
c_BRAND_INDEX = 'brand_index'
c_OPINION_POSITION = 'opinion_position'
c_OPINION_SOURCE = 'opinion_source'

# rule threshold
c_SHORT_TEXT_LENGTH = 40
c_SIMILAR_SHORT_TEXT_LENGTH = 100
c_SHORTSENT = 'shortsent'
c_VALID_NEG_OPINION_DISTANCE = 3 * 10 + 3 * 2  # 中间最多6个字，外加否定词自身的长度
c_VALID_TARGET_OPINION_DISTANCE_HIGHLEVEL = 3 * 10
c_VALID_TARGET_OPINION_DISTANCE_LOWLEVEL = 3 * 10

# rule feature directory
c_RULE_FEATURE = 'feature'
c_BRAND_FEAT = 'brand'
c_TARGET_FEAT = 'target'
c_OPINION_FEAT = 'opinion'
c_COMP_FEAT = 'comp'
c_BUT_FEAT = 'but'
c_NEG_FEAT = 'neg'
c_INQUIRE_FEAT = 'inquire'

# 规则预测和数据组商量好的返回值
c_PROB_DM_OPINION = 0.51
c_PROB_DATA_OPINION_RULE = 0.50
c_PROB_DATA_OPINION_NO_RULE = 0.49

# 数据组整理的特征，挖掘组整理的特征
c_DATA_OPINION = 1
c_DM_OPINION = 0
