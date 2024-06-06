import logging

from test.vm import compare_in_vm, dump_func

# Constants:
LOG = logging.getLogger(__name__)


@compare_in_vm
def test_addition():
    a = 1
    b = 2
    return a + b


@compare_in_vm
def test_multiplication():
    a = 1
    b = 2
    return a * b


@compare_in_vm
def test_subtraction():
    a = 1
    b = 2
    return a - b


@compare_in_vm
def test_division():
    a = 1.0
    b = 2.0
    return a / b


@compare_in_vm
def test_int_divide():
    a = 21
    b = 4
    return a // b


@compare_in_vm
def test_in():
    a = "quick brown fox"
    b = "brown"
    return b in a


@compare_in_vm
def test_not_in():
    a = "quick brown fox"
    b = "brown"
    return b not in a


@compare_in_vm
def test_is():
    a = "quick "
    b = "brown"
    c = a + b
    d = a + b
    return c is d


@compare_in_vm
def test_is_not():
    a = "quick "
    b = "brown"
    c = a + b
    d = a + b
    return c is not d


@compare_in_vm
def test_invert():
    a = 1234
    return ~a


@compare_in_vm
def test_negative():
    a = 1234
    return -a


@compare_in_vm
def test_not():
    a = True
    return not a
