Collections and Items
=====================

The goal of ``show`` is to provide the most useful information possible,
in the quickest and simplest way. Not requiring programmers to explicitly
restate values and names in print statements is the start, but it also
provides some additional functions that provide a bit more semantic value.
For example, ``say.items()`` is designed to make printing collections easy.
It shows not just the values, but also the cardinality (i.e., length) of the
collection::

    nums = list(range(4))
    show.items(nums)

yields::

    nums (4 items): [0, 1, 2, 3]

