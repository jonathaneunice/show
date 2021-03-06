from show.util import *
import re

def test_omitnames():
    """
    Make sure the basic omission helper works
    """

    def qw(data):
        """
        Quote words. Thanks, Perl!
        """
        return data.split() if isinstance(data, str) else data

    def check_list(lst, tests):
        lst = qw(lst)
        for pat, answer in tests.items():
            answer = qw(answer)
            assert omitnames(lst, pat, sort=False) == answer
            assert omitnames(lst, pat, sort=True) == sorted(answer)
            assert omitnames(lst, pat) == sorted(answer)

    L1 = 'one two three four five six seven'
    L1_tests = {
        'one': 'two three four five six seven',
        't*':  'one four five six seven',
        't* s*': 'one four five',
        't* f* s*': 'one',
        '*o*':  'three five six seven',
        '*': []
    }

    check_list(L1, L1_tests)

    L2 = '_this __that something_else _and __or__'
    L2_tests = {
        'one': L2,
        '_*': 'something_else',
        '__*': '_this something_else _and',
        '*_': '_this __that something_else _and',
        'and': L2,
        '*and': '_this __that something_else __or__'
    }

    check_list(L2, L2_tests)


def test_lambda_eval():

    noncallables  = [4, 4.5, 5+7j, [], {}, set()]
    for nc in noncallables:
        assert lambda_eval(nc) == nc

    x = 12
    assert lambda_eval(x) == x
    assert lambda_eval(lambda: x) == x
    assert lambda_eval(lambda: x < 10) == False
    assert lambda_eval(lambda: x > 10) == True


def test_wrapped_if():

    assert wrapped_if(None) == ""
    assert wrapped_if("") == ""

    upper = lambda x : x.upper()

    assert wrapped_if(None, 'A', 'B', upper) == ""
    assert wrapped_if("", 'A', 'B', upper) == ""

    assert wrapped_if("yes", 'A', 'B', upper) == "AYESB"
    assert wrapped_if("yes", 'A', 'B', None) == "AyesB"
    assert wrapped_if("yes", 'A', None, None) == "Ayes"
    assert wrapped_if("yes", 'A', None, upper) == "AYES"
    assert wrapped_if("yes", None, 'B', upper) == "YESB"
    assert wrapped_if("yes", None, 'B', None) == "yesB"


def test_words():
    assert words(None) == []
    assert words([]) == []
    assert words('a b c'.split()) == 'a b c'.split()
    assert words('a,b,c') == 'a b c'.split()
    assert words('  a,b,c ') == 'a b c'.split()
    assert words('  a , b ,c ') == 'a b c'.split()
    assert words('  a  b  c ') == 'a b c'.split()


def test_ellipsis():
    assert ellipsis("") == ""
    assert ellipsis("andy", maxlen=10) == "andy"
    assert ellipsis("mandypandy", maxlen=10)  == "mandypandy"
    assert ellipsis("mandypandy1", maxlen=10) == "mandypa..."
    assert ellipsis("this is a very long string", maxlen=10) == "this is..."
