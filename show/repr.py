"""
Home for repr implementations.
"""

from pprint import pformat
from warnings import warn
from .util import _PY2
if _PY2:
    from inspect import getargspec
else:
    from inspect import getfullargspec


# TODO: make possible to call reprs with the context
#       object so can pass in deigits, say
#       so can show.set(digits=4) meaningfully

#       goal: enable show(f, g /digits(5))


"""
Reprs should take either an optional opts argument or **kwargs, so that they can
all be called with opts=... to pass in context information. However this is desirable
not required. Repr functions are inspected once for whether they can take context
information, and that fact is remembered.
"""

class ReprStr(str):
    """
    A str subclass noting that the repr has already been rendered.

    Primarily useful to not re-repr what has already been repr'd.
    This avoids gratiutious requoting and erroneous interpretation
    as a string at hart, when in fact it is only a string insofar
    as it is the vessel for another type's repr.
    """
    def __repr__(self):
        return self


def float_repr(f, opts=None):
    """
    Enhanced float repr. Uses DEFAULT_DIGITS as a maximum
    number of digits. Does not show trailing 0s by default
    to limit visual clutter.
    """

    fstr = '{0:0.{1}f}'.format(f, opts.digits)
    return ReprStr(fstr.rstrip('0'))


def np_repr(v, opts=None):
    np_digits = None
    try:
        import numpy as np
        np_digits = np.get_printoptions()['precision']
        np.set_printoptions(precision=opts.digits)
    except:
        pass
    result = str(v)
    if np_digits is not None and np_digits != opts.digits:
        # Put precision back as we found it
        np.set_printoptions(np_digits)
    return ReprStr(result)

    # FIXME: add more graceful repr for numpy objects that doesnt monkeypatch a global


def pd_repr(v, opts=None):
    pd_float_format = None
    try:
        import pandas as pd
        pd_float_format = pd.get_option('float_format')
        frepr = lambda f: '{0:0.{1}f}'.format(f, opts.digits)
        pd.set_option('float_format', frepr)
    except:
        pass
    result = str(v)
    print('ar:', ascii(result))
    if pd_float_format is not None:
        pd.set_option('float_format', pd_float_format)
    return ReprStr(result)

    # FIXME: add more graceful repr for pd objects that doesnt monkeypatch a global


# IF there is a better, more concise, or more expressive way to
# represent a type than ``builtins.repr`` or ``pprint.pformat``,
# register it here via its full type name (e.g.``type_longname``)
repr_lookup = {
    'numpy.ndarray': np_repr,
    'pandas.core.series.Series': pd_repr,
    'numpy.ma.core.MaskedArray': str,
    'pandas.core.frame.DataFrame': pd_repr,
    'float': float_repr,
}

# Lookup of whether a repr function wants opts to be passed in
repr_wants_opts = {}


def wants_opts(func):
    """
    Does the given function want opts context to be passed in?
    """
    try:
        if _PY2:
            argspec = getargspec(func)
            return 'opts' in argspec.args or bool(argspec.keywords)
        else:
            argspec = getfullargspec(func)
            return 'opts' in argspec.args or bool(argspec.varkw)
    except TypeError:
        # builtin type names like `str` can't have their arg specs inspected
        # Good sign they cannot take opts context
        return False

def default_repr(value, opts=None):
    """
    The very most primived, fall-back repr defined by show.
    """
    try:
        width = opts.wrap if opts is not None and opts.wrap else 120
        # beginning of attempts to integrate with surrounding conctext
        return pformat(value, indent=4, width=width, depth=5)

        # At one point show tried to intercept highly generic reprs such as
        # '<__main__.User object at 0x10c73dbd0>' and dive deeper to give a
        # better representation (e.g. show properties). If we wanted to do that
        # again, this would be the place.
    except Exception as e:
        warn('Extremely primitive repr')
        return repr(value)

# TODO: integrate with width of terminal or show object
# TODO: determine how to integrate with IPython _repr_html_


def get_repr(value, opts=None):
    """
    Default entry point for getting the string representation of a Python
    object. If a value's type has a preferred stringifier, use it. If not,
    fall back to default_repr().  Custom show stringifiers are often more
    terse, e.g. for NumPy and Pandas objects. They also obey local settings
    like opts.digits.
    """
    type_name = type_longname(value)
    rfunc = repr_lookup.get(type_name, default_repr)

    # Call repr, ideally with opts, but naked otherwise
    takes_opts = repr_wants_opts.setdefault(rfunc, wants_opts(rfunc))
    return rfunc(value, opts=opts) if takes_opts else rfunc(value)



def type_longname(obj):
    s = str(type(obj))
    if s.startswith("<class '"):
        # strip off the "<class '" prefix and '> suffix
        return s[8:-2]
    return s


def type_shortname(obj):
    longname = type_longname(obj)
    return longname.split('.')[-1]


def typename(value):
    """
    Return the name of a type. Idiosyncratic formatting in order to
    provide the right information, but in the least verbose way possible. E.g.
    where Python would format `<type 'int'>` or `class '__main__.CName'>` or
    `<class 'module.submod.CName'>`, this function would return `<int>`,
    `<CName>`, and `<CName>` respectively. If a neat name cannot be returned
    directly, the default Python type formatting is invoked, then the string
    result hacked apart.
    """
    type_ = type(value)
    try:
        return '<{0}>'.format(type_.__name__)
    except AttributeError:                  # pragma: no cover
        rawname = '{0!r}'.format(type_)
        return rawname[rawname.index("'")+1:rawname.rindex("'")]

        # Not clear this except can ever execute. Are there actually Python
        # types that don't have names? Presumably a good idea to guard against
        # the possibility, but even anonymous types (e.g. ``type("", (),
        # {})()``) have ``__name__`` attributes.

def better_dir_name(thing, name):
    """
    Enhanced repr for dir names.
    """
    if callable(thing):
        return name + '()'
    if thing is not None:
        return name + typename(thing)
    return name

    # TODO: more enhacements. Types/classes, properties, variables,
    # slots, ...

# TODO: Refactor so that typename doesn't have extra chars.
#       Maybe segment typename from typelabel.


# For study:
# https://pypi.python.org/pypi/pprintpp/0.3.0
# https://pypi.python.org/pypi/prettier/0.92
