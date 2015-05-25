#!/usr/bin/env python2
# coding: utf8

import misaka as m
import houdini as h
from misaka import Markdown, HtmlRenderer, SmartyPants
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter


# Parse markdown to html
class BleepRenderer(HtmlRenderer, SmartyPants):

    def block_code(self, text, lang):
        if not lang:
            return '\n<pre><code>%s</code></pre>\n' % \
                h.escape_html(text.strip())

        lexer = get_lexer_by_name(lang, stripall=True)
        formatter = HtmlFormatter(style='solarizedlight')
        return highlight(text, lexer, formatter)


renderer = BleepRenderer()
md = Markdown(
    renderer,
    extensions=m.EXT_NO_INTRA_EMPHASIS | m.EXT_FENCED_CODE | m.EXT_AUTOLINK |
    m.EXT_LAX_HTML_BLOCKS | m.EXT_TABLES
)


def md2html(md_file):
    return md.render(md_file)


if __name__ == '__main__':
    import sys
    import codecs
    mdFile = codecs.open(sys.argv[1], mode='r', encoding='utf-8')
    content = mdFile.read()
    mdFile.close()
    print md.render(content)
