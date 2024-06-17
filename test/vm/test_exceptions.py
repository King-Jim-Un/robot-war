import logging
from unittest import TestCase

from test.vm import compare_in_vm, run_in_vm, dump_func

# Constants:
LOG = logging.getLogger(__name__)


@run_in_vm
def raise_exception():
    raise IndexError()


class TestException(TestCase):
    def test_exception(self):
        with self.assertRaises(IndexError):
            raise_exception()


@compare_in_vm
def test_exception1():
    print("before exception")
    try:
        raise IndexError()
    except IndexError:
        print("in exception")


@compare_in_vm
def test_exception2():
    print("before exception")
    try:
        raise IndexError("err msg")
    except IndexError as error:
        print("in exception" + repr(error))


@compare_in_vm
def test_exception3():
    print("before exception")
    try:
        raise IndexError("err msg")
    except ZeroDivisionError:
        print("in wrong error")
    except (IOError, IndexError) as error:
        print("in exception" + repr(error))


@compare_in_vm
def test_exception4():
    print("before exception 1")
    try:
        print("before exception 2")
        try:
            raise IndexError("err msg")
        except ZeroDivisionError:
            print("in wrong error")
        print("between exceptions")
    except IndexError:
        print("in exception")
    finally:
        print("in finally")


@compare_in_vm
def test_exception5():
    print("before exception 1")
    try:
        print("before exception 2")
        try:
            raise IndexError("err msg")
        except IndexError:
            print("in first exception")
            raise
        print("between exceptions")
    except IndexError:
        print("in second exception")


def sub2():
    print("in sub2")
    raise IndexError("an index error")


def sub1():
    print("in sub1")
    sub2()


@compare_in_vm([sub1, sub2])
def test_exception6():
    print("before exception")
    try:
        sub1()
    except IndexError:
        print("in exception")


class With1:
    def __init__(self):
        print("with1 constructor")

    def __enter__(self):
        print("enter with1")

    def __exit__(self, exc_type, exc_val, exc_tb):
        print("exit with1" + repr(exc_val))
        return True  # exception handled


class With2:
    def __init__(self):
        print("with2 constructor")

    def __enter__(self):
        print("enter with2")

    def __exit__(self, exc_type, exc_val, exc_tb):
        print("exit with2" + repr(exc_val))


@compare_in_vm
def test_with1():
    with With1():
        print("using with")
        raise IndexError("the error")
    print("done")


@compare_in_vm
def test_with2():
    try:
        with With2():
            print("using with")
            raise IndexError("the error")
    except IndexError as err:
        print("handler" + repr(err))
    print("done")


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    test_exception2()
