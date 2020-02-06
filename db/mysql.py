# -*- coding=utf-8 -*-
from queue import Queue
from pymysql import connect

class MySQLTool(object):
    """mysql 操作工具"""

    def __init__(self, **kwargs):
        self.records = Queue(maxsize=10000)
        self.connect = connect(**kwargs)
        print(self.connect)

    def addData(self, data):
        self.records.put(data)

