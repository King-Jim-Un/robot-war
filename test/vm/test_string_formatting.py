import logging

from test.vm import compare_in_vm, dump_func

# Constants:
LOG = logging.getLogger(__name__)


@compare_in_vm
def test_f_strings():
    string = "String"
    integer = 12
    fp_number = 123.45

    print(f"Values: {string} {integer} {fp_number}")
    print(f"Values: {string=} {integer=} {fp_number=}")
    print(f"Values: {string!r}")
    print(f"Values: {string:20}*{integer:-10}*{fp_number:10.4}")


@compare_in_vm
def test_percent():
    a = (12, "banana", 1.2345)
    b = {"foo": "bar", "monty": 12}
    print("1: %d, 2: %-10s, 3: %05.2f" % a)
    print("%(monty)d:%(monty)5d:%(foo)s" % b)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    test_f_strings()
