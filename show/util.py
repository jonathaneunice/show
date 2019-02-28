import fnmatch
from say.util import stringify
import sys

_PY2 = sys.version_info[0] == 2
string_types = (str, unicode) if _PY2 else str

def is_string(obj):
    return isinstance(obj, string_types)


def omitnames(names, patterns, sort=True):
    """
    Given a collection (list, set) of ``names``, remove any that do NOT match
    the glob sub-patterns found in ``patterns`` (separated by whitespace). If
    ``sort``, returns a sorted list (the default); else return the remaining
    names in their original order. If patterns is false-y, just return names.
    """
    if not patterns:
        return names
    omitset = set()
    for pattern in patterns.split(' '):
        omitset.update(fnmatch.filter(names, pattern))
    if sort:
        return sorted(set(names) - omitset)
    else:
        result = []
        for name in names:
            if name not in omitset:
                result.append(name)
        return result


def lambda_eval(v):
    """
    If v is a callable, call it and return the value. Else, return it.
    Helpful when you want to preserve the ability to lazy-evaluate a
    value.
    """
    return v() if hasattr(v, '__call__') else v


def wrapped_if(value, prefix="", suffix="", transform=None):
    """
    If a string has a value, then transform it (optionally) and add the
    prefix and suffix. Else, return empty string. Handy for formatting
    operations, where one often wants to add decoration iff the value
    exists. This is essentially a simple version of what the ``quoter``
    module does.
    """

    if not value:
        return ""
    s = stringify(value)
    ts = transform(s) if transform else s
    return (prefix or "") + ts + (suffix or "")


def words(data):
    """
    Take a list, a comma-separated values string, or a whitespace-separated
    values string, and return a list. Essentially a simplified form of the
    ``words`` routine from ``textdata``.
    """
    if not data:                    # nothing there
        return []
    elif isinstance(data, list):    # already a list
        return data
    elif ',' in data:               # csv = comma separated values
        return [ part.strip() for part in data.strip().split(',')]
    else:                           # wsv = whitespace separated values
        return [ part.strip() for part in data.strip().split()]


def ellipsis(s, maxlen=232):
    """
    Given a string, shorten it with ellipsis if need be to fit in the
    required maxlen.
    """
    s = stringify(s)
    if len(s) > maxlen:
        return s[:maxlen - 3] + '...'
    else:
        return s

    # TODO: do we really want ... at end, or in middle?
