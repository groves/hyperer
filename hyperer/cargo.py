import re
import subprocess
import sys
from . import consume_process, make_hyperlink

def main(argv=sys.argv, write=None) -> None:
    # right: `0`', src/main.rs:1012:9
    assert_pat = re.compile(br' +(?:left|right):.+ (.+):(\d+):(\d+)')
    # at /build/rustc-1.63.0-src/library/core/src/panicking.rs:181:5
    btrace_pat = re.compile(br' +at (.+):(\d+):(\d+)')
    num_pat = re.compile(br' +--> (.+):(\d+):(\d+)')
    def line_handler(write, raw_line, clean_line):
        for pat in [assert_pat, btrace_pat, num_pat]:
            if m := pat.match(clean_line):
                line_num = m.group(2)
                col_num = m.group(3)
                write(make_hyperlink(m.group(1), line=raw_line,
                    frag=line_num + b':' + col_num, 
                    params={b'line': line_num, b'column': col_num}))
                return
        write(raw_line)

    cmdline = ['cargo'] + argv[1:]
    try:
        # Capture both stdout and stderr as rustc uses stderr
        p = subprocess.Popen(cmdline, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    except FileNotFoundError:
        raise SystemExit('Could not find the cargo executable in your PATH. Is it installed?')

    return consume_process(p, line_handler, write)
