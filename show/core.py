# -*- encoding: utf-8 -*-

"""Debugging print features. """

import inspect
import sys
import os
import re
import six
import fnmatch
from options import Options, OptionsClass, OptionsContext, Transient, Unset
from options.methset import *
from say import Fmt, fmt, say, first_rest
from say.core import Say, SayReturn
from hjoin import *
from ansiwrap import fill
from functools import wraps
from .linecacher import *
from .linecacher import _IPY
from .introspect import *
from .util import *
from .util import _PY2
from .repr import *
from .exceptions import *
from .version import __version__
from functools import wraps

from nulltype import NullType
Private    = NullType('Private')
Impossible = NullType('Impossible')
Ignore     = NullType('Ignore')


DEBUGGING = True

CallArgs.add_target_func('show')


QUOTE_CHARS = ('"', "'", '"""', "'''")


# Probably cannot make `show` work from the interactive Python
# REPL because it constantly returns `<stdin>` as the filename
# of the current execution frame, and 1 as the line number.
# I am now more pessimistic than when I answered this SO question:
# http://stackoverflow.com/questions/13204161/how-to-access-the-calling-source-line-from-interactive-shell
# However, I am *much* more optimistic about the special case of
# getting sufficient information when run under IPython (either
# its console or under Jupyter Notebook). IPython's `_ih` structure
# holds input cells, and the filename handed back by `inspect` can
# be reliably queried and parsed into a solid index into `_ih`.
# Currently considering dropping all support for interactive use
# in the normal Python REPL, and putting all efforts at interactive
# support into IPython.

def _afunction(f): pass
function = type(_afunction)
module   = type(sys)
class _XYZ(object):
    def method(self): pass
_xyz = _XYZ()

if not _PY2:
    unicode = basestring = str

FUNKY = (function, module, type, type(_XYZ.method), type(_xyz.method), type(len)) # funky => functional infrastructure


