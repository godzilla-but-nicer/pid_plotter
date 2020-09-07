import pytest
from pid_plotter.pid_plotter import pretty_labels_map

test_label = '((2,), (1, 3))'
test_map = {test_label: '{2}{13}'}

def test_label_map():
    assert pretty_labels_map([test_label]) == test_map