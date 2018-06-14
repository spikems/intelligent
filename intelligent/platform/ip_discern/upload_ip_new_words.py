#! /usr/bin/python
# -*- coding:utf-8 -*-
from intelligent.model.modelbase import ModelBase
import xlrd
import sys
reload(sys)
sys.setdefaultencoding('utf-8')




class UploadIpWords(ModelBase):
    def __init__(self):
        super(UploadIpWords, self).__init__()
        self.table = 'ip_find'
        self.ip_datas = {}

    def read_words(self, file_name, ip_type):
        # 读取txt文件
        ip_words = []
        name_dict = {}
        read_data = xlrd.open_workbook(file_name)
        table = read_data.sheets()[0]
        for i in range(1, table.nrows):
            line = table.row_values(i)
            one_data = []   # 用于存储一条IP的数据
            # 影视类IP的处理方式
            if ip_type == 3:
                line[2] = line[2].encode('utf-8')
                if '电影' in line[2] or '电视剧' in line[2]:    # 如果类别是电影或者电视剧
                    ip_name = line[3].strip().encode('utf-8')
                    if '｜' in line[5]:
                        eng_name_list = line[5].strip().split('｜')
                    else:
                        eng_name_list = line[5].strip().split('|')
                    if '｜' in line[7]:
                        syno_name_list = line[7].strip().split('｜')
                    else:
                        syno_name_list = line[7].strip().split('|')
                    tag = line[2].strip().encode('utf-8')
                    noise_ip = int(line[8]) if (line[8]) else 0
                    determiner_word = line[9].strip().encode('utf-8')
                    type_noise_ip = int(line[10]) if line[10] else 0
                    one_data.append(ip_name)
                    one_data.append(tag)
                    one_data.append(determiner_word)
                    one_data.append(int(noise_ip))
                    one_data.append(int(type_noise_ip))
                    if ip_name and ip_name not in name_dict.keys():
                        name_dict[ip_name] = one_data + [0]
                    for eng_name in eng_name_list:
                        eng_name = eng_name.strip()
                        if eng_name and eng_name not in name_dict.keys():
                            eng_name = eng_name.encode('utf-8').strip()
                            name_dict[eng_name] = one_data + [1]
                    for syno_name in syno_name_list:
                        syno_name = syno_name.strip()
                        if syno_name and syno_name not in name_dict.keys():
                            syno_name = syno_name.encode('utf-8').strip()
                            name_dict[syno_name] = one_data + [0]
            # 赛事类IP的处理方法
            if ip_type == 2:
                if line[2]:
                    ip_name = line[2].strip().encode('utf-8')
                    noise_ip = int(line[7]) if line[7] else 0
                    fdeterminer_word = line[9].strip().encode('utf-8')
                    one_data.append(ip_name)   # 放到tag字段
                    one_data.append(fdeterminer_word)   # 放到fdeterminer字段
                    one_data.append(noise_ip)  # 放到noise_ip字段
                    if '｜' in line[4]:
                        eng_name_list = line[4].strip().split('｜')
                    else:
                        eng_name_list = line[4].strip().split('|')
                    abbre_name = line[5].strip().encode('utf-8')
                    if '｜' in line[6]:
                        syno_name_list = line[6].strip().split('｜')
                    else:
                        syno_name_list = line[6].strip().split('|')
                    if ip_name and ip_name not in name_dict.keys():
                        name_dict[ip_name] = one_data + [0]
                    if abbre_name and abbre_name not in name_dict.keys():
                        name_dict[abbre_name] = one_data + [0]
                    for eng_name in eng_name_list:
                        eng_name = eng_name.strip()
                        if eng_name and eng_name not in name_dict.keys():
                            eng_name = eng_name.encode('utf-8').strip()
                            print eng_name
                            name_dict[eng_name] = one_data + [1]
                    for syno_name in syno_name_list:
                        syno_name = syno_name.strip()
                        if syno_name and syno_name not in name_dict.keys():
                            syno_name = syno_name.encode('utf-8').strip()
                            print syno_name
                            name_dict[syno_name] = one_data + [0]
            # 对小说类IP的处理方法
            if ip_type == 4:
                line[2] = line[2].encode('utf-8')
                if '小说' in line[2]:    # 如果类别是电影或者电视剧
                    ip_name = line[3].strip().encode('utf-8')
                    if '｜' in line[5]:
                        eng_name_list = line[5].strip().split('｜')
                    else:
                        eng_name_list = line[5].strip().split('|')
                    if '｜' in line[7]:
                        syno_name_list = line[7].strip().split('｜')
                    else:
                        syno_name_list = line[7].strip().split('|')
                    tag = line[2].strip().encode('utf-8')
                    noise_ip = int(line[8]) if (line[8]) else 0
                    determiner_word = ''
                    if '电影' not in line[2] and '电视剧' not in line[2]:  # 单独小说，才能加正向词
                        determiner_word = line[9].strip().encode('utf-8')
                    # [ip_name,tag,determiner_word,noise_ip, is_english_name]
                    one_data.append(ip_name)
                    one_data.append(tag)
                    one_data.append(determiner_word)
                    one_data.append(int(noise_ip))
                    if ip_name and ip_name not in name_dict.keys():
                        name_dict[ip_name] = one_data + [0]
                    for eng_name in eng_name_list:
                        eng_name = eng_name.strip()
                        if eng_name and eng_name not in name_dict.keys():
                            eng_name = eng_name.encode('utf-8').strip()
                            print eng_name
                            name_dict[eng_name] = one_data + [1]
                    for syno_name in syno_name_list:
                        syno_name = syno_name.strip()
                        if syno_name and syno_name not in name_dict.keys():
                            syno_name = syno_name.encode('utf-8').strip()
                            print syno_name
                            name_dict[syno_name] = one_data + [0]
                    # print name_dict
                    # raw_input('next:')
            # 影视类明星IP的处理方法
            if ip_type == 1:
                ip_name = line[1].strip().encode('utf-8')
                chinese_name = line[2].strip().encode('utf-8')
                if '｜' in line[3]:
                    eng_name_list = line[3].strip().split('｜')
                else:
                    eng_name_list = line[3].strip().split('|')
                if '｜' in line[4]:
                    syno_name_list = line[4].strip().split('｜')
                else:
                    syno_name_list = line[4].strip().split('|')
                one_data.append(ip_name)
                if ip_name and ip_name not in name_dict.keys():
                    name_dict[ip_name] = one_data + [0, 0]
                if chinese_name and chinese_name not in name_dict.keys():
                    name_dict[chinese_name] = one_data + [0, 0]
                for eng_name in eng_name_list:
                    eng_name = eng_name.strip()
                    if eng_name and eng_name not in name_dict.keys():
                        eng_name = eng_name.encode('utf-8')
                        name_dict[eng_name] = one_data + [1, 1]
                for syno_name in syno_name_list:
                    syno_name = syno_name.strip()
                    if syno_name and syno_name not in name_dict.keys():
                        syno_name = syno_name.encode('utf-8')
                        name_dict[syno_name] = one_data + [0, 0]
            # 有歧义的影视类明星IP
            if ip_type == 0:
                input_name = line[0].strip().encode('utf-8')
                ip_name = line[1].strip().encode('utf-8')
                determiner_word = line[2].strip().encode('utf-8')
                fdeterminer_word = line[3].strip().encode('utf-8')
                is_english_name = int(line[5]) if (int(line[5]) == 1) else 0
                # ip_name,determiner_word,fdeterminer_word,is_english_name
                one_data.append(ip_name)
                one_data.append(determiner_word)
                one_data.append(fdeterminer_word)
                one_data.append(is_english_name)
                name_dict[input_name] = one_data
            # 体育类明星IP
            if ip_type == 5:
                tag = line[0].strip().encode('utf-8')
                ip_name = line[1].strip().encode('utf-8')
                chinese_name = line[2].strip().encode('utf-8')
                if '｜' in line[3]:
                    eng_name_list = line[3].strip().split('｜')
                else:
                    eng_name_list = line[3].strip().split('|')
                if '｜' in line[4]:
                    syno_name_list = line[4].strip().split('｜')
                else:
                    syno_name_list = line[4].strip().split('|')
                determiner_word = line[5].strip().encode('utf-8')
                noise_ip = int(line[6]) if (line[6]) else 0
                # ip_name, tag, determiner_word, noise_ip, is_english_name
                one_data.append(ip_name)
                one_data.append(tag)
                one_data.append(determiner_word)
                one_data.append(noise_ip)
                if ip_name and ip_name not in name_dict.keys():
                    name_dict[ip_name] = one_data + [0]
                if chinese_name and chinese_name not in name_dict.keys():
                    name_dict[chinese_name] = one_data + [0]
                for eng_name in eng_name_list:
                    eng_name = eng_name.strip()
                    if eng_name and eng_name not in name_dict.keys():
                        eng_name = eng_name.encode('utf-8')
                        name_dict[eng_name] = one_data + [1]
                for syno_name in syno_name_list:
                    syno_name = syno_name.strip()
                    if syno_name and syno_name not in name_dict.keys():
                        syno_name = syno_name.encode('utf-8')
                        name_dict[syno_name] = one_data + [0]
            # 综艺类明星IP
            # 综艺类IP
            if ip_type == 6:
                line[2] = line[2].encode('utf-8')
                if '综艺' in line[2]:    # 如果类别是电影或者电视剧
                    ip_name = line[3].strip().encode('utf-8')
                    if '｜' in line[5]:
                        eng_name_list = line[5].strip().split('｜')
                    else:
                        eng_name_list = line[5].strip().split('|')
                    if '｜' in line[7]:
                        syno_name_list = line[7].strip().split('｜')
                    else:
                        syno_name_list = line[7].strip().split('|')
                    tag = line[2].strip().encode('utf-8')
                    noise_ip = int(line[8]) if (line[8]) else 0
                    # [ip_name,tag,noise_ip]
                    one_data.append(ip_name)
                    one_data.append(tag)
                    one_data.append(int(noise_ip))
                    if ip_name and ip_name not in name_dict.keys():
                        name_dict[ip_name] = one_data + [0]
                    for eng_name in eng_name_list:
                        eng_name = eng_name.strip()
                        if eng_name and eng_name not in name_dict.keys():
                            eng_name = eng_name.encode('utf-8').strip()
                            name_dict[eng_name] = one_data + [1]
                    for syno_name in syno_name_list:
                        syno_name = syno_name.strip()
                        if syno_name and syno_name not in name_dict.keys():
                            syno_name = syno_name.encode('utf-8').strip()
                            name_dict[syno_name] = one_data + [0]
                    # print name_dict
                    # raw_input('next:')
        print len(name_dict)
        raw_input('continue')
        return name_dict

    def up_load(self, ip_words, ip_type=0):
        for ip_word in ip_words:
            change_ip_word = ip_word.replace(r"'", r"\'")
            sql = ''
            try:
                if ip_type == 3:    # 影视类IP执行的代码
                    # [ip_name,tag,determiner_word,noise_ip,type_noise_ip]
                    sql = "insert into ip_find(name, type, ip_name, tag, determiner, noise_ip, type_noise_ip, is_english_name) values" \
                           "('%s',%d,'%s','%s','%s',%d, %d, %d)" % (change_ip_word, ip_type, ip_words[ip_word][0],
                            ip_words[ip_word][1], ip_words[ip_word][2], ip_words[ip_word][3], ip_words[ip_word][4], ip_words[ip_word][5])
                elif ip_type == 2:   # 赛事类IP执行的代码
                    # [ip_name,fdeterminer_word,noise_ip,is_english_name]
                    sql = "insert into ip_find(name, type, ip_name, fdeterminer, noise_ip, is_english_name) values" \
                          "('%s',%d,'%s','%s', %d, %d)" % (change_ip_word, ip_type, ip_words[ip_word][0],
                                                           ip_words[ip_word][1], ip_words[ip_word][2], ip_words[ip_word][3])
                elif ip_type == 4:   # 小说类IP执行的代码
                    # [ip_name,tag,determiner_word,noise_ip]
                    sql = "insert into ip_find(name, type, ip_name, tag, determiner, noise_ip, is_english_name) values" \
                          "('%s', %d, '%s', '%s', '%s', %d, %d)" % (change_ip_word, ip_type, ip_words[ip_word][0], ip_words[ip_word][1],
                             ip_words[ip_word][2], ip_words[ip_word][3], ip_words[ip_word][4])
                elif ip_type == 1:   # 明星类[ip_name,noise_ip, is_english_name]
                    sql = "insert into ip_find(name, type, ip_name, noise_ip, is_english_name) values" \
                          "('%s',%d,'%s',%d,%d)" % (change_ip_word, ip_type, ip_words[ip_word][0],
                                                    ip_words[ip_word][1], ip_words[ip_word][2])
                elif ip_type == 0:   # ip_name,determiner_word,fdeterminer_word,is_english_name
                    sql = "insert into ip_find(name, type, ip_name, determiner, fdeterminer, noise_ip, is_english_name) values" \
                          "('%s',%d,'%s','%s','%s',%d, %d)" % (change_ip_word, 1, ip_words[ip_word][0],ip_words[ip_word][1],
                                                               ip_words[ip_word][2], 1, ip_words[ip_word][3])
                elif ip_type == 5:   # ip_name, tag, determiner_word, noise_ip, is_english_name
                    sql = "insert into ip_find(name, type, ip_name, tag, determiner, noise_ip, is_english_name) values" \
                          "('%s', %d, '%s','%s','%s', %d, %d)" % (change_ip_word, 5, ip_words[ip_word][0], ip_words[ip_word][1],
                                                               ip_words[ip_word][2], ip_words[ip_word][3], ip_words[ip_word][4])
                elif ip_type == 6:  # [ip_name,tag,noise_ip, is_english_name]
                    sql = "insert into ip_find(name, type, ip_name, tag, noise_ip, is_english_name) values" \
                          "('%s', %d, '%s','%s',%d, %d)" % (change_ip_word, 6, ip_words[ip_word][0], ip_words[ip_word][1],
                                                            ip_words[ip_word][2], ip_words[ip_word][3])
                result = self.oDbBase.execute_sql(sql)
            except Exception as e:
                print(e)
                print(type(ip_word))
                print(ip_word)
                continue

    def run(self, file_name, ip_type):
        # 控制整个流程
        ip_words = self.read_words(file_name, ip_type)
        self.up_load(ip_words, ip_type=ip_type)

if __name__ == '__main__':
    test = UploadIpWords()
    # test.run('影视及小说IP更新（自己更新版） (2).xlsx', ip_type=3)
    # test.run('体育赛事IP.xlsx', ip_type=2)
    # test.run('影视及小说IP更新（自己更新版） (2).xlsx', ip_type=4)
    # test.run('影视类明星IP.xlsx', ip_type=1)
    # test.run('有歧义的明星ip.xlsx', ip_type=0)
    # test.run('体育类明星.xlsx', ip_type=5)
    test.run('新增影视小说综艺IP.xlsx', ip_type=4)