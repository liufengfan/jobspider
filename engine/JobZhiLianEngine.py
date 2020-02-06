# -*- coding=utf-8 -*-

from .engine import AbstractEngine

class JobZhiLianEngine(AbstractEngine):
    '''
        智联招聘 爬虫
    '''
    
    def execute(self):
        print("51job 爬虫启动...")
