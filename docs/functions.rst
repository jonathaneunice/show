Function Call and Return
========================

It's often helpful to know what a function's parameters and corresponding
return values were, and it can be annoying to manually print them out.
No matter. Show has two decorators to make this easy::

    @show.inout
    def g(a):
        b = 3
        a += b
        return a

    g(4)

Displays::

    g(a=4)
    g(a=4) -> 7

The first line indicates the function being called. Additional debugging
or program output may follow it.
The second line here is displayed when the
function returns. It reminds us what the parameters were, and then shows
what return value resulted. If you like, you can specify the styling
of these calls, e.g. with ``@show.inout(style='red')``.

While printing both the call entry and exit is often helpful, especially
if many lines of output (or potential program crashes) may intervene. But
in cases where a more compact, "only the results, please" print is desired,
show takes a parameter that will show only function returns:
``@show.inout(only="out")``. Function calls sans
returns will be show if ``only='in'``.

You may find it useful that ``inout`` is an individually-styleable method.
To highlight function entry and exit points, try::

    show.inout.set(style='red')

.. note:: The  ``@show.retval`` decorator has been deprecated, and will soon
    be removed. Please shift to ``@show.inout`` variants instead.
