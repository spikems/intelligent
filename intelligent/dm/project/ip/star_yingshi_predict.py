# -*- coding:utf-8 -*-
# 对影视类明星的数据进行判断
import esm
import copy
import logging
import traceback
from intelligent.common.util import *
from intelligent.dm.project.ip.conf.ip_discern_conf import *
from intelligent.dm.project.ip.conf.basic_tools import load_result
from intelligent.dm.project.ip.conf.basic_tools import remove_ip_rule
from intelligent.dm.project.ip.conf.basic_tools import predicate_ip_rule


@singleton
class PredictStarYingShi(object):
    def __init__(self):
        self.err_logger = logging.getLogger('errinfo')
        self.models = None  # 保存影视类模型
        self.ip_words = None  # 保存ip词汇
        self.ip_type = None  # 保存所指的ip_type
        self.star_ip_index = None  # 影视类明星的全文搜索词
        self.load_index()  # 加载所需要的index

    def load_index(self):
        ip_name_index = esm.Index()
        for name in star_full_text_related_words:  # 将这种全文搜索词，只需要加载一起
            ip_name_index.enter(name)
        ip_name_index.fix()
        self.star_ip_index = ip_name_index

    def rule_filter(self, name_position_data, text):
        '''
        影视类明星的过滤规则
        :return:
        '''
        result = {}  # {'name1':[{'prob':1, 'type':'3', 'name':'一代宗师'}],  'name2':[{}]}
        try:
            # 获取经过反向规则判断得到的剩下的数据
            names_list = name_position_data.keys()
            contain_name = remove_ip_rule(self.ip_words, name_position_data, text, names_list)

            # 根据保留下来的数据来判断是否是ip
            for ip_word in contain_name:  # 遍历每一个ip词
                ip_name = self.ip_words[ip_word][0]['ip_name']  # 存储对应ip_name中的ip_name
                if ip_name in result:  # 如果此条ip_name 已经存在结果集里面了
                    continue
                # 根据范围内出现（化名）来去除
                judge_noise_word = False
                judge_noise_break = False
                for position in name_position_data[ip_word]:
                    start = position[0] - 24 if (position[0] - 24) > 0 else 0
                    end = position[1] + 24 if (position[1] + 24 < len(text)) else (len(text))
                    judge_scope = text[start: end]
                    for noise_word in ['化名', '编辑', '实习', '记者', '/摄', '观察员']:
                        if noise_word in judge_scope:
                            judge_noise_word = True
                            judge_noise_break = True
                            break
                    if judge_noise_break:
                        break
                if judge_noise_word:  # 如果规则4存在
                    continue
                # 根据basic_tools中的规则进行判断
                basic_judge_result = predicate_ip_rule(self.ip_words, ip_word, text, name_position_data, contain_name,
                                                       three_related=True)
                if basic_judge_result:
                    result[ip_name] = load_result(prob=1, ip_type=ip_types[self.ip_type], name=ip_word)
                    continue
                # 规则4，一定范围内出现词汇，进行判断
                judge_words = copy.deepcopy(star_part_text_related_words)
                other_names = copy.deepcopy(contain_name)
                other_names.remove(ip_word)
                for other_name in other_names:
                    if not self.ip_words[ip_word][0]['noise_ip']:     # 加其他ip的name加入附近判断的行列中
                        judge_words.append(other_name)
                judge_part_break = False
                for position in name_position_data[ip_word]:
                    judge_break = False
                    start = position[0] - 45 if (position[0] - 45) > 0 else 0
                    end = position[1] + 45 if (position[1] + 45 < len(text)) else (len(text))
                    judge_scope = text[start: end]
                    for word in judge_words:
                        if word in judge_scope:
                            result[ip_name] = load_result(prob=1, ip_type=ip_types[self.ip_type], name=ip_word)
                            judge_break = True
                            judge_part_break = True
                            break
                    if judge_break:
                        break
                if judge_part_break:   # 如果规则4存在
                    continue
                # 规则5，更小的范围内判断
                least_judge_words = star_least_text_related_words
                judge_least_break = False
                for position in name_position_data[ip_word]:
                    judge_break = False
                    start = position[0] - 24 if (position[0] - 24) > 0 else 0
                    end = position[1] + 24 if (position[1] + 24 < len(text)) else (len(text))
                    judge_scope = text[start: end]
                    for word in least_judge_words:
                        if word in judge_scope:
                            result[ip_name] = load_result(prob=1, ip_type=ip_types[self.ip_type], name=ip_word)
                            judge_break = True
                            judge_least_break = True
                            break
                    if judge_break:
                        break
                if judge_least_break:  # 如果规则4存在
                    continue
                # 规则5，前后100个字内判断存在相关性词汇
                for position in name_position_data[ip_word]:
                    start = position[0] - 150 if (position[0] - 150) > 0 else 0
                    end = position[1] + 150 if (position[1] + 150 < len(text)) else (len(text))
                    judge_scope = text[start: end]
                    full_text_name_position = self.star_ip_index.query(judge_scope)
                    if full_text_name_position:  # 如果范围内没有
                        result[ip_name] = load_result(prob=1, ip_type=ip_types[self.ip_type], name=ip_word)
                        break
        except:
            error = "stars_yingshi_rule_filter error. traceback: %s" % traceback.format_exc()
            self.err_logger.error(error)
        return result, []

    def predict_result(self, models, ip_words, ip_type, text, name_position_data):
        # 开始先赋初始值，只有使用权，没有修改权
        self.models = models
        self.ip_words = ip_words
        self.ip_type = ip_type
        try:
            result, model_predict_words = self.rule_filter(name_position_data, text)
            return result
        except:
            error = "stars_yingshi_predict.run error. traceback: %s" % traceback.format_exc()
            self.err_logger.error(error)
            return None
