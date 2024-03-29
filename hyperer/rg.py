#!/usr/bin/env python
# License: GPLv3 Copyright: 2020, Kovid Goyal <kovid at kovidgoyal.net>
import re
import subprocess
import sys
from . import make_hyperlink, consume_process, strip_ansi

# TODO - parse --colors to see if something other than red is being used for matches. Or maybe switch to matching on bold if it's only used for matches?
match_pat = re.compile(b"\x1b\\[31m(.+?)\x1b\\[0m")


def link_match(line, path, line_num, prefix_width) -> bytes:
    frag = line_num
    params = {b"line": line_num}
    if match := match_pat.search(line):
        # If we're able to find an individual match via its being colored, link to the column of the first match
        # TODO - this is a byte offset into the line. It should likely be a unicode-aware character offset
        col_num = b"%d" % (len(strip_ansi(line[: match.start()])) + 1 - prefix_width)
        frag += b":" + col_num
        params[b"column"] = col_num
    return make_hyperlink(path, line, frag=frag, params=params)


def main(argv=sys.argv, write=None):
    output_altering_flags = set(
        [
            "--column",
            "--json",
            "-I",
            "--no-filename",
            "--no-heading",
            "-N",
            "--no-line-number",
            "--vimgrep",
        ]
    )
    for arg in argv:
        if arg in output_altering_flags:
            raise SystemExit(
                f"hyperer-rg relies on the output format of rg and can't be used with the '{arg}' flag. Call rg directly to use it."
            )

    in_result: list[bytes] = [b""]
    num_pat = re.compile(rb"^(\d+):")

    def line_handler(write, raw_line, clean_line):
        if in_result[0]:
            m = num_pat.match(clean_line)
            if not clean_line:
                in_result[0] = b""
            elif m := num_pat.match(clean_line):
                write(link_match(raw_line, in_result[0], m.group(1), len(m.group(0))))
                return
        elif raw_line.strip():
            in_result[0] = clean_line
        write(raw_line)

    # rg 11 on ubuntu doesn't include color with --pretty, so we specify the --pretty options explicitly
    # We also use --color=ansi instead of always as we parse ansi codes
    cmdline = [
        "rg",
        "--with-filename",
        "--heading",
        "--color=ansi",
        "--line-number",
    ] + argv[1:]
    try:
        p = subprocess.Popen(cmdline, stdout=subprocess.PIPE)
    except FileNotFoundError:
        raise SystemExit(
            "Could not find the rg executable in your PATH. Is ripgrep installed?"
        )

    return consume_process(p, line_handler, write)
