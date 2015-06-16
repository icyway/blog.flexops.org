#!/usr/bin/env python
# coding:utf8

import os
import web
import json
import codecs
from hashlib import md5
from md2html import md2html, md2html_toc
from datetime import datetime
from config import configs, urls
from utils import SQLAStore
from models import Post, Tag, User, WebSession, load_sqla
from webpy_jinja2 import render_template, context_processor

web.config.debug = False

app = web.application(urls, globals())
app.add_processor(load_sqla)

# session_db = web.database(dbn="sqlite", db='session.db')
# store = web.session.DBStore(session_db, 'sessions')
# session = web.session.Session(
#     app,
#     store,
#     initializer={'logined': 0}
# )
# session.logined = 0

web.config.session_parameters['cookie_name'] = 'sid'
web.config.session_parameters['timeout'] = 600
web.config.session_parameters['ignore_expiry'] = True
web.config.session_parameters['ignore_change_ip'] = False
web.config.session_parameters['expired_message'] = 'Session expired'

session = web.session.Session(app, SQLAStore(WebSession))


def checkLogged():
    if session.get('logined', 0) == 0:
        return False
    else:
        return True


@context_processor
def getNavs():
    return {'navs': configs['navs']}


@context_processor
def getConfigs():
    return {'config': configs}


@context_processor
def getTags():
    tags = web.ctx.orm.query(Tag).all()
    return {'tags': tags}


@context_processor
def addMarkdown():
    return {'markdown': md2html}


class Home:
    def GET(self):
        postsQuery = web.ctx.orm.query(Post).order_by('modified desc')
        page = web.input(page=1).page-1
        pageSize = web.input(pageSize=10).pageSize
        if page > 1:
            posts = postsQuery.offset(page*pageSize).limit(pageSize).all()
        else:
            posts = postsQuery.limit(pageSize).all()
        return render_template(
            'start.html', posts=posts
        )


class Views:
    def GET(self, postId):
        post = web.ctx.orm.query(Post).filter_by(id=postId).first()
        if post:
            f = os.path.join('articles', post.filename)
        else:
            raise web.NotFound

        try:
            mdFile = codecs.open(f, mode='r', encoding='utf-8')
            content = mdFile.read()
            toc, html = md2html_toc(content)
            mdFile.close()
        except:
            mdFile.close()
            raise web.seeother('/')
        # html = md2html('articles/' + post.filename)
        return render_template('view.html', toc=toc, html=html, post=post)


class GetTags:
    def GET(self, tag):
        posts = web.ctx.orm.query(Tag).filter_by(name=tag).first()

        return render_template(
            'tags.html', posts=posts
        )


class About:
    def GET(self):
        return render_template('about.html')


class Admin:
    def GET(self):
        if checkLogged():
            postsQuery = web.ctx.orm.query(Post).order_by('modified desc')
            posts = postsQuery.all()
            return render_template('admin.html', posts=posts)
        else:
            print 'Failed'
            raise web.seeother('/login')

    def POST(self):
        pass


class Login:
    def GET(self):
        return render_template('login.html')

    def POST(self):
        # if checkLogin():
        user = web.input().username
        passwd = web.input().passwd
        passwd = md5(passwd).hexdigest()
        check = web.ctx.orm.query(User).filter_by(
            name=user, passwd=passwd
        ).first()
        if check and passwd == check.passwd:
            session.logined = 1
            session.user = user
            raise web.seeother('/server')
        else:
            session.logined = 0
            raise web.seeother('/login')


class AddPost:
    def POST(self):
        title = web.input().title
        tags = web.input().tags.split()
        mdName = web.input().filename
        mdSummary = web.input().summary
        fileSrc = web.input().mdfile

        newPost = Post(
            title=title,
            upload=datetime.now(),
            modified=datetime.now(),
            summary=mdSummary,
            filename=mdName
        )
        web.ctx.orm.add(newPost)
        web.ctx.orm.flush()

        for tag in tags:
            checkTag = web.ctx.orm.query(Tag).filter_by(name=tag).all()
            if not checkTag:
                newTags = Tag(name=tag)
                web.ctx.orm.add(newTags)
                web.ctx.orm.flush()

            newPost.tags.append(newTags)

        fout = open('articles/'+mdName, 'w')
        fout.write(fileSrc)
        fout.close()
        return json.dumps({
            'success': True
        })


class EditPosts:
    def GET(self, id):
        return json.dumps({
            'success': True,
            'action': 'action'
        })


if __name__ == '__main__':
    app.run()

application = app.wsgifunc()
