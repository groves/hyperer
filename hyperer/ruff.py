#!/usr/bin/env python
# License: GPLv3 Copyright: 2020, Kovid Goyal <kovid at kovidgoyal.net>
import os
import re
import subprocess
import sys
from . import make_hyperlink, consume_process

# ruff_check_raiser.py:7:1: E722 Do not use bare `except`
check_pat = re.compile(rb"^(.+):(\d+):(\d+): ")


def main(argv=sys.argv, write=None):
    output_altering_flags = set(["--output-format"])
    for arg in argv:
        if arg in output_altering_flags:
            raise SystemExit(
                f"hyperer-ruff relies on the output format of ruff and can't be used with the '{arg}' flag. Call ruff directly to use it."
            )

    def line_handler(write, raw_line, clean_line):
        if m := check_pat.match(clean_line):
            line_num = m.group(2)
            col_num = m.group(3)
            write(
                make_hyperlink(
                    m.group(1),
                    line=raw_line,
                    frag=line_num + b":" + col_num,
                    params={b"line": line_num, b"column": col_num},
                )
            )
        else:
            write(raw_line)

    env = os.environ.copy()
    env["CLICOLOR_FORCE"] = "1"
    cmdline = ["ruff"] + argv[1:]
    try:
        p = subprocess.Popen(cmdline, stdout=subprocess.PIPE, env=env)
    except FileNotFoundError:
        raise SystemExit(
            "Could not find the ruff executable in your PATH. Is ruff installed?"
        )

    return consume_process(p, line_handler, write)