class Show(OptionsClass):

    """
    Show objects print debug output in a 'name: value' format that
    is convenient for discovering what's going on as a program runs.
    """

    options = Options(
        show_module=False,  # Show the module name in the call location
        where=False,        # show the call location of each call
        sep="  ",           # separate items with two spaces, by default
        retvalue=False,     # return the value printed?
        digits=4,           # number digits to show floating point values
        props=Transient,    # props desired to print (given at call time)
        omit=Transient,     # vars not to print (for those like show.locals,
                            # show.dir, etc that might default to many)
        verbose=Transient,
        fmtfunc=get_repr,   # formatting func used to format each value
        fmtcode=unicode,    # formatting used to format code snippets
        prefixer=None,      # prefix for each show call (may be callable)
        shape=None,         # shape of the output (if can be set)
        show=True,          # show or not
        quietplaces=[],     # experimental: list of no-show places
        _callframe=Transient,
        wrap = None,        # experimental: promote say options
    )

    def __init__(self, **kwargs):
        self.options = self.opts = Show.options.push(kwargs)
        self.fmt = Fmt()
        self.say = SayReturn()
        self._watching = {} # remembers last value of variables for given frames
        self.__version__ = __version__


    def call_location(self, caller):
        """
        Create a call location string indicating where a show() was called.
        """
        if _IPY:
            cellno, lineno = find_cell_loc(caller)
            return "[{}]:{}".format(cellno, lineno)
        elif isInteractive:
            return "<stdin>:{0}".format(len(history.lines))
        else:
            module_name = ""
            if self.opts.show_module:
                filepath = caller.f_locals.get('__file__', caller.f_globals.get('__file__', 'UNKNOWN'))
                filename = os.path.basename(filepath)
                module_name = re.sub(r'.py', '', filename)

            lineno = caller.f_lineno
            co_name = caller.f_code.co_name
            if co_name == '<module>':
                co_name = '__main__'
            func_location = wrapped_if(module_name, ":") + wrapped_if(co_name, "", "()")
            return ':'.join([func_location, str(lineno)])

    def value_repr(self, value, opts):
        """
        Return a representation string (like ``repr()``) for value.

        If highlighting is accomplished, it is inserted here.

        Needs to escape any brace characters (e.g. for ``dict`` or ``set`` values
        with double-{{ so they are not interpreted as format template characters
        when the composed string is eventually output by ``say``.
        """
        fvalue = self.opts.fmtfunc(value, opts)
        return self.fmt.escape(fvalue)

    def code_repr(self, code):
        """
        Return a formatted string for code. If there are any internal brace
        characters, they are escaped (doubled) so that they are not interpreted
        as format template characters when the composed string is eventually
        output by ``say``.
        """
        return self.fmt.escape(self.opts.fmtcode(code))

        # TODO: remove value_repr and code_repr given say.verbatim

    def arg_format(self, name, value, caller, opts):
        """
        Format a single argument. Strings returned formatted.
        """
        if name.startswith(QUOTE_CHARS):
            return fmt(value, _callframe=caller)
        else:
            label = '{0}:'.format(name)
            return hjoin([label, self.value_repr(value, opts)], sep=' ')

    # TODO: it is likely that styling information needs to be applied
    #       here if ANSI colors are being used so that each arg is
    #       colored separately. This would help manage competing
    #       ANSI formatters, e.g. when show(x, y, style='blue') is
    #       run but x and y are Pygments formatted.
    #       This is a place where the item-level formatting really
    #       needs to be separted from the line level formatting.


    def arg_format_items(self, name, value, caller, opts):
        """
        Format a single argument to show items of a collection.
        """
        if name.startswith(QUOTE_CHARS):
            return fmt(value, _callframe=caller)
        else:
            fvalue = self.value_repr(value, opts)
            if isinstance(value, (list, dict, set, basestring)):  # weak test
                length = len(value)
                itemname = 'char' if isinstance(value, basestring) else 'item'
                s_or_nothing = '' if length == 1 else 's'
                return "{0} ({1} {2}{3}): {4}".format(name, length, itemname, s_or_nothing, fvalue)
            else:
                return "{0}: {1}".format(name, fvalue)

        # Aren't all these alternate arg formatters because we don't have faith that
        # the repr will be to our liking? The label format never changes. Wouldn't it be easier to call get_repr
        # with some kind of display hint?

    def arg_format_dir(self, name, value, caller, opts):
        """
        Format a single argument to show items of a collection.
        """
        if name.startswith(QUOTE_CHARS):
            return fmt(value, _callframe=caller)
        else:
            label = "{0}{1}:".format(name, typename(value))
            attnames = omitnames(dir(value), opts.omit)
            if opts.verbose:
                better_names = [better_dir_name(getattr(value, n), n)
                                for n in attnames]
                valuestr = ' '.join(better_names)
            else:
                valuestr = ' '.join(attnames)
            if opts.wrap:
                prefix_width = len(label) + 1
                valuestr = fill(valuestr, width=opts.wrap - prefix_width)
                if 'wrap' in opts.maps[0]:
                    del opts.maps[0]['wrap'] # down and dirty

            result = hjoin([label, valuestr])
            # print('☾', ascii(result))
            return result

            # This wrapping not quite right. Basically, you cannot line-wrap
            # precisely until you know how much width you have to wrap into,
            # which we cannot here (not knowing line prefix, indent, etc.)
            # However, neither can we wrap later, once those are known, because
            # then we have only line wrapping, not the column wrapping we'd like.
            # HTML output is altogether simpler, in that final computations are
            # performed later, once all info present.

            # Also, line wrapping is happening after this point, destroying the
            # beautiful column wrapping implemented here. Or at least, degrading
            # it from column back down to line wrapping.

            # Line wrapping interfering with column wrapping is now fixed, at
            # cost of complex, low-level hack (removing 'wrap' key). It does work...
            # but is exteremly ungeneral and specialized.

    def arg_format_props(self, name, value, caller, opts, ignore_funky=True):
        """
        Format a single argument to show properties.
        """
        if name.startswith(QUOTE_CHARS):
            return fmt(value, _callframe=caller)
        else:
            try:
                props = self.opts.props
                if props and isinstance(props, basestring):
                    proplist = props.split(',') if ',' in props else props.split()
                    proplist = [ p.strip() for p in proplist ]
                else:
                    propkeys = object_props(value)
                    if opts.omit:
                        propkeys = omitnames(propkeys, opts.omit)
                    if ignore_funky:
                        propkeys = [ p for p in propkeys if not isinstance(getattr(value, p), FUNKY) ]
                    proplist = sorted(propkeys, key=lambda x: x.replace('_','~'))

                propvals = [ "    {0}={1}".format(p, ellipsis(self.value_repr(getattr(value, p), opts))) for p in proplist ]

                # change out brace charactes likely to cause problems
                LUBRACE, RUBRACE = six.u("\u2774"), six.u("\u2775")
                propvals = [ p.replace("{{", LUBRACE).replace("}}", RUBRACE) for p in propvals ]
                # this is probably totally broken

                if hasattr(value, 'items'):
                    if opts.shape == 'compact':
                        propvals = [ "{0}={1}".format(k, ellipsis(self.value_repr(v, opts)))
                                  for k,v in value.items() ]
                        return "{0}: {1}({2})".format(name, type(value).__name__, ", ".join(propvals))
                    else:
                        propvals += [ "    {0}: {1}".format(k, ellipsis(self.value_repr(v, opts)))
                                     for k,v in value.items() ]
                return "{0}{1}:\n{2}".format(name, typename(value), '\n'.join(propvals))
            except Exception as e:
                return "{0}{1}: {2}".format(name, typename(value), self.value_repr(value, opts))

    def get_arg_tuples(self, caller, values):
        """
        Return a list of argument (name, value) tuples.
        :caller: The calling frame.
        :values: Argument values.
        """
        filename, lineno = frame_to_source_info(caller)
        try:
            argnames = CallArgs(filename, lineno).args
        except ArgsUnavailable:
            argnames = ['?'] * len(values)
        return list(zip(argnames, list(values)))

    def set(self, **kwargs):
        """
        Change the values of the show.
        """
        self.options.set(**kwargs)
        self.fmt.set(**kwargs)

        # FIXME: with show.settings() broken - needs better rules for
        # passing values into the context manager

        # TODO: HMMM - do we need combo say/fmt feature from say after all?

        # NB this is the paradigm usage of ``options``'s "leftovers" strategy


    def clone(self, **kwargs):
        """
        Create a child instance whose options are chained to this instance's
        options (and thence to Show.options). kwargs become the child instance's
        overlay options. Because of how the source code is parsed, clones must
        be named via simple assignment.
        """
        child = Show()
        child.options = self.options.push(kwargs)

        # introspect caller to find what is being assigned to
        caller = inspect.currentframe().f_back
        filename, lineno = frame_to_source_info(caller)
        sourceline = getline(filename, lineno)
        name = sourceline.strip().split()[0]
        CallArgs.add_target_func(name)
        return child

    def _showcore(self, args, kwargs, caller, formatter, opts):
        """
        Do core work of showing the args.
        """
        self.opts = opts

        # Introspect for argument names
        argtuples = self.get_arg_tuples(caller, args)

        # Construct the formatted result string
        fvals = [ formatter(name, value, caller, opts) for name, value in argtuples ]
        valstr = hjoin(fvals, sep=opts.sep)

        if opts.where:
            locstr = self.call_location(caller) + ':'
            locval = [ hjoin([locstr, valstr]) ]
            # does Fmt need to be hjoin line aware?
        else:
            locval = [ valstr ]

        # Emit the result string, and optionally return it
        silent = not lambda_eval(opts.show)
        # print('☾ _showcore: opts.show =', repr(opts.show), 'silent =', repr(silent))
        # kwargs['silent'] = silent
        kwargs['retvalue'] = opts.retvalue
        retval = self.fmt(*locval, **opts)  # changed
        if not silent:
            retval = retval.replace("{", "{{").replace("}", "}}")
            self.say(retval)
            # TODO: swap out for say.verbatim
        # silence functionality needs hard look
        if opts.retvalue and not silent:
            return retval

    def __call__(self, *args, **kwargs):
        """
        Main entry point for Show objects. Invoked when they are called.
        So for most intents and purposes, this is the `show()` entry point.
        """
        caller = self._get_callframe(kwargs)
        opts = self.opts = self.options.push(kwargs)
        opts.update(kwargs) # in flux; here for options that don't get passed
                            # through - need more coordination with options module
        formatter = self.arg_format_props if opts.props else self.arg_format
        result = self._showcore(args, kwargs, caller, formatter, opts)
        return result

    def items(self, *args, **kwargs):
        """
        Show items of a collection.
        """
        caller = self._get_callframe(kwargs)
        opts = self.options.push(kwargs)
        return self._showcore(args, kwargs, caller, self.arg_format_items, opts)

    def dir(self, *args, **kwargs):
        """
        Show the attributes possible for the given object(s)
        """
        caller = self._get_callframe(kwargs)
        opts = self.options.push(kwargs)
        opts.setdefault('omit', '__*')
        opts.setdefault('verbose', True)
        opts.update(kwargs) # special, to pass down wrap etc
        # print('☾ show.dir: opts:', opts, 'kwargs:', kwargs)

        return self._showcore(args, kwargs, caller, self.arg_format_dir, opts)

    def pprint(self, *args, **kwargs):
        """
        Show the objects as displayed by pprint. Not well
        integrated as yet. Just a start.
        """
        caller = self._get_callframe(kwargs)
        opts = self.options.push(kwargs)

        return self.say(pformat(*args, **kwargs))

    def props(self, *args, **kwargs):
        """
        Show properties of objects.
        """
        caller = self._get_callframe(kwargs)
        opts = self.opts = self.options.push(kwargs)
        opts.setdefault('omit', '__*')
        if len(args) > 1 and isinstance(args[-1], str):
            used = opts.addflat([args[-1]], ['props'])
            args = args[:-1]
        if opts.sep == Show.options.sep:
            opts.sep = '\n\n'
        return self._showcore(args, kwargs, caller, self.arg_format_props, opts)

        # should this check for and show (perhaps with ^ annotation), properties
        # of object inherited from class?

        # if no props, should show normally?
        # Ie less difference between show, show.items, show.props
        # also, maybe more automatic or easy-to-specify truncation of results?

    def args(self, **kwargs):
        """
        First attempt at a standalone "show the arguments"
        method. Does not yet obey all the standard rules about
        return values, silence, etc.
        """
        caller = self._get_callframe(kwargs)
        opts = self.opts = self.options.push(kwargs)
        arginfo = inspect.getargvalues(caller)
        argstr = inspect.formatargvalues(*arginfo)
        funcname = caller.f_code.co_name
        funcstr = funcname + argstr
        if '{' in funcstr:
            # excape for fmt
            funcstr = funcstr.replace("{", "{{").replace("}", "}}")
        fmtstr = self.fmt(funcstr, **opts)
        self.say(fmtstr)

        # FIXME: send args through improved formatting that can do highlighting
        # FIXME: regularize the fmt/say/say.verbatim distinctions
        # FIXME: do we really nee the explicit escaping?


    def locals(self, *args, **kwargs):
        """
        Show all local vars, plus any other values mentioned.
        """
        caller = self._get_callframe(kwargs)
        opts = self.opts = self.options.push(kwargs)
        opts.setdefault('omit', '')
        assert not args  # for now
        locdict = caller.f_locals

        to_omit = (opts.omit or '') + ' @py_assert*'
        names = omitnames(locdict.keys(), to_omit)

        # Construct the result string
        parts = [ self.arg_format(name, locdict[name], caller, opts) for name in names ]
        valstr = opts.sep.join(parts)
        locval = [ self.call_location(caller) + ":  ", valstr ] if opts.where else [ valstr ]

        # Emit the result string, and optionally return it
        kwargs['silent'] = not lambda_eval(opts.show)
        kwargs['retvalue'] = opts.retvalue

        # should probably use non-interpreting say.verbose
        # or a locvalstr - why is the retval coming from say?
        fmtstr = self.fmt(*locval, **opts)
        retval = self.say(fmtstr, **kwargs)
        if opts.retvalue:
            return retval

    def where(self, *args, **kwargs):
        """
        Show where program execution currently is. Can be used with
        normal output, but generally is intended as a marker.
        """
        caller = self._get_callframe(kwargs)
        opts = method_push(self.options, self.where.__kwdefaults__, kwargs)
        opts.where = True
        show('where options:', opts, kwargs)
        return self._showcore(args, kwargs, caller, self.arg_format, opts)

    def changed(self, *args, **kwargs):
        """
        Show the local variables, then again only when changed.
        """
        caller = self._get_callframe(kwargs)
        opts = self.opts = self.options.push(kwargs)

        f_locals = caller.f_locals
        _id = id(f_locals)

        valitems  = [ (k, v) for (k, v) in f_locals.items() if \
                                not k.startswith('@py_assert') and \
                                not k.startswith('_') and \
                                not isinstance(v, FUNKY) and \
                                not getattr(v, '__module__', '').startswith( ('IPython', 'site', 'show')) and \
                                not (isInteractive and (k == 'In' or k == 'Out'))
                            ]
        if args:
            argtuples = self.get_arg_tuples(caller, args)
            valitems.extend(argtuples)

        valdict = dict(valitems)
        _id = id(f_locals)
        watching = self._watching.get(_id, None)
        if watching is None:
            self._watching[_id] = watching = to_show = valdict
        else:
            to_show = {}
            for k, v in valdict.items():
                if k not in watching or v != watching[k]:
                    to_show[k] = v
                    watching[k] = v

        names = omitnames(to_show.keys(), opts.omit)

        # Construct the result string
        if names:
            valstr = opts.sep.join([ self.arg_format(name, to_show[name], caller, opts) for name in names ])
        else:
            valstr = "no changes" # six.u('\u2205')
        locval = [ self.call_location(caller) + ":  ", valstr ] if opts.where else [ valstr ]

        # Emit the result string, and optionally return it
        kwargs['silent'] = not lambda_eval(opts.show)
        kwargs['retvalue'] = opts.retvalue

        retval = self.say(*locval, **kwargs)
        if opts.retvalue:
            return retval

    def quiet(self, func, value=True):
        """
        Add or remove a function from the list of "quiet places"--that
        is, functions where show is currently turned off.
        """
        func_name = func if is_string(func) else func.__name__
        qp = self.options.quietplaces
        if value:
            if func_name not in qp:
                qp.append(func_name)
        else:
            if func_name in qp:
                qp.remove(func_name)

    def inout(self, *dargs, **dkwargs):
        """
        Show arguments to a function. Decorator itself may
        take arguments, or not. Whavevs.
        """

        # argument prep for decorator with optional arguments
        no_args = False
        if len(dargs) == 1 and not dkwargs and callable(dargs[0]):
            # We were called without args
            func = dargs[0]
            dargs = []
            no_args = True

        opts = method_push(self.options, self.inout.__kwdefaults__, dkwargs)

        # mkwargs = self.meth_defaults.get('inout', {}).copy()
        # mkwargs.update(dkwargs)
        # opts = self.options.push(mkwargs)
        # say_kwargs = mkwargs
        only_arg = dkwargs.get("only")
        only_in = only_arg == "in"
        only_out = only_arg == "out"

        def inout_decorator(func):
            """
            Decorator that shows arguments to a function.
            """
            func_code = func.__code__
            argnames = func_code.co_varnames[:func_code.co_argcount]
            fname = func.__name__

            @wraps(func)
            def echo_func(*args, **kwargs):
                # update some options, in case they've changed in the meanwhile
                opts.update(self.inout.__kwdefaults__)
                opts.update(dkwargs)
                argitems = list(zip(argnames, args)) + list(kwargs.items())
                argcore = ', '.join('{0}={1!r}'.format(*argtup) for argtup in argitems)
                callstr = ''.join([func.__name__, '(', argcore, ')'])
                fmtcallstr = self.code_repr(callstr)
                if not only_out and func.__name__ not in opts.quietplaces:
                    self.say(fmtcallstr, **opts) # changed
                try:
                    retval = func(*args, **kwargs)
                    if not only_in and func.__name__ not in opts.quietplaces:
                        fmtretval = self.value_repr(retval, opts)
                        retstr = ''.join([fmtcallstr, ' -> ', fmtretval])
                        self.say(retstr, **opts) # changed
                    return retval
                except Exception as e:  # pragma: no cover
                    raise e

            return echo_func

        if no_args:
            return inout_decorator(func)
        else:
            return inout_decorator

    # TODO: add ability to give methods default styles (like all show.where in red)


    def prettyprint(self, mode='ansi', sep='  ', indent=4, width=75, depth=5,
                    prefix=u'\u25a0  ', prefixer=True, style='friendly'):
        """
        Turn on multiple pretty-printing techniques, including a Unicode prefix,
        Pygments-based syntax highlighting of data values, ....
        Mode can be 'text' or 'ansi'.
        """
        self.set(sep=sep, prefix=prefix, wrap=width)
        if prefixer is True:
            # black square, white square
            # do we need prefixer, or is prefix enough?
            self.set(prefixer=first_rest(u'\u25a0  ', u'\u25a1  '))
        else:
            self.set(prefix=prefixer)
        mode = mode.lower()
        if mode == 'text':
            self.set(fmtfunc=get_repr)
            return
        elif mode == 'ansi':
            if 'Komodo' in os.environ.get('PYDBGP_PATH', ''):
                self.set(fmtfunc=get_repr)
                return
            try:
                from pygments import highlight
                from pygments.lexers import PythonLexer
                lexer = PythonLexer()
                from pygments.formatters import Terminal256Formatter
                formatter = Terminal256Formatter(style=style)
                self.set(fmtfunc=lambda x, opts=None: highlight(get_repr(x, opts), lexer, formatter).strip())
                self.set(fmtcode=lambda x: highlight(x,     lexer, formatter).strip())
                return
            except ImportError:
                raise ImportWarning('install pygments for ANSI forfmatting; falling back to plain text')
                self.set(fmtfunc=pf)
                return
            except Exception as e:
                raise e
        else:
            raise BadValue("{mode!r} not a recognized pretty print mode")

    # TODO: Give option for showing return value differently
    # TODO: Give this decorator standard show kwargs


    def _get_callframe(self, kwargs=None):
        """
        Set the _callframe value in kwargs to be the frame of the original caller.
        However, this is done with setdefault so that if for some reason the caller
        has specifically dictated the call frame to use, use that instead.
        """
        caller = inspect.currentframe().f_back.f_back # back twice, once to compensate for this method
        if kwargs is not None:
            kwargs.setdefault('_callframe', caller)
            # if in quiet place, turn show off
            # note because callframe interpretation is active, must always consider
            # it, even if not used for variable interpolation
            if caller.f_code.co_name in self.options.quietplaces:
                kwargs.setdefault('show', False)
        return caller

    # Promote delegated formatting functions

    def blank_lines(self, *args, **kwargs):
        self._get_callframe(kwargs)
        opts = method_push(self.options, self.blank_lines.__kwdefaults__, kwargs)
        if opts.show:
            self.say.blank_lines(*args, **opts)

    def hr(self, *args, **kwargs):
        self._get_callframe(kwargs)
        opts = method_push(self.options, self.hr.__kwdefaults__, kwargs)
        if opts.show:
            self.say.hr(*args, **opts)

    def title(self, *args, **kwargs):
        self._get_callframe(kwargs)
        opts = method_push(self.options, self.title.__kwdefaults__, kwargs)
        if opts.show:
            self.say.title(*args, **opts)

    def sep(self, *args, **kwargs):
        self._get_callframe(kwargs)
        opts = method_push(self.options, self.sep.__kwdefaults__, kwargs)
        if opts.show:
            self.say.sep(*args, **opts)

    # TODO: on these elevation methods, should push down **kwargs or **opts?
    #       kwargs may be sufficient, if opts only needs to be resolved for
    #       opts.show value
    # TODO: finally clean up/integrate the method-relevant setting functions


