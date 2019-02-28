Discovering What's There
========================

It's often helpful to figure out "what am I dealing with here? what attributes
or methods or properties are available to me?" This is where ``show.dir`` comes
into play. You could do ``show(dir(x))``, but ``show.dir(x)`` will provides more
information, and does so more compactly. It also allows you to filter out the
often huge hubbub of some objects. By default, it doesn't show any attributes
starting with double underscore ``__``. You can control what's omitted with the
``omit`` keyword argument. ``show.dir(x, omit=None)`` shows everything, while
``show.dir(x, omit='_* proxy*')`` omits all the methods starting with an
underscore or the word "proxy."

