# -*- coding=utf-8 -*-

from .engine import AbstractEngine
from ..model import JobModel

import threading
from threading import Thread
import requests
from bs4 import BeautifulSoup
from queue import Queue
import uuid 
from pymysql import connect
import pymysql

def my_uuid():
    return str(uuid.uuid1()).replace('-', '')

counter_lock2 = threading.Lock()

class Job51Engine(AbstractEngine):
    """51job 爬虫"""

    def __init__(self, **kwargs):
        self.name = kwargs['name']
        self.rawurl = kwargs['url']
        self.keywords =  "%2520" if kwargs['keywords'] == "" else kwargs['keywords']
        self.pagenum = kwargs['pagenum']

        self.url = self.rawurl.format(keywords=self.keywords, pagenum=self.pagenum)        
        self.hrefQueue = Queue(maxsize=5000)
        self.jobinfothreads = []
        self.joblisthreads = []
        self.totalpage = 0
        self.connection = connect(
            host='localhost',
            user='root',
            password='123456',
            db='jobinfo',
            charset='utf8'
        )
        self.cursor = self.connection.cursor()
        self.templatesql = "INSERT INTO jobinfo (jid ,jurl ,jpost ,jsalary ,jcompany ,jsummary ,jpostinfo ,jconcatinfo ,jsource) VALUES ( '{jid}','{jurl}','{jpost}','{jsalary}','{jcompany}','{jsummary}', '{jpostinfo}','{jconcatinfo}','{jsource}' )"
    
    def execute(self):
        print("51job 爬虫启动...")
        indexpage = self._gethtmlpage(url=self.url, encoding='gbk')
        # 获取总页数
        self.totalpage = indexpage.select("#hidTotalPage")[0].attrs['value']
        # self.totalpage = 1
        self.__pagenum = self.genpagenum(int(self.totalpage))
            
        self._inithreads(self.joblisthreads, self._getjoblist)
        self._starthreads(self.joblisthreads)
        self._jointhreads(self.joblisthreads)

        print(self.hrefQueue.qsize())

        self._inithreads(self.jobinfothreads, self._getJobInfo)
        self._starthreads(self.jobinfothreads)
        self._jointhreads(self.jobinfothreads)

        print("51job 爬虫结束...")

    def _gethtmlpage(self, url, encoding='utf-8'):
        """
            通过url获取列表页面
            返回 BeautifulSoup 对象
        """
        response = requests.get(url)
        if 200 != response.status_code:
            BeautifulSoup("", 'lxml')
        response.encoding = encoding
        return BeautifulSoup(response.text, 'lxml')

    def _getJobInfo(self):
        """获取职位详情信息"""
        while True:
            if self.hrefQueue.empty():
                break
            jobinfourl = self.hrefQueue.get()
            # print("thread name {} : get href is {}".format(threading.currentThread().getName() ,jobinfourl))
            infopage = self._gethtmlpage(jobinfourl, 'gbk')
            try:
                company_center = infopage.select("div.tCompany_center.clearfix")[0]
                header = company_center.select("div.tHeader.tHjob")[0]
                company_main = company_center.select("div.tCompany_main")[0]
            except IndexError as identifier:
                break
            
            tBorderTop_boxs = company_main.select("div.tBorderTop_box")

            # 职位信息
            postInfo = tBorderTop_boxs[0]
            # 联系方式
            contactInfo = tBorderTop_boxs[1]

            # print(("=" * 30) + ">")
            # print("url: " + jobinfourl)
            # print("职位: " + header.select("div.cn h1")[0].attrs['title'])
            # print("薪资: " + header.select("div.cn strong")[0].text)
            # print("公司: " + header.select("div.cn p.cname a.catn")[0].attrs['title'])
            # print("摘要信息: " + header.select("div.cn p.msg.ltype")[0].attrs['title'])
            # print("职位信息: " + self._pinjiezhiweixinxi(postInfo.select("div.bmsg.job_msg.inbox > p")))
            # print("联系方式: " + contactInfo.select("div.bmsg.inbox > p.fp")[0].text)
            # print(("=" * 30) + "<")

            # job = JobModel()
            # job.juid = uuid()
            # job.url = jobinfourl
            # job.post = header.select("div.cn h1")[0].attrs['title']
            # job.salary = header.select("div.cn strong")[0].text
            # job.company = header.select("div.cn p.cname a.catn")[0].attrs['title']
            # job.summary = header.select("div.cn p.msg.ltype")[0].attrs['title']
            # job.postinfo = self._pinjiezhiweixinxi(postInfo.select("div.bmsg.job_msg.inbox > p"))
            # job.concatinfo = contactInfo.select("div.bmsg.inbox > p.fp")[0].text
            # job.source = 'http://www.51job.com'
            tempsql = self.templatesql.format(
                jid            = my_uuid(),
                jurl           = jobinfourl,
                jpost          = self._getjpost(header),
                jsalary        = self._getjsalary(header),
                jcompany       = self._getjcompany(header),
                jsummary       = self._getjsummary(header),
                jpostinfo      = str(self._pinjiezhiweixinxi(postInfo.select("div.bmsg.job_msg.inbox > p"))),
                jconcatinfo    = self._getconcatinfo(contactInfo),
                jsource        = 'http://www.51job.com'
            )

            counter_lock2.acquire()
            self.cursor.execute(tempsql)
            self.connection.commit()
            counter_lock2.release()

        # print("thread name {} : is exit.".format(threading.currentThread().getName()))
    def _getjsummary(self, header):
        try:
            return str(header.select("div.cn p.msg.ltype")[0].attrs['title'])
        except IndexError as identifier:
            return ""

    def _getjcompany(self, header):
        try:
            return str(header.select("div.cn p.cname a.catn")[0].attrs['title'])
        except IndexError as identifier:
            return ""

    def _getjsalary(self, header):
        try:
            return str(header.select("div.cn strong")[0].text)
        except IndexError as identifier:
            return ""

    def _getjpost(self, header):
        try:
            return str(header.select("div.cn h1")[0].attrs['title'])
        except IndexError as identifier:
            return ""

    def _getconcatinfo(self, element):
        try:
            return str(element.select("div.bmsg.inbox > p.fp")[0].text)
        except IndexError as identifier:
            return ""

    def _pinjiezhiweixinxi(self, resultset):
        result = []
        for temp in resultset:
            result.append("\n")
            result.append(str(temp.text).replace("'",""))
        return "".join(result)

    def _getjoblist(self):
        """获取职位列表"""
        while True:
            try:
                pagenum = next(self.__pagenum)
                # print("thread name {} : pagenum is {}".format(threading.currentThread().getName() , pagenum))
                listpage = self._gethtmlpage(
                    url=self.rawurl.format(
                        keywords=self.keywords, 
                        pagenum = pagenum
                    ),
                    encoding='gbk'
                )
                self._parserListpage(listpage)
            except StopIteration:
                break
        # print("thread name {} is exit.".format(threading.currentThread().getName()))

    def _parserListpage(self, listpage):
        table = listpage.select("div#resultList.dw_table div.el p.t1 span a")
        for item in table:
            self.hrefQueue.put(item.attrs['href'])
   
    def _inithreads(self, threadlist, target, threadsize=10):
        for i in range(threadsize):
            work = Thread(target=target, name=('job thread %s' % i))
            threadlist.append(work)

    def _starthreads(self, threads):
        for work in threads:
            work.start()

    def _jointhreads(self, threads):
        for work in threads:
            work.join()

