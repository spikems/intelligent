# encoding:utf-8
import sys


class DiDiNoiseRule:
    def __init__(self):
        self.abst = ''

    def rule1(self):
        # rule 1: 摘要中仅含有滴滴、滴[表情]滴滴、滴滴？？、滴滴！的为噪音数据
        fuhaos = ['～', '?', ',', '，', '[', '？', '。', '...', '~', '~', '!', '！']
        if len(self.abst) > 100:
            return False

        if self.abst == '滴滴':
            return True
        for fuhao in fuhaos:
            zaoyin = '滴滴%s' % (fuhao)
            if self.abst.startswith(zaoyin):
                return True

        return False

    def rule2(self):
        # rule2 开头为的数据为噪音数据
        fuhaos = ['滴滴//', '滴滴http://', '滴滴！//', '滴滴？//', '滴滴#']
        for fuhao in fuhaos:
            if self.abst.startswith(fuhao):
                return True
        return False

    def rule3(self):
        # rule3 结尾为滴滴、滴滴？或滴滴http://为噪音数据
        fuhaos = ['滴滴', '滴滴？', '滴滴http://']
        for fuhao in fuhaos:
            if self.abst.endswith(fuhao):
                return True
        return False

    def run(self, abst):
        self.abst = abst.strip().replace(' ', '')
        fs = dir(DiDiNoiseRule)
        bResult = False
        for fname in fs:
            if fname.find('rule') == -1:
                continue
            bResult = getattr(self, fname)()
            if bResult:
                return bResult, fname

        return False, ""


if __name__ == '__main__':
    di = DiDiNoiseRule()
    print di.run('滴滴 ... 滴，滴滴 ... 滴，滴滴～')
    with open('sample1.txt', 'r') as fr:
        for line in fr:
            print line.strip() + "\t" + str(di.run(line))
