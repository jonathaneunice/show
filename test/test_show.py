
import pytest
from show import Show, NoShow, noshow
from show.exceptions import BadValue
import sys
import platform
import six
import re

# version logic
_PYVER = sys.version_info[:3]
_PY3  = _PYVER >= (3,)
_PY32 = _PYVER[:2] == (3,2)
_PY33 = _PYVER[:2] == (3,3)
_PY36FF = _PYVER >= (3,6)
_PYPY = platform.python_implementation() == 'PyPy'

show = Show(where=False, retvalue=True)

global_var = 'hey!'

def nospaces(s):
    return s.replace(' ', '')


def test_basic(param = 'Yo'):

    a = 1
    b = 3.141
    c = "something else!"

    assert show(a) == 'a: 1'
    assert show(a, b) == 'a: 1  b: 3.141'
    assert show(a, b, c) == "a: 1  b: 3.141  c: 'something else!'"

    assert show(len(c), c) == \
                "len(c): 15  c: 'something else!'"

            # anything with paraens in it must be on separate line, given weak parser
            # of show parameters

def test_clone(param = 'Yo'):

    a = 1
    b = 3.141
    c = "something else!"

    another = show.clone()

    assert another(a) == 'a: 1'
    assert another(a, b) == 'a: 1  b: 3.141'
    assert another(a, b, c) == "a: 1  b: 3.141  c: 'something else!'"

    assert another(len(c), c) == \
                "len(c): 15  c: 'something else!'"


def test_literals():
    # codegen only, not astor
    # assert show(1 + 1) == '1 + 1: 2'
    # assert show(1+1) == '1 + 1: 2'

    # for when using astor as codegen replacement
    assert show(1 + 1) == '(1 + 1): 2'
    assert show(1+1) == '(1 + 1): 2'

    # NB output may have more or fewer spaces than actual parameter, based on codegen.to_source()
    # creating its 'idealized' code output

    # when we were using codegen to recreate source, it did so without parenthesis
    # astor uses parens -- which seem superflous here...but printing literals isn't
    # the main use case, so whatever...

def test_say_params():
    a = 1
    b = 3.141
    c = "something else!"

    assert show(a, indent='+1') == '    a: 1'
    assert show(a, b, sep='\n') == 'a: 1\nb: 3.141'


def test_strings():
    assert show('this') == "this"
    x = 44
    assert show("x = {x}") == 'x = 44'


def test_string_example():

    n = 14312
    assert show("{n} iterations, still running") == "14312 iterations, still running"

    s = '{n} iterations'
    assert show(s) == "s: '{{n}} iterations'"


def test_set():

    s = set([1,2,99])

    # native literals for sets different in py2 and py3
    if _PY3:
        assert show(s) == "s: {{1, 2, 99}}"
    else:
        assert show(s) == "s: set([1, 2, 99])"


def test_show_example():

    x = 12
    nums = list(range(4))

    assert show(x) == 'x: 12'
    assert show(nums) == 'nums: [0, 1, 2, 3]'
    assert show(x, nums, len(nums)) == \
        'x: 12  nums: [0, 1, 2, 3]  len(nums): 4'
    assert show(x, nums, len(nums), indent='+1') == \
        '    x: 12  nums: [0, 1, 2, 3]  len(nums): 4'
    assert show(x, nums, len(nums), sep='\n') == \
        'x: 12\nnums: [0, 1, 2, 3]\nlen(nums): 4'
    assert show(x, nums, len(nums), sep='\n', indent=1) == \
        '    x: 12\n    nums: [0, 1, 2, 3]\n    len(nums): 4'


# @pytest.mark.skipif(True, reason="test broken")
def test_show_items():
    nums = list(range(4))
    assert show.items(nums) == \
        'nums (4 items): [0, 1, 2, 3]'

    astring = 'this'
    assert show.items(astring) == \
        "astring (4 chars): 'this'"


    assert show.items("and this") == \
        "and this"

    x = 33
    assert show.items(x) == "x: 33"

    d = {'a': 1, 'b': 2}
    fstr = show.items(d)
    assert fstr == "d (2 items): {{'a': 1, 'b': 2}}" or \
           fstr == "d (2 items): {{'b': 2, 'a': 1}}"

    # double braces is an odd artifact of Python formatting braces
    # being interpreted by the underlying ``say`` engine. ``show``
    # doubles the braces as a form of quoting. It's likely that
    # we should extend ``say`` (either with an option or a subclass)
    # to optionally NOT interpolate in these cases.


