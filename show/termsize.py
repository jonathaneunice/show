
"""
Determine height and width of current terminal.

Combines best methods mentioned in:
http://stackoverflow.com/questions/566746/how-to-get-console-window-width-in-python
"""

__all__ = ['get_terminal_size']


# Mimic terminal_size struct that os, shutil, and posix modules return
# from C code
from collections import namedtuple
terminal_size = namedtuple('terminal_size', 'columns lines')


DEFAULT_ANSWER = terminal_size(columns=80, lines=24) # 1985 all over again


# Series of individual approaches to determining terminal size, roughly in order
# they should be attempted. None catch their own exceptions, nor should they.
# Any exceptions are managed by `get_terminal_size()` as part of attempt
# sequencing.


def _from_os_module():
    # requires Python 3.3 or later
    import os
    return os.get_terminal_size(0)


def _from_curses_module():
    # best fallback
    import curses
    w = curses.initscr()
    height, width = w.getmaxyx()
    return terminal_size(columns=width, lines=height)


def _from_stty():
    # fallback request to shell
    # stty common on Linux and macOS
    import subprocess
    tup = subprocess.check_output(['stty', 'size']).decode().split()
    return terminal_size(columns=int(tup[1]), lines=int(tup[0]))


def _from_windows():
    # source: https://gist.github.com/jtriley/1108174
    from ctypes import windll, create_string_buffer
    # stdin handle is -10
    # stdout handle is -11
    # stderr handle is -12
    h = windll.kernel32.GetStdHandle(-12)
    csbi = create_string_buffer(22)
    res = windll.kernel32.GetConsoleScreenBufferInfo(h, csbi)
    if res:
        (bufx, bufy, curx, cury, wattr,
         left, top, right, bottom,
         maxx, maxy) = struct.unpack("hhhhHhhhhhh", csbi.raw)
        sizex = right - left + 1
        sizey = bottom - top + 1
        return terminal_size(columns=sizex, lines=sizey)
    raise RuntimeError


def get_terminal_size():
    """
    Mimic `os.get_terminal_size()` (minus the file descriptor parameter).
    Has several different mechanisms, used in turn. If nothing
    sticks, returns a default value.
    """
    methods = [
        _from_os_module,
        _from_curses_module,
        _from_stty,
        _from_windows,
    ]
    for method in methods:
        try:
            return method()
        except Exception:
            pass
    return DEFAULT_ANSWER


# This module is horrifically heuristic and exceedingly dicey
# to test.
