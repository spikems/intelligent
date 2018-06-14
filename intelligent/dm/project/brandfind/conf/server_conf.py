#!/usr/bin/python
# -*- coding: utf-8 -*-

import os

#
# 行业模型对应的关系
#
c_industry_model = {
    '小米': 'xiaomi',
    '汽车': 'car-1200',
    '数码': 'phone',
    '母婴': 'muying',
    '运动': 'sport-6',
    # '电视' : 'tv-7',
    # '电影' : 'tv-7',
    '美妆': 'hzp-5',
    '安利': 'anli-6',
    '时尚': 'shishang-300',
    '网约车': 'didi6',
    '美食': 'meishi-6',
    '教育': 'education-5',
    '共享单车': '',
    # '电商' : 'ElectricityBusiness-5',
    '健康': 'health-6',
    '餐饮': 'canying-6',
    '租房': ''
}

#
# 品牌输出名称转换
#
c_brand_transform = {
    '名图': '新名图'
}

#
# 只过策略的品牌
#
c_only_strategy_brand = {
    '名图': 1
}
#
# 模拟的品牌,只打日志,不返回结果
#
c_simulate_brand = {

}

#
# 只过策略的行业
#
c_only_strategy = {
    '共享单车 ': 1
}

#
# 策略识别的品牌打的分数
#
c_strategy_brand_score = 0.81

# 过完模型以后的识别出品牌，过滤掉不需要的内容，如名图，过滤掉新名图
#
c_after_model = {
}

#
# 难识别的品牌词不会被识别，当且仅当hard_brand = False.
#
c_hard_brands = {
    '安利': 1,
    '仙贝': 1,
    '牛奶': 1,
    '蔡旺家': 1,
    '蔡衍明': 1,
    '旺旺': 1,
    '旺仔 ': 1,
    '阳光': 1,
    '布蕾': 1,
    '特浓牛奶': 1,
    '芝士仙贝': 1,
    '仙贝物语': 1,
    '拼车': 1,
    '专车': 1,
    '租车': 1,
    '出租车': 1,
    '代驾': 1,
    '网约车': 1
}
# 先过正向的品牌
c_zheng_brand = {
    '滴滴': 1
}

# 很难识别的品牌
SPECIAL_NOISE_BRAND_DIDI = '滴滴'

#
# 品牌识别项目目录
#

c_project_path = '%s/../' % os.path.dirname(os.path.realpath(__file__))

#
# 品牌识别模型目录
#

c_model_path = '%smodel' % (c_project_path)

#
# 日志名称
#
c_log = "intelligent"
c_errlog = "errinfo"
