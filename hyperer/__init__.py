import functools
import os
import re
import sys
import signal
import socket
import subprocess
from typing import Callable, Optional
from urllib.parse import quote_from_bytes


@functools.cache
def hostname():
    return socket.gethostname().encode("utf-8")


def make_hyperlink(
    path: bytes, line: bytes, frag: bytes = b"", params: dict[bytes, bytes] = {}
) -> bytes:
    osc_8 = b"\x1b]8;"
    string_terminator = b"\x1b\\"
    params_enc = b":".join(k + b"=" + v for k, v in params.items())
    path_enc = quote_from_bytes(os.path.abspath(path)).encode("utf-8")
    frag = b"#" + frag if frag else b""
    return b"".join(
        [
            # Open link
            osc_8,
            params_enc,
            b";file://",
            hostname(),
            path_enc,
            frag,
            string_terminator,
            # Link content
            line,
            # Close link
            osc_8,
            b";",
            string_terminator,
        ]
    )


Writer = Callable[[bytes], None]

sgr_pat = re.compile(rb"\x1b\[.*?m")
osc_pat = re.compile(rb"\x1b\].*?\x1b\\")


def strip_ansi(line):
    line = osc_pat.sub(b"", line)  # remove any existing hyperlinks
    return sgr_pat.sub(b"", line)  # remove SGR formatting


def consume_process(
    p: subprocess.Popen,
    line_handler: Callable[[Writer, str, str], None],
    write: Optional[Writer] = None,
):
    assert p.stdout is not None
    if write is None:

        def write(b: bytes) -> None:
            sys.stdout.buffer.write(b)
            # If we're in a pipe, we'll not have a tty and be block buffered
            # Flush to avoid that.
            # Can't easily turn off block buffering from inside the program
            # https://stackoverflow.com/questions/881696/unbuffered-stdout-in-python-as-in-python-u-from-within-the-program
            sys.stdout.buffer.flush()

    try:
        for line in p.stdout:
            clean_line = strip_ansi(line).rstrip()
            line_handler(write, line, clean_line)
    except KeyboardInterrupt:
        p.send_signal(signal.SIGINT)
    except (EOFError, BrokenPipeError):
        pass
    finally:
        try:
            p.stdout.close()
        except Exception:
            pass
    return p.wait()
