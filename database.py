# -*- coding: utf-8 -*- 
'''
Created on 2013

@author: catsky
'''
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Text
import setting


Base = declarative_base()


class ServerDB():
    def __init__(self):
        ServerDB.engine = None
        ServerDB.session = None

        if ServerDB.engine is None:
            ServerDB.engine = create_engine('mysql+mysqldb://%s:%s@%s:%s/%s?charset=utf8'
                                            %(setting.DBUSER, setting.DBPASSWORD,
                                              setting.HOSTNAME, setting.DBPORT,
                                              setting.DBNAME))
        Session = sessionmaker(bind=ServerDB.engine)
        if ServerDB.session is None:
            ServerDB.session = Session()

    def getSession(self):
        Base.metadata.create_all(ServerDB.engine)
        return ServerDB.session


class Queue(Base):
    __tablename__ = 'queue'
    id = Column(Integer, primary_key=True)
    url = Column(String(200))

    def __init__(self, url):
        self.url = url

    def __repr__(self):
        return "<Queue('%s')>" % (self.url)


class DuplCheckDB(Base):
    __tablename__ = 'duplcheckDB'
    id = Column(Integer, primary_key=True)
    url = Column(String(200))

    def __init__(self, url):
        self.url = url

    def __repr__(self):
        return "<DuplCheckDB('%s')>" % (self.url)


class Webpage(Base):
    __tablename__ = 'webpage'
    id = Column(Integer, primary_key=True)
    url = Column(String(200))
    html = Column(Text)

    category = Column(String(17))
    title = Column(String(100))
    content = Column(Text)
    comment_num = Column(Integer)
    closecomment = Column(Integer)
    tags = Column(String(100))
    password = Column(String(8))
    add_time = Column(Integer)
    edit_time = Column(Integer)
    shorten_content = Column(String(200))
    imgthumbnail = Column(String(200))
    post_type = Column(Integer)  # 1 for shown on top
    click_num = Column(Integer)  # 1 for shown on top
    editor_title = Column(String(100))

    def __init__(self, url=None, html=None, category=None, title=None,
                 content=None, comment_num=0, closecomment=0, tags=None,
                 password=None, shorten_content=None, imgthumbnail=None,
                 post_type=0, add_time=0, edit_time=0, click_num=0,
                 editor_title=None):
        self.url = url
        self.html = html
        self.category = category
        self.title = title
        self.content = content
        self.comment_num = comment_num
        self.closecomment = closecomment
        self.tags = tags
        self.password = password
        self.add_time = add_time
        self.edit_time = edit_time
        self.shorten_content = shorten_content
        self.imgthumbnail = imgthumbnail
        self.post_type = post_type
        self.click_num = click_num
        self.editor_title = editor_title

    def __repr__(self):
        return "<Webpage('%s','%s')>" % (self.url, self.html)


class OperatorDB:
    def __init__(self, serverDB=None):
        if serverDB is None:
            self.db = ServerDB()
        else:
            self.db = serverDB
        self.session = self.db.getSession()

    def add_seeds(self, links):
        new_links = []
        for link in links:
            if self.session.query(DuplCheckDB).filter_by(url=link).first() is None:
                new_links.append(link)

        for link in new_links:
            dc = DuplCheckDB(link)
            self.session.add(dc)

            queue = Queue(link)
            self.session.add(queue)

        self.session.commit()

    def pop_url(self):
        row = self.session.query(Queue).order_by("id").first()
        url = None
        if row is not None:
            print "in pop_url: row is not None. id: %s" % row.id
            url = row.url.strip()
            self.session.delete(row)
            self.session.commit()
            print "in pop_url: row is delted and commit"
        return url

    def html2db(self, url, html):
        webpage = Webpage(url, html)
        self.session.add(webpage)
        self.session.commit()

    def close(self):
        self.session.close()

if __name__ == '__main__':
    dbop = OperatorDB()
    dbop.add_seeds(["http://www.baidu.com", "http://sinaapp.com"])
