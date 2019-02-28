Object Properties
=================

::

    show.props(x)

shows the properties of object ``x``. ("Properties" here
is generic language for "values" or "attributes" associated with
an object, and isn't used in the technical sense of Python properties.)
Properties will be listed alphabetically, but with those starting with underscores
(``_``), usually indicating "private" data, sorted after those that are
conventionally considered public.

If ``x`` has real ``@property`` members, those too displayed. However, other class
attributes that ``x`` rightfully inherits, but that are not directly present in the
``x`` instance, will not be displayed.

An optional second
parameter can determine which properties are shown. E.g.::

    show.props(x, 'name,age')

Or if you prefer the keyword syntax, this is equivalent to::

    show(x, props='name,age')

Or if you'd like all properties except a few::

    show.props(x, omit='description blurb')

