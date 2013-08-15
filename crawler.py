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
    rules = {'^(http://xkb\.com\.au)(.*)$': ['^(http:)//(xkb\.com\.au).*$']}
    mycrawler.add_rules(rules)
    mycrawler.start()
