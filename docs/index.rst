show
====

``show`` provides simple, effective debug printing.

Every
language has features to print text, but they're seldom optimized for
printing debugging information. ``show`` is. It provides a simple, DRY
mechanism to "show what's going on"--to identify what
values are associated with program variables in a neat,
labeled fashion. For instance::

    from show import show

    x = 12
    nums = list(range(4))

    show(x, nums)

yields::

    x: 12  nums: [0, 1, 2, 3]

You could of course get the same output with Python's standard
``print`` statement/function::

    print("x: {}  nums: {}".format(x, nums))

But that's much more verbose, and unlike ``show``, it's fails the
`DRY
<https://en.wikipedia.org/wiki/Don%27t_repeat_yourself>`_ principle.

But while avoiding a few extra characters of typing and a little extra
program complexity is nice--very nice, actually--``show`` goes well beyond
that. It has methods to show all local variables which have recently
changed, to trace the parameters and return values of function calls, and
other useful information that you simply cannot get without a lot of
needless extra work and a lot of extra lines mucking up your program source.
And if you run ``show.prettyprint()``, values will be
automagically highlighted with `Pygments <http://pygments.org/>`_, which is
very helpful when you're displaying complex objects, dictionaries and
other structures.

As just one exmaple, if you have a lot of output flowing by, and it's hard
to see your debugging output, just::

    show(x, y, z, style='red')

And now you have debug output that clearly stands out from the rest. Or
``show.set(style='blue')`` and now all your debug output is colorized.

But "debug printing is so very 1989!" you may say.  "We now have logging,
logging, embedded assertions, unit tests,
interactive debuggers. We don't need debug printing."

Have to disagree with you there. All those tools are grand, but often
the fastest, simplest way to figure out what's going in a program
is to print values
and watch what happens the program runs. Having a simple, effective way
to do that doesn't replacing logging, assertsions, unit testing, and
debuggers; it's a effective complement to them. One that is especially
useful in two parts of the development process:

1. In exploratory programming, where the values coming back from new
   or external functions (say, some package's API with which you may
   not be intimately familiar) aren't well-known to you.
2. In debugging, where the assumptions embedded into the code are
   clearly, at some level, not being met. Else you wouldn't need to
   debug.

In either case, knowing what values are actually happening, and figuring
them out without a lot of extra effort or complexity--well, it doesn't matter
how many unit tests or logging statements you have, that's still of value.

Every
language has features to print text, but they're seldom optimized for
printing debugging information. ``show`` is. It provides a simple, DRY
mechanism to "show what's going on."

.. toctree::
   :titlesonly:

   Diving In <divingin>
   Collections and Items <collections>
   Object Properties <properties>
   Wax On, Wax Off <waxonoff>
   How Things Are Shown <howshown>
   Where Am I? <whereami>
   What's Changed <whatchanged>
   Function Call and Return <functions>
   Discovering What's There <discovering>
   Interactive Limitations <interactive>
   api
   notes
   installation
   CHANGES
