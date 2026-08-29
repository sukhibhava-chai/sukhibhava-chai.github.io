#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate llms-full.txt — the whole page as plain markdown.

llms.txt is the summary; this is the full text, for answer engines that would
otherwise have to parse 70KB of Tailwind-classed markup to find six sentences.
Generated from index.html so it cannot drift out of date:

    python3 build/make-llms-full.py

Chrome and decoration are skipped: nav, the mobile drawer, the marquee, every
nav link list, and anything aria-hidden.
"""
import html
import io
import os
import re
from html.parser import HTMLParser

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC  = os.path.join(ROOT, 'index.html')
OUT  = os.path.join(ROOT, 'llms-full.txt')

SKIP_TAGS  = {'script', 'style', 'svg', 'head', 'noscript', 'nav'}
SKIP_IDS   = {'drawer', 'siteNav'}
BLOCK      = {'p', 'li', 'h1', 'h2', 'h3', 'h4', 'dt', 'dd', 'summary', 'td', 'th', 'caption'}


class Extract(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.out, self.buf = [], []
        self.depth_skip = 0
        self.stack = []
        self.tag = None
        self.row, self.table, self.in_table = [], [], False

    # -- helpers ------------------------------------------------------------
    def flush(self):
        text = re.sub(r'\s+', ' ', ''.join(self.buf)).strip()
        self.buf = []
        if not text:
            return
        t = self.tag
        if self.in_table:
            if t == 'caption':
                self.out.append('\n**%s**\n' % text)
            elif t in ('td', 'th'):
                self.row.append(text)
            return
        if t == 'h1':      self.out.append('# %s\n' % text)
        elif t == 'h2':    self.out.append('\n## %s\n' % text)
        elif t in ('h3', 'summary'): self.out.append('\n### %s\n' % text)
        elif t == 'li':    self.out.append('- %s' % text)
        elif t == 'dt':    self.out.append('- **%s**: ' % text)
        elif t == 'dd':
            if self.out and self.out[-1].endswith(': '):
                self.out[-1] += text
            else:
                self.out.append('- %s' % text)
        else:              self.out.append(text)

    # -- parser hooks -------------------------------------------------------
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag in SKIP_TAGS or a.get('id') in SKIP_IDS or 'aria-hidden' in a:
            self.depth_skip += 1
            self.stack.append(('skip', tag))
            return
        self.stack.append(('keep', tag))
        if self.depth_skip:
            return
        if tag == 'table':
            self.in_table, self.table = True, []
        if tag == 'tr':
            self.row = []
        if tag in BLOCK:
            self.buf, self.tag = [], tag

    def handle_endtag(self, tag):
        while self.stack:
            kind, t = self.stack.pop()
            if kind == 'skip':
                self.depth_skip -= 1
            if t == tag:
                break
        if self.depth_skip:
            return
        if tag in BLOCK:
            self.flush()
            self.tag = None
        if tag == 'tr' and self.row:
            self.table.append(self.row)
            self.row = []
        if tag == 'table':
            if self.table:
                w = max(len(r) for r in self.table)
                rows = [r + [''] * (w - len(r)) for r in self.table]
                # The page's tables are row-header tables with no <thead>, so a
                # generic header keeps the markdown valid without inventing labels.
                self.out.append('| ' + ' | '.join(['Fact', 'Value'][:w]
                                                  + [''] * max(0, w - 2)) + ' |')
                self.out.append('|' + '---|' * w)
                for r in rows:
                    self.out.append('| ' + ' | '.join(r) + ' |')
                self.out.append('')
            self.in_table, self.table = False, []

    def handle_data(self, data):
        if not self.depth_skip and self.tag:
            self.buf.append(data)


src = io.open(SRC, encoding='utf-8').read()
body = src[src.index('<body'):]

p = Extract()
p.feed(body)

lines, prev_blank = [], True
for chunk in p.out:
    for line in chunk.split('\n'):
        blank = not line.strip()
        if blank and prev_blank:
            continue
        lines.append(line.rstrip())
        prev_blank = blank

header = (
 '# Hyderabadi Amruttulya — full page text\n'
 '\n'
 '> The complete text of https://hyderabadiamruttulya.com/ as markdown. Generated from\n'
 '> the page itself, so it always matches what is published. The short fact sheet is at\n'
 '> https://hyderabadiamruttulya.com/llms.txt, which also lists what is deliberately NOT\n'
 '> published and should not be inferred.\n'
 '\n'
 '---\n\n'
)

io.open(OUT, 'w', encoding='utf-8').write(header + '\n'.join(lines).strip() + '\n')
print('wrote %s (%d bytes)' % (OUT, os.path.getsize(OUT)))