# enable method-local setting
enable_func_set(Show.where, Show)
enable_func_set(Show.inout, Show)
enable_func_set(Show.blank_lines, Show)
enable_func_set(Show.hr, Show)
enable_func_set(Show.title, Show)
enable_func_set(Show.sep, Show)

show = Show()

# institute nice defaults
show.sep.set(vsep=(1,0))
show.title.set(vsep=1)
# TODO: hoist such defaults into a decorator

# TODO: Should ensure that either instances or classes can have those setters run

class NoShow(Show):
    """
    NoShow is a Show variant that shows nothing. Maintains just enough context
    to respond as a real Show would. Any clones will also be ``NoShow``s--again, to retain
    similarity. Designed to squelch all output in an efficient way, but without
    requiring any changes to the source code.
    """

    options = Show.options.add(
        show   = False,
        retval = False,
    )

    def __init__(self, **kwargs):
        self.options = NoShow.options.push(kwargs)
        self.say = SayReturn(silent=True, retvalue=False)
        self.opts = None  # per call options, set on each call to reflect transient state

    def clone(self, **kwargs):
        """
        Create a child instance whose options are chained to   this instance's
        options (and thence to Show.options). kwargs become the child instance's
        overlay options. Because of how the source code is parsed, clones must
        be named via simple assignment.
        """
        return NoShow()

    def _do_nothing(self, *args, **kwargs):
        """
        Fake entry point. Does nothing, returns immediately.
        """
        return None

    __call__ = __gt__ = __rshift__ = _do_nothing
    items = dir = props = locals = changed = inout = _do_nothing
    blank_lines = hr = title = _do_nothing

noshow = NoShow()


# TODO: add easier decorator for function tracing (just @show?)
