#!/usr/bin/env python2
# coding: utf8

from __future__ import unicode_literals
from __future__ import print_function

import re
import misaka as m
# import houdini as h
# from misaka import Markdown, HtmlRenderer, SmartyPants
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter


title_pattern = re.compile(u'^# .+\n')
tag_pattern = re.compile(
    u'(\nTAGS: )(.+)\n'
)


# Class for add line number
class LineNoHtmlFormatter(HtmlFormatter):
    def wrap(self, source, outfile):
        return self._wrap_code(self._wrap_div(self._wrap_pre(source)))

    def _wrap_code(self, source):
        for i, t in source:
            if i == 1:
                # it's a line of formatted code
                t = '<span class="wrapLineNo"></span>' + t
            yield i, t


# Parse markdown to html
class BleepRenderer(m.HtmlRenderer, m.SmartyPants):

    def block_code(self, text, lang):
        if not lang:
            return u'\n<pre><code>%s</code></pre>\n' % text.strip()
            # h.escape_html(text.strip().deconde('utf-8'))

        lexer = get_lexer_by_name(lang, stripall=True)
        formatter = LineNoHtmlFormatter(
            style=u'github'
        )
        return highlight(text, lexer, formatter)

    def preprocess(self, text):
        if text.find(u'\n[TOC]') >= 0:
            return text.replace(u'\n[TOC]', u'\n' + md2toc(text))
        else:
            return text


def getTags(md_file, parsed=None):
    tags_re = tag_pattern.match(md_file)
    if tags_re:
        tags = tags_re.group(2).split()
    else:
        return None
    if parsed:
        s = u''
        for t in tags:
            s = s + u'`' + t + u'` '
        return md2body(s)
    else:
        return tags


def md2body(text):
    text_rndr = BleepRenderer(flags=m.HTML_TOC | m.HTML_HARD_WRAP)
    md = m.Markdown(
        text_rndr,
        # extensions=m.EXT_NO_INTRA_EMPHASIS | m.EXT_FENCED_CODE | m.EXT_TABLES
        extensions=m.EXT_FENCED_CODE | m.EXT_TABLES |
        m.EXT_LAX_HTML_BLOCKS | m.EXT_AUTOLINK
    )
    return md.render(text)


def md2toc(text):
    tocTree = m.html(
        text,
        extensions=m.EXT_NO_INTRA_EMPHASIS | m.EXT_FENCED_CODE,
        render_flags=m.HTML_SMARTYPANTS | m.HTML_TOC_TREE
    )
    # tocTree = h.unescape_html(tocTree.encode('utf8'))
    tocTree = tocTree.encode('utf8')

    return tocTree.decode('utf8')


def md2html(md_file):
    try:
        text = md_file.replace(title_pattern.match(md_file).group(), '')
        text = text.replace(tag_pattern.match(text).group(), '')
    except:
        pass

    return {
        'tags': getTags(md_file, parsed=True),
        'toc': md2toc(text),
        'body': md2body(text)
    }


def mdInfo(md_file):
    title_re = title_pattern.match(md_file)
    if title_re:
        title = title_pattern.match(md_file).group()
    else:
        title = None
    tags = getTags(md_file)
    return {'title': title, 'tags': tags}


if __name__ == '__main__':
    import sys
    from io import open
    mdFile = open(sys.argv[1], encoding='utf8')
    content = mdFile.read()
    result = md2html(content)
    print(result['toc'])
    print(result['body'])
    print(result['tags'])
    mdFile.close()