def test_show_dir():

    class R(object):
        x = 4
        def __init__(self):
            self.y = 44
            self._other = 943
    r = R()

    assert show.dir(r) == "r<R>: _other x y"

    if _PY3:
        full_ans = 'r<R>: __class__ __delattr__ __dict__ __dir__ __doc__ __eq__ __format__ __ge__ __getattribute__ __gt__ __hash__ __init__ __le__ __lt__ __module__ __ne__ __new__ __reduce__ __reduce_ex__ __repr__ __setattr__ __sizeof__ __str__ __subclasshook__ __weakref__ _other x y'
    elif _PYPY:
        full_ans = 'r<R>: __class__ __delattr__ __dict__ __doc__ __format__ __getattribute__ __hash__ __init__ __module__ __new__ __reduce__ __reduce_ex__ __repr__ __setattr__ __str__ __subclasshook__ __weakref__ _other x y'
    else:
        full_ans = 'r<R>: __class__ __delattr__ __dict__ __doc__ __format__ __getattribute__ __hash__ __init__ __module__ __new__ __reduce__ __reduce_ex__ __repr__ __setattr__ __sizeof__ __str__ __subclasshook__ __weakref__ _other x y'


    tests = {
        '_*':  "r<R>: x y",
        '__*': "r<R>: _other x y",
        '':    full_ans,
        None:  full_ans,
    }

    for pat, answer in tests.items():
        print("pat:", repr(pat))
        result = show.dir(r, omit=pat)

        prefix_result = show.dir('>>>A PREFIX<<<', r, omit=pat)
        assert prefix_result.replace('>>>A PREFIX<<<' + '  ', '') == result

        space_index = answer.index(' ')
        assert result.startswith(answer[:space_index+1])
        result_rest = set(result[space_index+1:].strip().split())
        answer_rest = set(answer[space_index+1:].strip().split())
        if _PY32:
            answer_rest.discard('__dir__')
        if _PYPY and _PY3:
            answer_rest.discard('__sizeof__')
            result_rest.discard('__locals__')
        if _PY33:
            # seems transiently inlcuded in 33
            result_rest.discard('__locals__')

        if _PY36FF:
            result_rest.discard('__init_subclass__')
        # if assertion fails, pre-computing the symmetric difference
        # will quickly show where the delta was
        arsd = answer_rest ^ result_rest
        assert result_rest == answer_rest

def test_prefix():
    x = 1
    y = 3
    assert show(x, y) == 'x: 1  y: 3'
    assert show(x, y, prefix='> ') == '> x: 1  y: 3'
    show.set(prefix='> ')
    assert show(x, y) == '> x: 1  y: 3'

    show.set(prefix=None)


def col(*items):
    """
    Return hanging column of the given items. Can either
    use *args or pass first item as list. Items should
    be strings. No strinfication attemted.
    """
    if len(items) == 1 and isinstance(items[0], list):
        items = items[0]
    return '\n    '.join(items)


def test_show_props_basic(capsys):

    show = Show(where=False, retvalue=True)

    class O(object):
        name    = 'Bozo'
        age     = 2
        address = 'RAM'

    o = O()
    assert show.props(o) == col('o<O>:',
                                "address='RAM'",
                                "age=2",
                                "name='Bozo'")


    good = 'GOOD'
    longer = show.props('SOMETHING {good}', o)
    longer = longer.replace('SOMETHING GOOD', '').strip()

    assert longer == show.props(o)

    o.stuff = 99
    assert show.props(o) == col('o<O>:',
                                "address='RAM'",
                                "age=2",
                                "name='Bozo'",
                                "stuff=99")


def test_show_dict_props():

    show = Show(where=False, retvalue=True)

    class Dicter(dict):
        pi = '3.14'

    d = Dicter(a=1, b=2)
    ret = show.props(d)
    assert ret == col('d<Dicter>:',  "pi='3.14'" , "a: 1", "b: 2") or \
           ret == col('d<Dicter>:',  "pi='3.14'" , "b: 2", "a: 1")


