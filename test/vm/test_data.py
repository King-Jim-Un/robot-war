import logging

from test.vm import compare_in_vm, dump_func

# Constants:
LOG = logging.getLogger(__name__)


@compare_in_vm
def test_slice():
    """BUILD_SLICE or BINARY_SLICE"""
    a = "quick brown fox"
    print(a[:])
    print(a[5:])
    print(a[:15])
    print(a[5:15])
    print(a[-10:])
    print(a[:-5])
    print(a[-10:-5])


@compare_in_vm
def test_subscr():
    """BUILD_LIST, LIST_EXTEND and BINARY_SUBSCR"""
    a = [10, 20, 30]
    print(a[1])


@compare_in_vm
def test_build_const_key_map():
    a = {"1": 2, "3": 4}
    print(a)


@compare_in_vm
def test_set():
    """BUILD_SET and SET_UPDATE"""
    a = {1, 2, 3}
    a.add(4)
    print(a)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    test_set()
