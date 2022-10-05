#!/usr/bin/env python
# License: GPLv3 Copyright: 2020, Kovid Goyal <kovid at kovidgoyal.net>

import os
import re
import subprocess
import sys
from urllib.parse import quote_from_bytes

from .hrg import consume_process, write_hyperlink


def main() -> None:
    # right: `0`', src/main.rs:1012:9
    assert_pat = re.compile(br' +(?:left|right):.+ (.+):(\d+):(\d+)')
    # at /build/rustc-1.63.0-src/library/core/src/panicking.rs:181:5
    btrace_pat = re.compile(br' +at (.+):(\d+):(\d+)')
    num_pat = re.compile(br' +--> (.+):(\d+):(\d+)')
    def line_handler(write, raw_line, clean_line):
        for pat in [assert_pat, btrace_pat, num_pat]:
            if m := pat.match(clean_line):
                write_hyperlink(write, m.group(1), line=raw_line, frag=m.group(2))
                return
        write(raw_line)

    cmdline = ['cargo'] + sys.argv[1:]
    try:
        # Capture both stdout and stderr as rustc uses stderr
        p = subprocess.Popen(cmdline, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    except FileNotFoundError:
        raise SystemExit('Could not find the cargo executable in your PATH. Is it installed?')

    consume_process(p, line_handler)

if __name__ == '__main__':
    main()
