# -*- coding: utf-8 -*- 
import lxml.html    # python-lxml
import urlparse
import re
from lxml import etree
from StringIO import StringIO
from lxml.cssselect import CSSSelector


class WebPage:
    ###########################################
    #   WEBPAGE CONSTRUCTOR
    ###########################################
    def __init__(self, url, html):
        self.url = url
        self.html = html
        self.doc = lxml.html.fromstring(self.html)
        self.links = {}

    ###########################################
    #   extract the title/content/publishdate etc
    #   from the HTML
    ###########################################
    def extract(self):
        '''
        0. 澳洲2013/14总移民配额不变 技术移民减700
        1. 2013-06-26
        2. 18:02
        3. 来源：澳洲新快网
        4. 编辑：轩渺 
        5. 据澳洲论坛网报道，澳洲2013/14年度永久性移民配额将与上一个财年持平，为19万个。其中，在技术移民与家庭移民之间将微调700个配额。
                            在2013/1
        '''
        parser = etree.HTMLParser()
        tree = etree.parse(StringIO(self.html), parser)
        result = etree.tostring(tree.getroot(), pretty_print=True, method="html")
        #headline
        article = []
        sel = CSSSelector('div#top')
        for e in sel(tree.getroot()):
            for c in e.getchildren():
                for i in c.getchildren():
                    #print i.text
                    article.append(i.text.strip())
        #content
        sel = CSSSelector('div#mid')
        content = ""
        for e in sel(tree.getroot()):
            for c in e.getchildren():
                if c.text is not None:
                    #print c.text
                    content += c.text.strip() + "\n"
        article.append(content)
        return article

    #######################################
    # parsing links from html page
    #######################################
    def parse_links(self):
        for elem, attr, link, pos in self.doc.iterlinks():
            absolute = urlparse.urljoin(self.url, link.strip())
            #print ">>absolute:%s" %absolute
            #print elem.tag ,attr, absolute, pos
            if elem.tag in self.links:
                self.links[elem.tag].append(absolute)
            else:
                self.links[elem.tag] = [absolute]
        return self.links

    # filter links
    def filter_links(self,tags=[],str_patterns=[]):
        patterns = []
        for p in str_patterns:
            patterns.append(re.compile(p))

        filterlinks = []
        if len(tags)>0:
            for tag in tags:
                if tag in self.links:
                    for link in self.links[tag]:
                        if len(patterns) == 0:
                            pass
                            #filterlinks.append(link)
                        else:
                            for pattern in patterns:
                                if pattern.match(link)!=None:
                                    filterlinks.append(link)
                                    continue
                else:
                    continue
        else:
            for k,v in self.links.items():
                for link in v:
                    if len(patterns) == 0:
                        pass
                        #filterlinks.append(link)
                    else:
                        for pattern in patterns:
                            if pattern.match(link)!=None:
                                filterlinks.append(link)
                                continue

        return list(set(filterlinks))



    # form
    def get_form(self, index):
        form = self.doc.forms[index]
        form.action = urlparse.urljoin(self.url, form.action)
        return form.action, form.fields

    #
    def get_html(self):
        return self.html


if __name__ == "__main__":
    import time
    from downloader import DownloadManager
    downloader = DownloadManager()

    url = "http://xkb.com.au/html/immi/yimingonglue/"
    error_msg, url, redirected_url, html = downloader.download(url)
    #print error_msg, url, redirected_url, len(html)
    time.sleep(2)

    page = WebPage(url, html)
    page.parse_links()
    links = page.filter_links(tags=['a'], str_patterns = ['^(http://xkb\.com\.au).*'])

    elements = page.doc.findall('./body//div') 
#     for e in elements:
#         print "ELEMETNS =========================================="
#         print lxml.html.tostring(e,pretty_print=True)
#         print "ITEMS------------------------------------------"
#         print e.items()
#         print "TEXT-CONTENT-----------------------------------"
#         print e.text_content()
#         print "CLASSES-----------------------------------"
#         classes = e.find_class("NewsHeadline")
#         for c in classes:
#             lxml.html.tostring(c)
    
