#!/usr/bin/env python
# License: GPLv3 Copyright: 2020, Kovid Goyal <kovid at kovidgoyal.net>

import os
import re
import subprocess
import sys
from urllib.parse import quote_from_bytes

from .hrg import consume_process, write_hyperlink


def main() -> None:
    in_result: bytes = [b'']
    num_pat = re.compile(br' +--> (.+):(\d+):(\d+)')
    def line_handler(raw_line, clean_line, write):
        m = num_pat.match(clean_line)
        if m is not None:
            write_hyperlink(write, m.group(1), line=raw_line, frag=m.group(2))
        else:
            write(raw_line)

    cmdline = ['cargo', '--color=always'] + sys.argv[1:]
    try:
        p = subprocess.Popen(cmdline, stderr=subprocess.PIPE)
    except FileNotFoundError:
        raise SystemExit('Could not find the cargo executable in your PATH. Is it installed?')

    consume_process(p, p.stderr, line_handler)

if __name__ == '__main__':
    main()
