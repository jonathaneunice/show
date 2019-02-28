Change Log
==========

**1.6.0**  (May 15, 2017)

    Updated mechanism for method-specific option setting. Still work
    in progress, but code now much cleaner.

    One additional routine, ``show.where``, can have its method
    parameters set at runtime. More to follow as the method-setting
    technqiue progresses.

    The experimental operator forms of ``show`` such as ``>`` and
    ``>`` have been withdrawn. The operator style isn't consonant with
    Python philosophy, complicated the code base, and only partially
    worked. Interesting idea, but experience suggests they are not
    worth the trouble.

    Deprecated ``@show.retval`` is removed. Replace with ``@show.inout(only='out')``

    Shifted compatibility strategy from "Python 2 + Python 3" to
    "Python 3 + Python 2 shims." Removed some older Python 2 shims that were
    only necessary for now-removed Python 2.5 support; Python 2.{6,7}
    both have some reach-forward work (e.g. ``func.__name__`` alias for
    older ``func.func_name``) that's now used to simplify compatiblity.
    ``_PY3`` flag removed in preference for ``_PY2`` flag.


**1.5.0**  (May 14, 2017)

    Changed name of parameter ``sep`` in ``hr``, ``title``, and
    ``sep`` methods because discovered it was conflating and
    interfering with the ``sep`` parameter in the main options.  The
    horizontal separator character that is repeated N times is now
    addressed as ``char``. Also fixed bug in temporary turning off of
    output from  those methods; fixed.


**1.4.8**  (March 22, 2017)

    New ``show.pretty`` module. If you ``from show.pretty import *``
    then pretty-printing will be automatically turned on, and a
    Unicode solid square will be prefixed to every line, to make it
    easier to visually distinguish debug output from normal program
    output.


**1.4.7**  (March 9, 2017)

    Bumped test coverage to 80%.  In the process, discovered and fixed
    some bugs with ``show.props``. Most things that can be basically
    unit-tested, are. Largest remaining test coverage gaps concern
    operation under different I/O managers--esp. IPython and the
    standard Python REPL--that will require integration testing.


**1.4.6**  (March 1, 2017)

    Quashed second bug related to IPython and its ``%run`` command,
    especially as used by the Enthought Canopy IDE.


**1.4.5**  (March 1, 2017)

    Fixed problem with IPython when program run with the ``%run``
    command. Fix esp. important for users of Enthought Canopy IDE,
    which uses this mode of execution extensively.


**1.4.4**  (February 19, 2017)

    Tweak ``show.prettyprint()`` to not automatically multi-line all
    show output. If you want multi-line output, either set
    ``show.prettyprint(sep='\m')`` to globalize that preference, or
    use ``show(..., sep='\n)`` each time you want multi-line.


**1.4.3**  (February 2, 2017)

    Bug fix: When `show.set(prefix=...)` or other settings were used,
    duplicate behaviors could occur, like two prefix strings printing,
    not just one. Also, support for Python 2.6 has been restored. Not
    that you should still be using that antiquated buggy. But if you
    are, show will once again work for you, given removal of the
    preventing dependency (``stuf``).


**1.4.2**  (January 30, 2017)

    Fixed bug when location display is active (e.g. after
    `show.set(where=True)`) in IPython. Now correctly identifies what
    cell code was executed in.


**1.4.0**  (January 27, 2017)

    Finally have good support for IPython, either in a Notebook or in
    a terminal/console. Suddenly, interactive use does not minimize
    show's usefulness (though the standard REPL still has glitches).


**1.3.2**  (January 26, 2017)

    Fixes nasty packaging bug (failure to bundle astor sub-package
    into source distributions) that didn't show up in testing.


**1.3.0**  (January 25, 2017)

    Python 3.5 and 3.6 now pass formal verification. This required
    embedding a 'nightly' build of astor 0.6 that has not yet made it
    to PyPI. Given the shift from codegen to newer astor AST-to-source
    library, bumping minor version.


**1.2.7**  (January 23, 2017)

    Updated dependencies to support Python 3.5 and 3.6. These versions
    do not yet pass formal validation, but they do seem to work in
    informal testing. This is the start of a push to fully support
    these most recent Python implementations, and to improve support
    for interactive code (REPL or Jupyter Notebook).


**1.2.6**  (September 1, 2015)

    Tweaks and testing for new version of underlying ``options``
    module that returns operation to Python 2.6.


**1.2.4**  (August 26, 2015)

    Major documentation reorg.


**1.2.3**  (August 25, 2015)

    Code cleanups and additional testing. Test coverage now 77%.


**1.2.1**  (August 21, 2015)

    Added ability to give ``@show.inout`` decorator its own
    parameters. Deprecated ``@show.retval``, which is now redunant
    with ``@show.inout(only=''out'')``.

    Test coverage bumped to 71%.


**1.2.0**  (August 18, 2015)

    Added ``show.where()`` as a marker for "where am I now?" Improved
    docs, esp. for ``where``, ``inout``, and ``retval`` methods.
    Improved testing. Now at 67% line coverage.


**1.1.1**  (August 17, 2015)

    Updated testing strategy to integrate automated test coverage
    metrics. Immediate test and code improvements as a result. Initial
    coverage was 53%. Releasing now at 57%.

    Clearly backed out Python 3.5 support for the moment. The AST
    ``Call`` signature has changed notably. Will need to deep-dive to
    fix that.


**1.1.0**  (August 16, 2015)

    Fixed problem with underlying ``say`` object interactions. Some
    doc and testing tweaks.


**1.0.4**  (July 22, 2015)

    Updated config, docs, and testing matrix.


**1.0.2**  (September 16, 2013)

    Improved pretty printing of code snippets for ``@show.inout`` and
    ``@show.retval`` decorators.

    Made ``show`` also accept lambdas to link to variable values.

    Added ``noshow`` object for easy turning off of showing.

    General cleanups. Tightened imports. Tweaked docs. Switched to
    ``FmtException`` from ``say>=1.0.4``, and separated extensions
    into own module.

    Drove version information into ``version.py``


**1.0.1**  (September 15, 2013)

    Moved main documentation to Sphinx format in ./docs, and hosted
    the long-form documentation on readthedocs.org. README.rst now an
    abridged version/teaser for the module.


**1.0.0**  (September 15, 2013)

    Improved robustness for interactive use. If names cannot be
    detected, still gives value result with ``?`` pseudo-name.

    Improved type names for ``show.dir`` and ``show.props``

    Improved ``show.inout`` with full call string on function return.
    A bit verbose in small tests, but too easy to lose "what was this
    called with??" context in real-scale usage unless there is clear
    indication of how the function was called.

    Improved omission of probably useless display properties via
    ``omit`` keyword.

    Began to add support for showing properties even when proxied
    through another object. Currently limited to selected SQLAlchemy
    and Flask proxies. More to come.

    Cleaned up source for better (though still quite imperfect), PEP8
    conformance

    Bumped version number to 1.0 as part of move to `semantic
    versioning <http://semver.org>`_, or at least enough of it so as
    to not screw up Python installation procedures (which don't seem
    to understand 0.401 is a lesser version that 0.5, because 401 >
    5).

    Probably several other things I've now forgotten.
