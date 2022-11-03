#!/usr/bin/env python
# License: GPLv3 Copyright: 2020, Kovid Goyal <kovid at kovidgoyal.net>
import os
import re
import subprocess
import sys
from . import make_hyperlink, consume_process

def main(argv=sys.argv, write=None):
    if not sys.stdout.isatty() and '--pretty' not in argv and '-p' not in argv:
        os.execlp('rg', 'rg', *argv[1:])

    in_result: bytes = [b'']
    num_pat = re.compile(br'^(\d+):')
    def line_handler(write, raw_line, clean_line):
        if in_result[0]:
            m = num_pat.match(clean_line)
            if not clean_line:
                in_result[0] = b''
            elif m := num_pat.match(clean_line):
                write(make_hyperlink(in_result[0], raw_line, frag=m.group(1)))
                return
        elif raw_line.strip():
            in_result[0] = clean_line
        write(raw_line)

    cmdline = ['rg', '--pretty', '--with-filename'] + argv[1:]
    try:
        p = subprocess.Popen(cmdline, stdout=subprocess.PIPE)
    except FileNotFoundError:
        raise SystemExit('Could not find the rg executable in your PATH. Is ripgrep installed?')

    return consume_process(p, line_handler, write)
