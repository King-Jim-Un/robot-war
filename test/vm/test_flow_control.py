import logging
from unittest import TestCase

from test.vm import compare_in_vm, run_in_vm, dump_func

# Constants:
LOG = logging.getLogger(__name__)


def func(a, b):
    return a + b


@compare_in_vm([func])
def test_call():
    return func(1, 2) + 3


@compare_in_vm([func])
def test_call_kw():
    return func(b=1, a=2) + 3


class MyClass:
    a = 1

    def b(self, c):
        return self.a + c


@compare_in_vm([MyClass])
def test_call_method():
    d = MyClass()
    return d.b(2)


@compare_in_vm
def test_jumps_1():
    """JUMP_ABSOLUTE & POP_JUMP_IF_FALSE"""
    a = 1
    while a < 5:
        print(a)
        a += 1
    return a


@run_in_vm
def raise_exception():
    raise IndexError()


class TestFlowControl(TestCase):
    def test_exception(self):
        with self.assertRaises(IndexError):
            raise_exception()


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    TestFlowControl().test_exception()
