import logging

from test.vm import compare_in_vm, dump_func

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


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    test_call_method()
