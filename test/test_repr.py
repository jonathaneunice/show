import pytest
from show.repr import *


def test_typename_basic():
    assert typename(4) == '<int>'
    assert typename(4.5) == '<float>'
    assert typename(5+7j) == '<complex>'
    assert typename([]) == '<list>'
    assert typename({}) == '<dict>'
    assert typename(set()) == '<set>'


def test_typename_classes():

    class R(object): pass
    r = R()

    assert typename(R) == '<type>'
    assert typename(r) == '<R>'

    def nested():
        class RR(object): pass
        assert typename(RR) == '<type>'
        r2 = RR()
        assert typename(r2) == '<RR>'

    nested()


def test_ReprStr():
    assert ReprStr('this') == 'this'
    assert ReprStr(repr('this')) == "'this'"
    assert ReprStr('1') == '1'
    assert ReprStr(ReprStr('1')) == '1'
    assert ','.join([ReprStr('1'), ReprStr('2')]) == '1,2'