@pytest.mark.skipif(True, reason="broken")
def test_show_dict_props_later():

    show = Show(where=False, retvalue=True)

    class Dicter(dict):
        pi = '3.14'

    d = Dicter({'a': 1, 'b': 2})

    assert show.props(d, 'pi,a') == col('d<Dicter>:', "pi='3.14'", "a: 1")

    assert show.props(d, 'pi,b') == col('d<Dicter>:', "pi='3.14'", "b: 2")

    assert show(d, props='a,b') == col('d<Dicter>:', "a: 1", "b: 2")


def test_show_props():

    show = Show(where=False, retvalue=True)

    class O(object):
        name    = 'Bozo'
        age     = 2
        address = 'RAM'

    o = O()

    o = O()
    assert show.props(o, 'name, age') == col('o<O>:',
                                             "name='Bozo'",
                                             "age=2")

    assert show.props(o, 'name,address,age') == col('o<O>:',
                                             "name='Bozo'",
                                             "address='RAM'",
                                             "age=2")

    assert show.props(o,'name,age') == show(o, props='name,age')


def test_show_props2():

    class OO(object):
        def __init__(self, name, age, address):
            self.name = name
            self._name = name.upper()
            self.age  = age
            self.address = address
        def test(self):
            return self.age > 17
        def best(self):
            return self.name.capitalize()

    oo = OO('Joe', 36, 'Waverly Place')

    oo_answer = col('oo<OO>:', "address='Waverly Place'",
                    "age=36", "name='Joe'", "_name='JOE'")

    assert show.props(oo) == oo_answer


def test_show_real_properties():

    class P(object):
        def __init__(self, name):
            self._name = name.upper()
            self.name = name
        @property
        def namer(self):
            return self._name.lower()
        def named(self):
            return self.name

    p = P('Joe')
    assert show.props(p) == "p<P>:\n    name='Joe'\n    namer='joe'\n    _name='JOE'"


def test_show_locals():
    x = 1
    y = 2
    assert show.locals() == 'x: 1  y: 2'

    a = 22
    b = 23
    assert show.locals(omit='x') == 'a: 22  b: 23  y: 2'
    # assert show.locals(global_var) == "global_var: 'hey!'  x: 1  y: 2"


def test_show_changed():
    x = 1
    assert show.changed() == 'x: 1'
    y = 2
    assert show.changed() == 'y: 2'
    assert show.changed() == 'no changes'
    x = 4
    assert show.changed() == 'x: 4'
    assert show.changed() == 'no changes'
    x = 5
    y = 3
    # _z = 99

    changed = show.changed()
    assert changed == 'x: 5  y: 3' or changed == 'y: 3  x: 5'

    # assert show.changed() == six.u('\u2205')

    # assert show.changed(_z) == '_z: 99'
    # assert show.changed() == six.u('\u2205')


def test_show_flag():
    """
    Test that the show keyword argument actually turns showing on or off.
    """
    x = 1

    # NB the retvalue setting is set to same as the show attribute because
    # here in this testing situation, we're testing the return not the pure
    # output


    # Test instance on-off
    assert show(x) == 'x: 1'
    assert show(x, show=True, retvalue=True) == 'x: 1'
    assert show(x, show=False, retvalue=False) == None

    # Now test global on-off settings, and instance overrides

    show.set(show=False, retvalue=False)
    assert show(x) == None
    assert show(x, show=True, retvalue=True) == 'x: 1'
    show.set(show=True, retvalue=True)
    assert show(x) == 'x: 1'
    assert show(x, show=False, retvalue=False) == None

    # Now test that clones are independently controllable
    if False:
        show_verbose = show.clone()
        show(show_verbose.options)
        assert show(x * 5) == 'x * 5: 5'
        assert show_verbose(x * 5) == 'x * 5: 5'

        show_verbose.set(show=False, retvalue=False)
        assert show(x * 6) == 'x * 6: 6'
        assert show_verbose(x * 6) == None
        show.set(show=False, retvalue=False)
        assert show(x * 7) == None
        assert show_verbose(x * 7) == None
        show.set(show=True, retvalue=True)
        assert show(x * 8) == 'x * 8: 8'
        assert show_verbose(x * 8) == None
        show_verbose.set(show=True, retvalue=True)
        assert show(x * 9) == 'x * 9: 9'
        assert show_verbose(x * 9) == 'x * 9: 9'

        # Now test lambda expressions for showing
        debug = True
        assert show(x * 5) == 'x * 5: 5'
        show.set(show=lambda: debug)
        show.props(show.options, omit='_*')
        assert show.options.show() == debug
        assert debug == True
        assert show(x * 5) == 'x * 5: 5'
        debug = False
        assert show(x * 5) == None

    # clean up for rest of testing
    debug = True
    show.set(show=True)


