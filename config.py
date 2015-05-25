# coding: utf-8

configs = {
    'wb_url': 'http://weibo.com/songvy',
    'current': '/',
    'navs': {
        'Home': '/',
        'Archives': '/archive',
        'About': '/about',
        'Contact Me': 'http://weibo.com/songvy'
    }
}

urls = (
    '/', 'Home',
    '/about', 'About',
    '/server', 'Admin',
    '/addPost', 'AddPost',
    '/tags', 'GetTags',
    '/login', 'Login',
    '/archives', 'Archives',
    '/article/(.*)', 'GetTags',
    '/views/([0-9]+)', 'Views',
    '/archive/(.*)', 'Archive',
    '/editPosts/(.*)', 'EditPosts',
)


def getNavItems(app):
    def nav(navs=[], superUser=None):
        for eachUri, relativeClass in app.mapping:
            if eachUri in navs:
                yield relativeClass
    return nav


def urlFor(app):
    def urlIs(realClass):
        for eachUri, relativeClass in app.mapping:
            if realClass == relativeClass:
                return eachUri
    return urlIs

if __name__ == '__main__':
    pass
