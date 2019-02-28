What's Changed
==============

::

    show.changed()

will display the value of local variables. When invoked again, only those
variables that have changed (since the last ``show.changed()`` in the same context)
will be displayed. For example::


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

You may ``omit`` some local variables if you like.
By default, those starting with underscores (``_``) will be omitted, as
will those containing functions, methods, builtins, and other parts Python
program infrastructure. If you'd like to add those, or global variables into
the mix, that's easily done::

    show.changed(_private, MY_GLOBAL_VAR)

Will start watching those.

