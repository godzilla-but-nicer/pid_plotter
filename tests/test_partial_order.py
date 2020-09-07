import pytest
from pid_plotter.pid_plotter import partial_order

set_alpha_pos = ((2,), (3,))
set_alpha_neg = ((2,),)
set_beta = ((1, 2), (3,))

def test_partial_order_pos():
    assert partial_order(set_alpha_pos, set_beta)

def test_partial_order_neg():
    assert not partial_order(set_alpha_neg, set_beta)
