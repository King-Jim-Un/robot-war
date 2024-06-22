import logging
from unittest import TestCase

from test.vm import compare_in_vm, run_in_vm, dump_func

# Constants:
LOG = logging.getLogger(__name__)


class Base1:
    a = 1

    def b(self):
        return self.a


class Base2:
    c = 2

    def d(self):
        return self.c


class Sub1(Base1):
    def e(self, x: int):
        return self.b() + x


class Sub2(Base1, Base2):
    def f(self):
        return self.b() + self.d()


@compare_in_vm([Base1, Sub1])
def test_no_inheritance():
    """LOAD_BUILD_CLASS, MAKE_FUNCTION, STORE_NAME, LOAD_NAME, LOAD_ATTR, LOAD_METHOD, and CALL_METHOD"""
    obj = Base1()
    print(hasattr("hello", "upper"))
    return obj.b()


@compare_in_vm([Base1, Sub1, Base2, Sub2])
def test_single_inheritance():
    obj = Sub1()
    return obj.e(5)


@compare_in_vm([Base1, Sub1, Base2, Sub2])
def test_double_inheritance():
    """STORE_ATTR"""
    obj = Sub2()
    obj.a = 10
    return obj.f()


@compare_in_vm([Base1, Sub1, Base2, Sub2])
def test_isinstance():
    print(isinstance("hello", int))
    print(isinstance("hello", str))
    obj = Base1()
    print(isinstance(obj, Base1))
    print(isinstance(obj, Sub1))
    obj = Sub1()
    print(isinstance(obj, Base1))
    print(isinstance(obj, Sub1))
    print(isinstance(obj, Sub2))
    obj = Sub2()
    print(isinstance(obj, Base1))
    print(isinstance(obj, Sub1))
    print(isinstance(obj, Sub2))


@compare_in_vm([Base1, Sub1, Base2, Sub2])
def test_hasattr():
    obj = Base1()
    print(hasattr(obj, "b"))
    print(hasattr(obj, "e"))
    obj = Sub1()
    print(hasattr(obj, "b"))
    print(hasattr(obj, "e"))
    obj = Sub2()
    print(hasattr(obj, "a"))
    print(hasattr(obj, "d"))
    print(hasattr(obj, "f"))


# TODO:  super

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    test_no_inheritance()
