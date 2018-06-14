#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
    A Classifier to filter general words
'''

from intelligent.model.t_general_word import TGeneralWord


class GeneralWordFilter:
    
    def __init__(self):
                 
        self.oTGW = TGeneralWord()
        self.dGeneralWords = {}
        self.__loaddata()

    def __loaddata(self):
        
        lGeneralList = self.oTGW.queryAll()
        for item in lGeneralList:
            self.dGeneralWords[item['name'].strip()] = 1
        

    def filter(self, words):

        '''
             input :  words
             output : dealed words without generalword

 
        '''
        result = []
        for word in words:
            if not word in dGeneralWords:
                result.append(word)

        return result

    def isGeneralWord(self, word) :
        if word in self.dGeneralWords:
            return True
        return False

#print GeneralWordFilter().isGeneralWord('落实') 


