import logging

from test.vm import compare_in_vm, dump_func

# Constants:
LOG = logging.getLogger(__name__)

# Globals:
G_GLOBAL = 20


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
    """BUILD_LIST, LIST_EXTEND, STORE_SUBSCR, and BINARY_SUBSCR"""
    a = [10, 20, 30]
    a[1] = 5
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


@compare_in_vm
def test_build_tuple():
    a = "one"
    b = "two"
    c = "three"
    d = (a, b, c)
    print(d)


@compare_in_vm
def test_compare():
    """COMPARE_OP and IS_OP"""
    a = "one"
    b = "two"
    print(a < b)
    print(a <= b)
    print(a > b)
    print(a >= b)
    print(a == b)
    print(a != b)
    print(a is b)
    print(a is not b)


@compare_in_vm(global_vars={"G_GLOBAL": 10})
def test_delete():
    """DELETE_SUBSCR, DELETE_FAST, and DELETE_GLOBAL"""
    global G_GLOBAL

    a = [1, 2, 3, 4]
    print(a)
    del a[2]
    print(a)
    del a
    del G_GLOBAL


@compare_in_vm
def test_closure():
    """STORE_DEREF, LOAD_CLOSURE, LOAD_DEREF"""
    a = 10

    def b(c):
        return a + c

    print(b(20))


@compare_in_vm(global_vars={"G_GLOBAL": 10})
def test_store_global():
    global G_GLOBAL

    G_GLOBAL = 1


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    test_set()
