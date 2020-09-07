import pytest
from pid_plotter.pid_plotter import PID_sets, contains_subsets, exclude_subsets, powerset

POS_SET = [(1, 2), (2, 3), (2,)]
NEG_SET = [(1, 2), (2, 3)]

def test_powerset():
    assert list(powerset([1, 2])) == [(1,), (2,), (1, 2)]

def test_contains_subsets_pos():
    assert contains_subsets(POS_SET) == True

def test_contains_subsets_neg():
    assert contains_subsets(NEG_SET) == False

def test_exclude_subsets_pos():
    assert exclude_subsets(POS_SET) == NEG_SET

def test_exclude_subsets_neg():
    assert exclude_subsets(NEG_SET) == NEG_SET