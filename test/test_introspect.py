
import os, random, string
from textdata import lines, textlines

# --- TEST FIXTURES ---

ALPHABET = string.ascii_lowercase + string.digits

def tempfile(text, tmpdir):
    """
    Make a temporary file.
    :text: Text contents to add to the file.
    :name: File name. If None, chosen randomly.
    """
    name = ''.join(random.choice(ALPHABET) for i in range(12)) + '.py'
    p = tmpdir.join(name)
    p.write(textlines(text))
    return p

# --- END TEST FIXTURES ---

from show.introspect import *

CallArgs.add_target_func('show')

def test_callargs_one(tmpdir):
    p = tempfile("""
        def func():
            x = 12
            show(x)
    """, tmpdir=tmpdir)

    assert CallArgs(p.strpath, 3).args == ['x']

def test_callargs_two(tmpdir):
    p = tempfile("""
        def func():
            x = 12
            y = 99
            show(x, y)
    """, tmpdir=tmpdir)

    assert CallArgs(p.strpath, 4).args == ['x', 'y']

def test_callargs_three(tmpdir):
    p = tempfile("""
        def func():
            x = 12
            y = 99
            show(x, y, x)
    """, tmpdir=tmpdir)

    assert CallArgs(p.strpath, 4).args == ['x', 'y', 'x']

def test_callargs_four(tmpdir):
    p = tempfile("""
        def func(x, z):
            def nested(y):
                show.dir(x, y, z)
            y = 99
            show(y, x)
    """, tmpdir=tmpdir)

    assert CallArgs(p.strpath, 3).args == ['x', 'y', 'z']
    assert CallArgs(p.strpath, 5).args == ['y', 'x']


def test_ClassProps():
    c = ClassProps(dict)
    assert 'keys' in c.props
    assert c.mro == (dict, object)

    class Slotted(object):
        __slots__ = ['a', 'b']

    cs = ClassProps(Slotted)
    assert 'a' in cs.props
    assert 'b' in cs.props


def test_class_props():
    assert 'keys' in class_props(dict)

    class Slotted(object):
        __slots__ = ['a', 'b']

    cps = class_props(Slotted)
    assert 'a' in cps
    assert 'b' in cps
