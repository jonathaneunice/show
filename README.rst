
| |version| |versions| |impls| |wheel| |coverage|

.. |version| image:: http://img.shields.io/pypi/v/show.svg?style=flat
    :alt: PyPI Package latest release
    :target: https://pypi.python.org/pypi/show

.. |versions| image:: https://img.shields.io/pypi/pyversions/show.svg
    :alt: Supported versions
    :target: https://pypi.python.org/pypi/show

.. |impls| image:: https://img.shields.io/pypi/implementation/show.svg
    :alt: Supported implementations
    :target: https://pypi.python.org/pypi/show

.. |wheel| image:: https://img.shields.io/pypi/wheel/show.svg
    :alt: Wheel packaging support
    :target: https://pypi.python.org/pypi/show

.. |coverage| image:: https://img.shields.io/badge/test_coverage-80%25-00BFFF.svg
    :alt: Test line coverage
    :target: https://pypi.python.org/pypi/show

::

    from show import *

    x = 12
    nums = list(range(4))

    show(x, nums)

yields::

    x: 12  nums: [0, 1, 2, 3]

Output is self-labeled, so you don't spend time
doing that yourself.

Debug Printing
==============

Logging, assertions, unit tests, and interactive debuggers are all great
tools. But sometimes you just need to print values as a program runs to see
what's going on. Every language has features to print text, but they're
rarely customized for printing debugging information. ``show`` is. It
provides a simple, DRY mechanism to "show what's going on."

Sometimes programs print so that users can see things, and sometimes they
print so that developers can. ``show()`` is for developers, helping rapidly
print the current state of variables in ways that easily identify what
value is being printed, without a lot of wasted effort. It replaces the
craptastic repetitiveness of::

    print "x: {0!r}".format(x)

with::

    show(x)

And if you have a lot of output flowing by, and it's hard
to see your debugging output, try::

    show(x, y, z, style='red')

And now you have debug output that clearly stands out from the rest.

But "debug printing is so very 1989!" you may say.  "We now have logging,
logging, embedded assertions, unit tests, ..." Yes, that's true. But wonderful
as those things are, just showing your current program values is often
what the doctor ordered.

And Much More
=============


While avoiding a few extra characters of typing and a little extra
program complexity is nice (very nice, actually), ``show`` does much
more. As just a taste, ``show.changed()`` displays local values that have
changed since it was last run::

    def f():
        x = 4
        show.changed()
        x += 1
        retval = x * 3
        show.changed()
        return retval

When run will display::

    x: 4
    x: 5  retval: 15

Functions decorated with ``@show.inout`` show you
input parameters as the function is called, then the return
value later.::

    @show.inout
    def g(a):
        b = 3
        a += b
        show.changed()
        return a

    g(4)

Displays::

    g(a=4)
    a: 7  b: 3
    g(a=4) -> 7

(If you want this terser, decorate with ``@show.inout(only='out')``.)

If you run `show.prettyprint()` after importing, or alternatively if
you import with ``from show.pretty import *``, the
`Pygments <http://pygments.org/>`_ syntax highlighter will (if installed),
be used to
colorize data values. This can significantly help
see complex lists and dictionaries.

Finally, ``show`` does normal output too, just like
`say <https://pypi.python.org/pypi/say>`_ (with all of its
high-level text formatting)::

    wizard = "Gandalf"
    show("You have no power here, {wizard}!")

Prints::

    You have no power here, Gandalf!

Long story short, ``show`` is a strong debugging companion that prints the
maximum amount of useful information
with the minimum amount of fuss.

For more, see `the full documentation at Read the Docs
<http://show.readthedocs.org/en/latest/>`_.

New and Notable
===============

Try ``from show.pretty import *``.

IPython is now well-supported, either in a terminal window or a
Jupyter Notebook. In other words, ``show`` now supports interactive
usage. (The plain Python REPL is still only marginally supported, given
significant weaknesses in its introspection support.)

A relatively new capability is to differentially set the formatting parameters on
a method by method basis. For example, if you want to see separators
in green and function call/return annotations in red::

    show.sep.set(style='green')
    show.inout.set(style='red')

You could long do this on a call-by-call basis, but being able to set the
defaults just for specific methods allows you to get more formatting in
with fewer characters typed.  This capability is available on a limited
basis: primarily for format-specific calls (``blanklines``, ``hr``, ``sep``,
and ``title``) and for one core inspection call (the ``inout`` decorator).
It will be extended, and mapped back to underlying ``say`` and ``options``
features over time.


.. warning::
    There are some outstanding issues with Windows.
    Also, when evaluating ``show``, do so
    from a program file or from IPython, not from the plain
    interactive REPL. ``show`` depends on introspection, which
    the plain REPL simply doesn't provide with any quality.
