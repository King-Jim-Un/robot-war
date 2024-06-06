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


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    test_call_kw()
