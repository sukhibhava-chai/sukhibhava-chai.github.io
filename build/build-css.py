#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Compile the stylesheet and splice it into index.html.

    python3 build/build-css.py

Run this after adding or changing any Tailwind class in index.html, otherwise
the new class has no CSS behind it. The theme lives in tailwind.config.js.
Pinned to Tailwind 3: the page uses v3 comma syntax in arbitrary grid values
(`lg:grid-cols-[1.1fr,.9fr]`), which v4 rejects.
"""
import io
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT  = os.path.join(ROOT, 'build', 'output.css')

subprocess.check_call([
    'npx', '-y', 'tailwindcss@3.4.17',
    '-c', os.path.join(ROOT, 'tailwind.config.js'),
    '-i', os.path.join(ROOT, 'build', 'input.css'),
    '-o', OUT, '--minify',
], cwd=ROOT)

css  = io.open(OUT, encoding='utf-8').read().strip()
page = os.path.join(ROOT, 'index.html')
s    = io.open(page, encoding='utf-8').read()

new, n = re.subn(r'/\* tw:start \*/.*?/\* tw:end \*/',
                 lambda _: '/* tw:start */' + css + '/* tw:end */',
                 s, flags=re.S)
if n != 1:
    sys.exit('expected exactly one tw:start/tw:end block in index.html, found %d' % n)

io.open(page, 'w', encoding='utf-8').write(new)
print('inlined %d bytes of CSS into index.html' % len(css))
