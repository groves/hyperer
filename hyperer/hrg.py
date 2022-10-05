#!/usr/bin/env python
# License: GPLv3 Copyright: 2020, Kovid Goyal <kovid at kovidgoyal.net>

import functools
import os
import re
import signal
import socket
import subprocess
import sys
from typing import Callable, cast
from urllib.parse import quote_from_bytes


@functools.cache
def hostname():
    return socket.gethostname().encode('utf-8')
    
def write_hyperlink(write: Callable[[bytes], None], path: str, line: bytes, frag: bytes = b'') -> None:
    path = quote_from_bytes(os.path.abspath(path)).encode('utf-8')
    text = b'\033]8;;file://' + hostname() + path
    if frag:
        text += b'#' + frag
    text += b'\033\\' + line + b'\033]8;;\033\\'
    write(text)


def consume_process(p, line_handler):
    def write(b):
        sys.stdout.buffer.write(b)
        # If we're in a pipe, we'll not have a tty and be block buffered
        # Flush to avoid that.
        # Can't easily turn off block buffering from inside the program
        # https://stackoverflow.com/questions/881696/unbuffered-stdout-in-python-as-in-python-u-from-within-the-program
        sys.stdout.buffer.flush()
    sgr_pat = re.compile(br'\x1b\[.*?m')
    osc_pat = re.compile(b'\x1b\\].*?\x1b\\\\')
    try:
        for line in p.stdout:
            line = osc_pat.sub(b'', line)  # remove any existing hyperlinks
            clean_line = sgr_pat.sub(b'', line).rstrip()  # remove SGR formatting
            line_handler(write, line, clean_line)
    except KeyboardInterrupt:
        p.send_signal(signal.SIGINT)
    except (EOFError, BrokenPipeError):
        pass
    finally:
        try:
            stream.close()
        except:
            pass
    raise SystemExit(p.wait())

def main() -> None:
    i = 1
    all_link_options = ['matching_lines', 'context_lines', 'file_headers']
    link_options = set()
    while i < len(sys.argv):
        if sys.argv[i] == '--kitten':
            if len(sys.argv) < i + 2 or not sys.argv[i + 1].startswith("hyperlink="):
                raise SystemExit("--kitten argument must be followed by hyperlink=(all|matching_lines|context_lines|file_headers)")
            for option in sys.argv[i + 1].split('=')[1].split(','):
                if option == 'all':
                    link_options.update(all_link_options)
                elif option not in all_link_options:
                    raise SystemExit(f"hyperlink option must be one of all, matching_lines, context_lines, or file_headers, not '{option}'")
                else:
                    link_options.add(option)
            del sys.argv[i:i+2]
        else:
            i += 1
    if len(link_options) == 0: # Default to linking everything if no options given
        link_options.update(all_link_options)
    link_file_headers = 'file_headers' in link_options
    link_context_lines = 'context_lines' in link_options
    link_matching_lines = 'matching_lines' in link_options

    if not sys.stdout.isatty() and '--pretty' not in sys.argv and '-p' not in sys.argv:
        os.execlp('rg', 'rg', *sys.argv[1:])

    in_result: bytes = [b'']
    num_pat = re.compile(br'^(\d+)([:-])')
    def line_handler(write, raw_line, clean_line):
        if in_result[0]:
            m = num_pat.match(clean_line)
            if not clean_line:
                in_result[0] = b''
                write(b'\n')
                return
            elif m is not None:
                is_match_line = m.group(2) == b':'
                if (is_match_line and link_matching_lines) or (not is_match_line and link_context_lines):
                    write_hyperlink(write, in_result[0], raw_line, frag=m.group(1))
                    return
            write(raw_line)
        else:
            if raw_line.strip():
                in_result[0] = clean_line
                if link_file_headers:
                    write_hyperlink(write, in_result[0], raw_line)
                    return
            write(raw_line)

    cmdline = ['rg', '--pretty', '--with-filename'] + sys.argv[1:]
    try:
        p = subprocess.Popen(cmdline, stdout=subprocess.PIPE)
    except FileNotFoundError:
        raise SystemExit('Could not find the rg executable in your PATH. Is ripgrep installed?')

    consume_process(p, line_handler)



if __name__ == '__main__':
    main()
