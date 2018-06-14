# -*- coding:utf-8 -*-
# 对影视类的数据进行判断
import logging
import traceback
from intelligent.common.util import *
from intelligent.dm.project.ip.conf.ip_discern_conf import *
from intelligent.dm.project.ip.conf.basic_tools import cut_input
from intelligent.dm.project.ip.conf.basic_tools import load_result
from intelligent.dm.project.ip.conf.basic_tools import model_predict
from intelligent.dm.project.ip.conf.basic_tools import remove_ip_rule
from intelligent.dm.project.ip.conf.basic_tools import predicate_ip_rule

@singleton
class PredictStarSport(object):
    def __init__(self):
        self.err_logger = logging.getLogger('errinfo')
        self.models = None  # 保存影视类模型
        self.ip_words = None  # 保存ip词汇
        self.ip_type = None  # 保存所指的ip_type

    def rule_filter(self, name_position_data, text, names_data, name_tag):
        '''
       体育类明星的过滤规则
       :return:
       '''
        result = {}  # {'name1':[{'prob':1, 'type':'3', 'name':'一代宗师'}],  'name2':[{}]}
        model_predict_words = {}  # 保存的是需要过模型的数据
        try:
            # 获取经过反向规则判断得到的剩下的数据
            names_list = names_data.keys()
            contain_name = remove_ip_rule(self.ip_words, name_position_data, text, names_list)

            for ip_word in contain_name:
                i_n = names_data[ip_word]
                ip_name = self.ip_words[ip_word][i_n]['ip_name']  # 存储对应ip_name中的ip_name
                if ip_name in result:  # 如果此条ip_name 已经存在结果集里面了
                    continue
                # 根据basic_tools中的规则进行判断
                basic_judge_result = predicate_ip_rule(self.ip_words, ip_word, text, name_position_data, contain_name,
                                                       three_related=True)
                if basic_judge_result:
                    result[ip_name] = load_result(prob=1, ip_type=ip_types[self.ip_type], name=ip_word)
                    continue
                # 规则3：对汤普森和亚当斯进行判断
                if ip_word in ['汤普森', '亚当斯']:
                    judge_fdeterminer = True
                    if ip_word == '汤普森':
                        fdeterminer_words = ['詹姆斯', '乐福', '韦德', '罗斯', '卡戴珊', '骑士', '特里斯坦', '斯坦', 'tt汤普森']
                        for fdeterminer in fdeterminer_words:
                            if fdeterminer in text:
                                judge_fdeterminer = True
                                result['特里斯坦·特雷沃·詹姆斯·汤普森'] = load_result(prob=1, ip_type=ip_types[self.ip_type], name=ip_word)
                                break
                        if judge_fdeterminer:
                            continue
                    elif ip_word == '亚当斯':
                        fdeterminer_words = ['新疆', '外援']
                        for fdeterminer in fdeterminer_words:
                            if fdeterminer in text:
                                judge_fdeterminer = True
                                result['达柳斯·亚当斯'] = load_result(prob=1, ip_type=ip_types[self.ip_type],name=ip_word)
                                break
                        if judge_fdeterminer:
                            continue
                model_predict_words[ip_word] = name_position_data[ip_word]
        except:
            error = "sport_stars__rule_filter error. traceback: %s" % traceback.format_exc()
            self.err_logger.error(error)
        return result, model_predict_words

    @staticmethod
    def process_data(ip_word, position_data, content, ip_type, tag=None):
        '''
        数据的处理
        :return:
        '''
        related_words = ip_related_words[ip_type][tag]
        word_num = 0
        for word in related_words:
            if word in content:
                content = 'word%d,' % word_num + content
                word_num += 1
            if word_num > 1:  # 最多只有word0, word1,这两个
                break
        process_result = cut_input(content)  # 做分词处理
        return process_result

    def filter_other_sports_name_date(self, name_data):
        '''
        tag_class = ['篮球','足球']
        (1):将识别出来的IP根据tag分为3大类{'足球':[],'篮球':[],'其他球类': []}
        '''
        tag_class_dict = {}
        for ip_word in name_data:
            number = 0
            for ip_word_tags in self.ip_words[ip_word]:
                tag = ip_word_tags['tag']
                if '篮球' in tag:
                    tag_class_dict['篮球'] = tag_class_dict.get('篮球',{})
                    tag_class_dict['篮球'][ip_word] = number
                elif '足球' in tag:
                    tag_class_dict['足球'] = tag_class_dict.get('足球', {})
                    tag_class_dict['足球'][ip_word] = number
                else:
                    tag_class_dict['其他体育'] = tag_class_dict.get('其他体育', {})
                    tag_class_dict['其他体育'][ip_word] = number
                number += 1
        return tag_class_dict

    def predict_result(self, models, ip_words, ip_type, text, name_position_data):
        # 开始先赋初始值，只有使用权，没有修改权
        self.models = models
        self.ip_words = ip_words
        self.ip_type = ip_type
        try:
            result = {}
            name_tag_classify = self.filter_other_sports_name_date(name_position_data.keys())
            for name_tag in name_tag_classify:
                raw_result, model_predict_words = self.rule_filter(name_position_data, text,
                                                                   name_tag_classify[name_tag], name_tag)
                if model_predict_words:  # 如果含有词，则需要先对数据进行处理，然后再过模型
                    for ip_word in model_predict_words:
                        # 对需要过模型的数据进行预处理，返回的处理过的数据
                        process_text = self.process_data(ip_word, model_predict_words[ip_word],
                                                         content=text, ip_type=self.ip_type, tag=name_tag)
                        one_list_result = model_predict(self.models, ip_types, process_text, ip_word, self.ip_type,
                                                        tag=name_tag)
                        i_n = name_tag_classify[name_tag][ip_word]
                        ip_name = self.ip_words[ip_word][i_n]['ip_name']
                        if one_list_result:
                            raw_result[ip_name] = one_list_result
                result = dict(result, **raw_result)  # 合并字典的操作
            return result
        except:
            error = "ip_predict.run error. traceback: %s" % traceback.format_exc()
            self.logger.error(error)
            return None

