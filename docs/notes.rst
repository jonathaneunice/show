Notes
=====

* ``show`` is in its early days. Over time, it will provide additional
  context-specific output helpers. For example, the "diff" views of ``py.test``
  seem a high-value enhancement.

* ``show`` depends on introspection, with its various complexities and
  limitations. It assumes that all objects are new-style classes, and that
  your program has not excessively fiddled with class data. Diverge from these
  assumptions, and all bets are off.

* Automated multi-version testing managed with the wonderful `pytest
  <http://pypi.python.org/pypi/pytest>`_ and `tox
  <http://pypi.python.org/pypi/tox>`_. Successfully packaged for, and
  tested against, most late-model versions of Python: 2.7, 3.3,
  3.4, 3.5, and 3.6, as well as PyPy 5.6.0 (based on 2.7.12) and PyPy3 5.5.0
  (based on 3.3.5).

* The author, `Jonathan Eunice <mailto:jonathan.eunice@gmail.com>`_ or
  `@jeunice on Twitter <http://twitter.com/jeunice>`_
  welcomes your comments and suggestions.
