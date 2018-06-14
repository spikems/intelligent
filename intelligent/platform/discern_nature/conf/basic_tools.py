# -*- coding:utf-8 -*-
from jieba.norm import norm_cut, norm_seg
import simhash
import sys, time
import re, os, os.path
project_path = os.path.dirname(os.path.realpath(__file__))  # 获取当前文件夹的路径


def cut_input(input):
    '''
    cut a input string, return utf-8 string
    '''
    result = norm_seg(input)
    wordsList = []
    for w in result:
        if w.word.strip() == '' or w.flag.strip() == '':
            continue
        wordsList.append(w.word)
    with open(project_path + '/stopwords') as f:
        stop_words = []
        data = f.readline().strip()
        while data:
            stop_words.append(data)
            data = f.readline().strip()
    drop_word_list = []  # 需要删掉的word
    for word in wordsList:
        if word.encode('utf-8').strip() in stop_words:
            drop_word_list.append(word)
        elif len(word.encode('utf-8').strip()) == len(word.strip()):
            drop_word_list.append(word)
    for drop_word in drop_word_list:
        wordsList.remove(drop_word)
    words = " ".join(wordsList)

    return words.encode('utf-8')


def compute(text):
    """
        compute hash for a document by shingles
    """
    #tokens = re.split(r'\W+', text)
    tokens = text.split()   # 默认以‘ ’来进行切割，得到分词的列表
    #logger.debug('%s', ''.join(tokens[:5]))

    phrases = (' '.join(phrase) for phrase in simhash.shingle(tokens, 4))
    #logger.debug('%s', [x for x in phrases])
    hashes = map(simhash.unsigned_hash, phrases)
    return simhash.compute(hashes)


def dedup_near(data_list, b, k, debug=False):
    """
    """
    #
    removelist = []
    grplist = []

    duphash = {}  # hash -> set(lineid)  # 保存的是每一个hash值，对应的所有lineid值 {hash1,{id1,id24,id100...}}

    #
    linecnt = 1
    data_h = []  # list of hash val
    index = {}  # hash val -> lineid   {hash1：[lineid1], hash2：[lineid2]  保存每一个hash值第一次出现的lineid值
    data_v = {}  # lineid -> data
    for line in data_list:
        # apos = line.find(' ')
        hash = compute(line)
        data_h.append(hash)  # 将所有数据的hash值放入到data_h中
        tokens = line.split()   # 如果分词的长度低于5
        if len(tokens) < 5:
            linecnt += 1
            continue

        # here duplicate hash exist
        if hash in index:
            # add the same line into the same group
            # set grpid to the grpid of the last lineid with equal hash value
            if hash in duphash:
                duphash[hash].append(linecnt)
            else:
                # init with the first lineid
                duphash[hash] = [index[hash]]
                duphash[hash].append(linecnt)
        else:
            index[hash] = linecnt
        data_v[linecnt] = line
        # data_v[linecnt] = line[apos:]
        linecnt += 1
    # logger.info('lines=%s', '\n'.join([data_v[x] for x in range(5)]))
    #    logger.info('hash=%s', data_h[:5])

    # if debug:
    #     with open('hash.txt', 'w') as hashf:
    #         for h in data_h:
    #             hashf.write('%s\n' % h)
    #     with open('hash_full.txt', 'w') as hashf:
    #         for idx in range(len(data_h)):
    #             hashf.write('%s %s' % (data_h[idx], data_v[idx]))

    # output the match group to .log
    grpwriter = open('duplicate.log', 'w')
    result_duplicate_list = []
    for key in duphash.keys():
        ids = duphash[key]  # 获取每一个hash值对应的id列表
        # only the first one reserved
        removelist.extend(ids[1:])  # removelist保存的是只有相同hash值的除了第一个id的其他所有值，
        if len(ids) > 1:  # 如果同一个hash值的id数大于1，则将整个列表添加进去
            result_duplicate_list.append(ids)
        grplist.append(ids)

        grpwriter.write('ids:%s\n' % ' '.join([str(x) for x in ids]))
        # write the group of match
        for lineid in ids:
            grpwriter.write('%s\n' % data_v[lineid])

        grpwriter.write('==================\n')
    return result_duplicate_list
    # 相似性匹配暂时不考虑
    # find all pairs of match
    # print b, k
    # raw_input('test')
    # matches = simhash.find_all(data_h, b, k)
    #
    # marks = {}  # lineid -> groupid
    # grpindex = {}  # groupid -> [lineids]
    # groupid = 0
    #
    # for A, B in matches:
    #     grpidA, grpidB = -1, -1
    #     if index[A] in marks:
    #         grpidA = marks[index[A]]
    #     if index[B] in marks:
    #         grpidB = marks[index[B]]
    #     if grpidA == -1 and grpidB == -1:
    #         # new pair
    #         marks[index[A]] = groupid
    #         marks[index[B]] = groupid
    #         grpindex[groupid] = set([index[A], index[B]])
    #
    #         groupid += 1
    #     elif grpidA == -1:
    #         # add B to group A
    #         marks[index[A]] = grpidB
    #         grpindex[grpidB].add(index[A])
    #     elif grpidB == -1:
    #         marks[index[B]] = grpidA
    #         grpindex[grpidA].add(index[B])
    #     else:
    #         # merge two old groups
    #         for lid in grpindex[grpidB]:
    #             marks[lid] = grpidA
    #             grpindex[grpidA].add(lid)
    #         grpindex[grpidB].clear()
    #
    # # output the groups
    # # grpwriter = open(outfile + '.log', 'w')
    # linecntx = 0
    # for grp in grpindex.keys():
    #     if grpindex[grp]:
    #         ids = [lid for lid in grpindex[grp]]
    #         ids = sorted(ids, reverse=True)
    #
    #         linecntx += len(ids[1:])
    #         # output the first one
    #         removelist.extend(ids[1:])
    #         grplist.append(ids)
    #
    #         # output all
    #         grpwriter.write('ids:%s\n' % ids)
    #         # write the group of match
    #         for lineid in ids:
    #             grpwriter.write('%s' % data_v[lineid])
    #
    #         grpwriter.write('==================\n')
    #
    # # out put final result
    # remove = set(removelist)
    # for lid in range(linecnt):
    #     if lid not in remove and lid in data_v:
    #         writer.write('%s' % data_v[lid])
    #
    # # output the grplist
    # with open(outfile + '.grp', 'w') as grpf:
    #     for grp in grplist:
    #         if len(grp) > 1:
    #             grpf.write('%s\n' % ' '.join([str(x) for x in grp]))
    #         else:
    #             grpf.write('%s\n' % grp[0])
    #
    # reader.close()
    # writer.close()