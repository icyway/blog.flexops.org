#!/usr/bin/env python
# coding:utf8

import web
from webpy_jinja2 import render_template


urls = (
    '/', 'Index',
)
app = web.application(urls, globals())

navs = {
    '/': 'Home',
    '/about': 'About',
    '/contact': 'Contact Me'
}

config = {'wb_url': 'http://weibo.com/songvy'}
config['current'] = '/'


class Index:
    def GET(self):
        posts = [
            {'title': 'title', 'url': 'url', 'tag': 'tag', 'content': 'cntent'},
            {'title': 'title', 'url': 'url', 'tag': 'tag', 'content': 'content'}
        ]
        return render_template(
            'start.html', posts=posts, navs=navs, config=config
        )


if __name__ == '__main__':
    app.run()