def test_show_settings():
    x = 1
    assert show(x) == 'x: 1'
    with show.settings(show=False):
        assert show(x) == None


def test_noshow_settings():
    x = 1
    assert noshow(x) == None
    with noshow.settings(show=False):
        assert noshow(x) == None
    with noshow.settings(show=True):
        assert noshow(x) == None
        # noshow is inert - not really modifiable on the fly
        # intended as black hole


def test_show_retval(capsys):

    show = Show(where=False, retvalue=True)

    # this tweak needed to make pytest's capsys work right
    show.say.setfiles([sys.stdout])

    @show.retval
    def f(a):
        return a + 1

    assert f(12) == 13
    out, err = capsys.readouterr()
    assert out.splitlines()[2] == "f(a=12) -> 13"
            # ^^^^^^^^^^^^^^^^ skip the deprecation warning
    assert err == ""


def test_show_inout(capsys):

    show = Show(where=False, retvalue=True)

    # this tweak needed to make pytest's capsys work right
    show.say.setfiles([sys.stdout])

    # basic test
    @show.inout
    def f(a):
        return a + 1

    assert f(12) == 13
    out, err = capsys.readouterr()
    assert out == "f(a=12)\nf(a=12) -> 13\n"
    assert err == ""

    # test only in
    @show.inout(only='in')
    def fin(a):
        return a + 1

    assert fin(12) == 13
    out, err = capsys.readouterr()
    assert out == "fin(a=12)\n"
    assert err == ""

    # test only out
    @show.inout(only='out')
    def fout(a):
        return a + 1

    assert fout(12) == 13
    out, err = capsys.readouterr()
    assert out == "fout(a=12) -> 13\n"
    assert err == ""

    # test that formatting works
    @show.inout(indent='+1')
    def findent(a):
        return a + 1

    assert findent(12) == 13
    out, err = capsys.readouterr()
    assert out == "    findent(a=12)\n    findent(a=12) -> 13\n"
    assert err == ""


def test_show_where(capsys):

    show = Show(where=False, retvalue=True)

    # this tweak needed to make pytest's capsys work right
    show.say.setfiles([sys.stdout])

    show.where()
    out, err = capsys.readouterr()

    assert re.match(r'test_show_where\(\):\d+:\s*\n', out)
    assert err == ""


# Does not test interactive usage (under ipython, eg) in any automated fashion.
# Nor does it test the formatted output through Pygments and pformat.


def test_noshow(capsys):
    show = Show(where=False, retvalue=True)
    show = noshow
    # this tweak needed to make pytest's capsys work right
    show.say.setfiles([sys.stdout])

    out, err = capsys.readouterr()
    assert show('this') is None
    assert out == ""
    assert err == ""

    othernoshow = noshow.clone()
    othernoshow.say.setfiles([sys.stdout])
    show = othernoshow
    assert show('this') is None
    assert out == ""
    assert err == ""



ANSIRE = re.compile('\x1b.*?m')

def deansi(s):
    """
    Quick and dirty routine to remove ANSI control
    strings from a given string.
    """
    return ANSIRE.sub('', s)


def test_show_prettyprint():
    show.prettyprint(sep=' | ')
    show.set(retval=True)
    x = 13
    y = 22
    out = show(x)
    assert deansi(out) == u'\u25a0  x: 13'

    out = show(x,y)
    assert deansi(out) == u'\u25a0  x: 13 | y: 22'

    show.prettyprint(mode='text', sep=' | ', prefix='')
    out = show(x,y)
    assert out == 'x: 13 | y: 22'

    with pytest.raises(BadValue):
        show.prettyprint(mode='YAML')

