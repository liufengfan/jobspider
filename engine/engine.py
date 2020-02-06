# -*- coding=utf-8 -*-

import sys

class AbstractEngine(object):

    def execute(self):
        '''
            abstract method
        '''
        print("execute is no operation.")
        pass
    
    @staticmethod
    def genpagenum(totalpage):
        for num in range(1, totalpage + 1):
            yield num 
