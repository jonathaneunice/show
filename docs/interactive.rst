Interactive Limitations
=======================

As of version 1.4, ``show`` has good support for IPython, whether running in a
terminal window or a Jupyter Notebook.

Support for the plain interactive Python REPL is *much* weaker. Call it
experimental. It works well at the interactive prompt, and within imported
modules. It cannot, however, be used within functions and classes defined within
the interactive session. This is a result of how Python supports--or rather,
fails to support--introspection for interactively-defined code. Whether this is
a hard limit, or something that can be worked around over time, remains to be
seen. (See e.g. `this discussion
<http://stackoverflow.com/questions/13204161/how-to-access-the-calling-source-line-from-interactive-shell>`_).

However, given how good and supportive
IPython and Jupyter Notebook are as interactive
workspaces, it's a mystery why you're still using the stock Python REPL.
Seriously!
If you want to work interactively, do so uner IPython or
Jupyter Notebook, which are excellent in ways
the stock REPL never will be.


Python under Windows does not support readline the same way it is supported on
Unix, Linux, and Mac OS X. Experimental support is provided for the use of
``pyreadline`` under Windows to correct this variance. This feature is yet
untested. Works/doesn't work reports welcome! (I do not have a Windows system
to test from, so Windows is a lagging environment at present.)
