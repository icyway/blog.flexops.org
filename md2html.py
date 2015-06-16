#!/usr/bin/env python2
# coding: utf8

import misaka as m
import houdini as h
from jinja2 import Markup
from misaka import Markdown, HtmlRenderer, SmartyPants
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter


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
class BleepRenderer(HtmlRenderer, SmartyPants):

    def block_code(self, text, lang):
        if not lang:
            return '\n<pre><code>%s</code></pre>\n' % \
                h.escape_html(text.strip())

        lexer = get_lexer_by_name(lang, stripall=True)
        formatter = LineNoHtmlFormatter(
            # linenos='inline',
            style='github'
            # linenostart=1
        )
        return highlight(text, lexer, formatter)

    def preprocess(self, text):
        for line in text:
            line


text_rndr = BleepRenderer(flags=m.HTML_TOC)
md = Markdown(
    text_rndr,
    extensions=m.EXT_NO_INTRA_EMPHASIS | m.EXT_FENCED_CODE | m.EXT_AUTOLINK |
    m.EXT_LAX_HTML_BLOCKS | m.EXT_TABLES
)


def md2html(md_file):
    return md.render(md_file)


def md2html_toc(md_file):
    tocTree = m.html(
        md_file,
        extensions=m.EXT_NO_INTRA_EMPHASIS | m.EXT_FENCED_CODE,
        render_flags=m.HTML_SMARTYPANTS|m.HTML_TOC_TREE
    )
    tocTree = Markup(tocTree).unescape()

    return tocTree, md.render(md_file)


if __name__ == '__main__':
    import sys
    import codecs
    mdFile = codecs.open(sys.argv[1], mode='r', encoding='utf-8')
    content = mdFile.read()
    mdFile.close()
    print md.render(content)
