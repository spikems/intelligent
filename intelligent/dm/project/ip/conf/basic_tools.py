# -*- coding:utf-8 -*-
import copy
from jieba.norm import norm_cut, norm_seg
from intelligent.dm.project.ip.conf.ip_discern_conf import ip_related_words


def load_result(prob, ip_type, name):
    '''
    封装识别识别结果的结构
    :return:
    '''
    one_list_result = []
    one_dict_result = {}
    one_dict_result['prob'] = prob
    one_dict_result['type'] = ip_type
    one_dict_result['name'] = name
    one_list_result.append(one_dict_result)
    return one_list_result


def cut_input(process_data):
    '''
        cut a input string, return utf-8 string  jieba中文分词的处理
    '''
    result = norm_seg(process_data)
    words_list = []
    for w in result:
        if w.word.strip() == '':
            continue
        words_list.append(w.word)
    words = " ".join(words_list)
    return words.encode('utf-8')


def remove_ip_rule(ip_words, name_position_data, text, names_list):
    contain_name = copy.deepcopy(names_list)
    remove_ip_list = []  # 保存，因为反向词、前后字母、无法分词需要去除的数据
    for ip_word in names_list:
        # 前提规则：反相关性进行判定
        if ip_words[ip_word][0]['fdeterminer']:
            judge_fdeterminer = False
            fdeterminer_words = ip_words[ip_word][0]['fdeterminer'].split('、')  # 非霍奇金、淋巴瘤
            for fdeterminer in fdeterminer_words:
                if fdeterminer in text:  # 当出现NFL的时候，出现了非霍奇金或者淋巴瘤，则认为非IP词
                    judge_fdeterminer = True  # 认为出现了反向限定词
                    break
            if judge_fdeterminer:  # 出现反向限定词，跳过此ip_word进行下一个
                remove_ip_list.append(ip_word)
                continue
        # 规则0，前后有字母的数据去掉
        if ip_words[ip_word][0]['is_english_name'] == 1:  # 如果是英文名字
            remove_position_list = []
            for position in name_position_data[ip_word]:  # [(position1), (position2)]
                start_pos = position[0]
                end_pos = position[1]
                if (text[start_pos - 1].isalnum()) and start_pos > 0:  # 如果前一或后一是字母或数字，此处非IP
                    remove_position_list.append(position)
                    continue
                if len(text) > end_pos:
                    if text[end_pos].isalnum():  # 如果前一或后一是字母或数字，此处非IP
                        remove_position_list.append(position)
                        continue
            for remove_data in remove_position_list:  # name_position_data去除position数据
                name_position_data[ip_word].remove(remove_data)
            if len(name_position_data[ip_word]) == 0:  # 如果没有position数据
                remove_ip_list.append(ip_word)
                continue
        # 规则0-1,需要分词的中文IP的数据，无法分词的去掉
        if ip_words[ip_word][0]['is_cut_word'] == 1:
            remove_position_list = []
            for position in name_position_data[ip_word]:
                start = position[0] - 60 if (position[0] - 60) > 0 else 0
                end = position[1] + 60 if (position[1] + 60 < len(text)) else (len(text))
                words_cut = norm_cut(text[start: end])
                word_list = []
                for word in words_cut:
                    word_list.append(word.encode('utf-8'))
                if ip_word not in word_list:
                    remove_position_list.append(position)
            for remove_data in remove_position_list:
                name_position_data[ip_word].remove(remove_data)
            if len(name_position_data[ip_word]) == 0:  # 如果没有position数据
                remove_ip_list.append(ip_word)
    for rm_ip in remove_ip_list:  # 根据去除规则，去除的数据
        contain_name.remove(rm_ip)
    return contain_name


def predicate_ip_rule(ip_words, ip_word, text, name_position_data, contain_name, quotes=False, three_related=False):
    # quotes：书名号,three_related 同类
    #  规则一：判断是否是噪音IP   'noise_ip' ：0或1，整形
    if not ip_words[ip_word][0]['noise_ip']:  # 如果是词ip是非噪音
        return True

    # 规则二：强相关性进行判定
    if ip_words[ip_word][0]['determiner']:  # 如果存在正限定词(有些noise_ip为1的词可能没有限定词)
        determiner_words = ip_words[ip_word][0]['determiner'].split('、')  # [土豆、大主宰...]
        for determiner in determiner_words:
            if determiner in text:  # 如果在出现 一代宗师的IP中，出现了王家卫，则认定一代宗师是一个IP词
                return True

    # 规则三：《左耳》【左耳】直接进行判定，（这里有个问题，将影视类的也同时识别进去了）
    if quotes:
        for position in name_position_data[ip_word]:  # [(position1), (position2)]
            start_pos = position[0] - 5 if (position[0] - 5) > 0 else 0
            end_pos = position[1] + 5 if (position[1] + 5) < len(text) else len(text)
            judge_symbol_1 = text[start_pos: end_pos]  # 根据《》，【】判断
            if (('《%s》' % ip_word) in judge_symbol_1) or (('【%s】' % ip_word) in judge_symbol_1):
                return True

    # 规则四：判断一个评论里面出现3个及以上的IP词，如果其中一个非是noise ip则为True, 如果5个以上，则IP为True
    if False: #three_related:
        if not ip_words[ip_word][0]['type_noise_ip']:   # 如果是type_noise_ip
            if len(contain_name) > 2:
                for ip_name in contain_name:
                    if not ip_words[ip_name][0]['noise_ip']:
                        return True
            if len(contain_name) > 5:
                return True
    return False


def model_predict(models, ip_types, process_text, ip_word, ip_type, judge_prob=0.5, tag=None):
    '''
    模型过滤
    :return:
    '''
    one_list_result = []
    if tag:
        predictor = models[ip_type][tag]
    else:
        predictor = models[ip_type]
    pred_prob = predictor.predict_one(process_text)[1][0][1]
    if pred_prob >= judge_prob:  # 如果概率大于1，则添加数据
        one_list_result = load_result(prob=pred_prob, ip_type=ip_types[ip_type], name=ip_word)
    return one_list_result


def related_word_process_data(position_data, content, ip_type, length=36):
    first_process_data = ''  # 第一步数据处理，对于影视，是修改为IP,添加word0新权重词
    related_words = ip_related_words[ip_type]
    result_content = []
    last_end_pos = 0
    deal_content = content
    word_num = 0
    for item in position_data:
        start_pos = item[0]
        end_pos = item[1]
        if result_content:  # 已经存有部分数据了，则把最后一项处理
            deal_content = result_content.pop()
        # 将ip_word 转换为 IP词
        result_content.append(deal_content[:start_pos - last_end_pos])
        result_content.append('IP')
        result_content.append(deal_content[end_pos - last_end_pos:])
        start_border = (start_pos - length) if (start_pos - length) > 0 else 0
        end_border = end_pos + length if (end_pos + length) < len(content) else len(content)
        judge_symbol_2 = content[start_border: end_border]
        for word in related_words:  # 在IP词的前后12字符中，查找相关性的词汇，如果有，加一个特征word0
            if word in judge_symbol_2:
                result_content.insert(0, 'word%d,' % word_num)  # 当出现一次以上的词，添加一个权重词word1
                word_num += 1
        last_end_pos = end_pos
        first_process_data = ''.join(result_content)  # 这里先做合并处理
    return first_process_data, word_num
