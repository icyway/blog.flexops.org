# coding: utf-8

import web
from os import path as os_path
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy import DateTime, Table, CHAR, Text, TIMESTAMP, func
from sqlalchemy.orm import scoped_session, sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base


basedir = os_path.abspath(os_path.dirname(__file__))
dbpath = 'sqlite:///' + os_path.join(basedir, 'flexops.db')

engine = create_engine(dbpath, echo=True)

Base = declarative_base()


class User(Base):
    __tablename__ = 't_user'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    fullname = Column(String)
    email = Column(String)
    passwd = Column(String)

    def __init__(self, name, fullname, passwd, email):
        self.name = name
        self.fullname = fullname
        self.passwd = passwd
        self.email = email

    def __repr__(self):
        return "<User('%s', '%s', '%s', '%s')>" % \
            (self.name, self.fullname, self.email, self.passwd)


t_tag = Table(
    't_tag', Base.metadata,
    Column('post_id', Integer, ForeignKey('t_posts.id')),
    Column('tag_id', Integer, ForeignKey('t_tags.id'))
)


class Post(Base):
    __tablename__ = 't_posts'

    id = Column(Integer, primary_key=True)
    tags = relationship('Tag', secondary=t_tag)
    title = Column(String)
    upload = Column(DateTime)
    modified = Column(DateTime)
    summary = Column(String)
    filename = Column(String)

    def __init__(self, title, filename, summary, upload, modified):
        self.title = title
        self.filename = filename
        self.summary = summary
        self.modified = modified
        self.upload = upload

    def __repr__(self):
        return "<Post('%s','%s','%s','%s')>" % \
            (self.title, self.filename, self.modified, self.upload)


class Tag(Base):
    __tablename__ = 't_tags'

    id = Column(Integer, primary_key=True)
    posts = relationship('Post', secondary=t_tag)
    name = Column(String)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "<Tag('%s')>" % (self.name)


class WebSession(Base):
    __tablename__ = 't_sessions'
    session_id = Column(CHAR(128), nullable=False, primary_key=True)
    atime = Column(TIMESTAMP, nullable=False, default=func.current_timestamp())
    data = Column(Text, nullable=True)

session_table = WebSession.__table__

sqlaSession = scoped_session(sessionmaker(bind=engine))


def load_sqla(handler):
    web.ctx.orm = sqlaSession
    try:
        return handler()
    except web.HTTPError:
        web.ctx.orm.commit()
        raise
    except:
        web.ctx.orm.rollback()
        raise
    finally:
        web.ctx.orm.commit()


if __name__ == '__main__':
    """
    http://blog.e3rp4y.me/2014/08/21/sqlalchemy-many-to-many-relationship.html
    """
    import sys
    from hashlib import md5
    metadata = Base.metadata
    if sys.argv[1] == '-c':
        metadata.create_all(engine)
        admin = User(
            name='flexops', passwd=md5('123456').hexdigest(),
            fullname=u'宋万伟', email=u'sww4718168@163.com'
        )
        sqlaSession.add(admin)
        sqlaSession.commit()
    elif sys.argv[1] == '-d':
        metadata.drop_all(engine)
