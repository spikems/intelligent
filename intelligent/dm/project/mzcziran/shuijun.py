# -*- coding:utf-8 -*-
from collections import Counter
'''
水军：
1、摘要大量一样的内容（重复10条以上）
2、品牌的美文宣传（标题重复10条以上且都是正面）
3、包含“国际妈”的数据
4、包含“建议选择知名度高”、“几乎都来自这几个区域”、    
'''
def _unicode_str(s, encoding="utf-8"):
    if isinstance(s, unicode):
        return s
    if not isinstance(s, str):
        return unicode(s)
    return s.decode(encoding, "ignore")

def shuijun_deal(raw_list):
    title_list = []
    text_list = []
    all_repeate = []
    shuijun_keyword = [u"国际妈", u"建议选择知名度高",u"几乎都来自这几个区域",u"我们所熟知"]
    for x in raw_list:
    #标题重复十条h或者摘要重复十次
        if x['title']:
            title_list.append(x.get('title',))
        if x['document']:
            text_list.append(x.get('document',))
    title_repeate = Counter(title_list)
    text_repeate = Counter(text_list)
    for k, v in title_repeate.items():
        if v >= 10:
            all_repeate.append(k)
    for k, v in text_repeate.items():
        if v >= 10:
            all_repeate.append(k)
    shuijun_list = []
    for x in raw_list:
        r = set(map(_unicode_str, x.values())) & set(map(_unicode_str, all_repeate))
        if r :
            raw_list=[xi for xi in raw_list if xi!=x]
            shuijun_list.append({"type":4,"id":x["id"],"prob":1})
	else :
            for i in shuijun_keyword:
                if i in x['title'] or i in x['document']:
                    raw_list=[j for j in raw_list if j!=x]
            	    shuijun_list.append({"type":4,"id":x["id"],"prob":1})
		    break
    return raw_list,shuijun_list


if __name__ == '__main__':
    raw_list = [{'id':1,'title':u'刚出生的宝宝你们给她（他）喝什么牌子的奶粉','document':u'备了荷兰牛栏2017-05-0815:01...'}]
    shuijun_deal(raw_list)
