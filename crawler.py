# -*- coding: utf-8 -*-
'''
Created on 2013

@author: catsky
'''
import sys
import re
import time
from database import OperatorDB
from downloader import DownloadManager
from webpage import WebPage


class Crawler():
    def __init__(self):
        self.downloader = DownloadManager()
        self.webpage = None
        self.rules = {}
        self.dbop = OperatorDB()

    def add_seeds(self, links):
        self.dbop.add_seeds(links)

    def add_rules(self, rules):
        self.rules = {}
        for url, inurls in rules.items():
            reurl = re.compile(url)
            repatn = []
            for u in inurls:
                repatn.append(re.compile(u))
            self.rules[reurl] = repatn

    def get_patterns_from_rules(self, url):
        patns = []
        for purl, ru in self.rules.items():
            if purl.match(url) != None:
                patns.extend(ru)
        return list(set(patns))

    def start(self):
        while 1:
            try:
                url = self.dbop.pop_url()
                print "url: %s" % url
                if url == None:
                    print "crawling task is done."
                    break
                error_msg, url, redirected_url, html = self.downloader.download(url)
                #print error_msg, url, redirected_url, html
                if html != None:
                    self.dbop.html2db(url, html)
    
                    self.webpage = WebPage(url, html)
                    print self.webpage.parse_links()
                    ruptn = self.get_patterns_from_rules(url)
                    links = self.webpage.filter_links(tags = ['a'], str_patterns = ruptn)
                    self.add_seeds(links)
                self.mysleep(3)
            except Exception, err:
                print "!!error!! Exception happend! %s" % url
                self.dbop.close()

    def mysleep(self, n):
        for i in range(n):
            time.sleep(1)
            print "sleep", i, "of", n


if __name__ == "__main__":
    mycrawler = Crawler()
    mycrawler.add_seeds(['http://xkb.com.au/html/immi/yimingonglue/'])
    rules = {'^(http://xkb\.com\.au)(.*)$':
             ['^(http:)//(xkb\.com\.au)/html/immi/yimingonglue/2013/\d+/\d+.*html$',
              '^(http:)//(xkb\.com\.au)/html/immi/zhiyezhilu/2013/\d+/\d+.*html$',
              '^(http:)//(xkb\.com\.au)/html/immi/renzaiaozhou/2013/\d+/\d+.*html$',
              '^(http:)//(xkb\.com\.au)/html/immi/shenghuozixun/2013/\d+/\d+.*html$',
              ]}
#     http://xkb.com.au/html/immi/yimingonglue/2013/0811/109468.html
#     http://xkb.com.au/html/immi/zhiyezhilu/2013/0701/106708.html
#     http://xkb.com.au/html/immi/renzaiaozhou/2013/0814/109694.html
#     http://xkb.com.au/html/immi/shenghuozixun/2013/0725/108398.html
#     http://xkb.com.au/html/news/shehui/2013/0815/109762.html
#     http://xkb.com.au/html/news/aozhoushizheng/2013/0815/109798.html
#     http://xkb.com.au/html/news/aozhoucaijing/2013/0815/109789.html
#     http://xkb.com.au/html/study/news/2013/0815/109775.html
#     http://xkb.com.au/html/study/focus/2013/0730/108719.html
#     http://xkb.com.au/html/study/life/2013/0731/108778.html
#     http://xkb.com.au/html/study/job/2013/0717/107852.html
#     http://xkb.com.au/html/life/wanleaozhou/2013/0812/109520.html
#     http://xkb.com.au/html/life/meiweiaozhou/2013/0815/109790.html
#     http://xkb.com.au/html/life/pinweiaozhou/2013/0814/109713.html
#     http://xkb.com.au/html/life/wodelehuo/2013/0807/109199.html

    mycrawler.add_rules(rules)
    mycrawler.start()
