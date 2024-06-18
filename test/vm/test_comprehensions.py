import logging

from test.vm import compare_in_vm, dump_func

# Constants:
LOG = logging.getLogger(__name__)


# @dump_func
@compare_in_vm
def test_list():
    print([i * 3 for i in range(10) if i > 5])


@compare_in_vm
def test_set():
    print({i * 3 for i in range(10) if i < 5})


@compare_in_vm
def test_dict():
    print({str(i): i * 3 for i in range(10) if i < 5})


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    logging.getLogger("robot_war.vm.exec_context").setLevel(logging.WARNING)  # push/pop values
    test_dict()
