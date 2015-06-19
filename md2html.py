#!/usr/bin/env python2
# coding: utf8

from __future__ import unicode_literals
from __future__ import print_function

import re
import json
import misaka as m
import houdini as h
# from misaka import Markdown, HtmlRenderer, SmartyPants
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter


title_pattern = re.compile(u'^# .+\n')
tag_pattern = re.compile(
    u'(\n\u6807\u7b7e\uff08\u7a7a\u683c\u5206\u9694\uff09\uff1a)(.+)\n'
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
            return u'\n<pre><code>%s</code></pre>\n' % \
                h.escape_html(text.strip())

        lexer = get_lexer_by_name(lang, stripall=True)
        formatter = LineNoHtmlFormatter(
            style=u'github'
        )
        return highlight(text, lexer, formatter)


def getTags(md_file, parsed=None):
    tags = tag_pattern.match(md_file).group(2).split()
    if parsed:
        s = u''
        for t in tags:
            s = s + u'`' + t + u'` '
        return md2body(s)
    else:
        return tags


def md2body(text):
    text_rndr = BleepRenderer(flags=m.HTML_TOC)
    md = m.Markdown(
        text_rndr,
        extensions=m.EXT_NO_INTRA_EMPHASIS | m.EXT_FENCED_CODE | m.EXT_TABLES |
        m.EXT_LAX_HTML_BLOCKS | m.EXT_AUTOLINK
    )
    return md.render(text)


def md2toc(text):
    tocTree = m.html(
        text,
        extensions=m.EXT_NO_INTRA_EMPHASIS | m.EXT_FENCED_CODE,
        render_flags=m.HTML_SMARTYPANTS | m.HTML_TOC_TREE
    )
    tocTree = h.unescape_html(tocTree.encode('utf8'))

    return tocTree.decode('utf8')


def md2html(md_file):
    text = md_file.replace(title_pattern.match(md_file).group(), '')
    text = text.replace(tag_pattern.match(text).group(), '')

    return json.dumps({
        'tags': getTags(md_file, parsed=True),
        'toc': md2toc(text),
        'body': md2body(text)
    })


def mdInfo(md_file):
    title = title_pattern.match(md_file).group()
    tags = getTags(md_file)
    # summary =
    return json.dumps({'title': title, 'tags': tags})


if __name__ == '__main__':
    import sys
    from io import open
    mdFile = open(sys.argv[1], encoding='utf8')
    content = mdFile.read()
    html = md2html(content)
    toc = md2toc(content)
    print(toc)
    print(html)
    mdFile.close()
