
class Hint(object):
    """
    Hints capture ways of displaying variables.
    """
    def __init__(self, name=None, value=None, repr_func=None):
        self.name = name
        self.value = value
        self.repr_func = repr_func
        self.params = {}

    def render(self):
        """
        Actually do the repr of value.
        """
        pass

    def __call__(self, **kwargs):
        self.params = kwargs
        # or should it be an options Object?

    def __rtruediv__(self, other):
        """
        Right division so that we can say things like
        show(x /dir) or show(x /props) or show(s /chars)
        """
        pass

    if _PY2:
        __rdiv__ = __rtruediv__

    def __neg__(self):
        pass

    def __pos__(self):
        pass

    # reminder that unary functions are possible

props = Hint()