def test_pprint(capsys):

    show = Show(where=False, retvalue=True)

    # this tweak needed to make pytest's capsys work right
    show.say.setfiles([sys.stdout])

    d = [1, 3, "this"]
    show.pprint(d)
    out, err = capsys.readouterr()
    assert out == "[1, 3, 'this']\n"
    assert err == ""


# FIXME: This will FAIL on dictionaries, because of the escaping issue


def test_blank_lines(capsys):

    show = Show(where=False, retvalue=True)

    # this tweak needed to make pytest's capsys work right
    show.say.setfiles([sys.stdout])

    show.blank_lines(3)
    out, err = capsys.readouterr()
    assert out == "\n\n\n"
    assert err == ""


def test_hr(capsys):

    show = Show(where=False, retvalue=True)

    # this tweak needed to make pytest's capsys work right
    show.say.setfiles([sys.stdout])

    show.hr(char="=", width=4)
    out, err = capsys.readouterr()
    assert out == "====\n"
    assert err == ""


def test_title(capsys):

    show = Show(where=False, retvalue=True)
    show.sep.set(vsep=(1,0))
    show.title.set(vsep=1)

    # this tweak needed to make pytest's capsys work right
    show.say.setfiles([sys.stdout])

    show.title('section', char="=", width=4)
    out, err = capsys.readouterr()
    assert out == "\n==== section ====\n\n"
    assert err == ""


def test_title_mkwargs(capsys):

    show = Show(where=False, retvalue=True)
    show.sep.set(vsep=(1,0))
    show.title.set(vsep=1)

    # this tweak needed to make pytest's capsys work right
    show.say.setfiles([sys.stdout])

    show.title('section', char="=", width=4)
    out, err = capsys.readouterr()
    assert out == "\n==== section ====\n\n"
    assert err == ""

    show.title.set(char="*", width=5)
    show.title('section')
    out, err = capsys.readouterr()
    assert out == "\n***** section *****\n\n"
    assert err == ""


def test_sep(capsys):

    show = Show(where=False, retvalue=True)
    show.sep.set(vsep=(1,0))
    show.title.set(vsep=1)

    # this tweak needed to make pytest's capsys work right
    show.say.setfiles([sys.stdout])

    show.sep('one', char="=", width=4)
    out, err = capsys.readouterr()
    assert out == "\n==== one\n"
    assert err == ""

def test_sep_mkwargs(capsys):

    show = Show(where=False, retvalue=True)
    show.sep.set(vsep=(1,0))
    show.title.set(vsep=1)

    # this tweak needed to make pytest's capsys work right
    show.say.setfiles([sys.stdout])

    show.sep.set(char="=", width=4)
    show.sep('one')
    out, err = capsys.readouterr()
    assert out == "\n==== one\n"
    assert err == ""

    show.sep.set(vsep=(1,1), char='*')
    show.sep('two')
    out, err = capsys.readouterr()
    assert out == "\n**** two\n\n"
    assert err == ""

def test_settings_noshow(capsys):
    """
    Had some trouble where the formatting routines (e.g.
    sep. title, hr, blank_lines) were not properly responding
    to show=False in a transient context, based on the way their
    core implementation was "forwarded" to the say module. This
    test is a regression bulwark to make sure that that these
    routines specifically remember when to show and not show.
    """
    show = Show(where=False, retvalue=True)
    show.say.setfiles([sys.stdout])
    out, err = capsys.readouterr()

    show.sep.set(vsep=(1,1), char='*')

    show.sep('two')
    out, err = capsys.readouterr()
    assert out == "\n**** two\n\n"
    assert err == ""

    with show.settings(show=False):
        show.sep('two')
        out, err = capsys.readouterr()
        assert out == ""
        assert err == ""

    with show.settings(show=False):
        show.hr()
        out, err = capsys.readouterr()
        assert out == ""
        assert err == ""

    with show.settings(show=False):
        show.title('this')
        out, err = capsys.readouterr()
        assert out == ""
        assert err == ""

    with show.settings(show=False):
        show.blank_lines(5)
        out, err = capsys.readouterr()
        assert out == ""
        assert err == ""
