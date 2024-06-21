import logging

from test.api import run_in_vm

# Constants:
LOG = logging.getLogger(__name__)


@run_in_vm
def test_time():
    from time import monotonic, sleep

    t1 = monotonic()
    assert t1 > 0.0
    sleep(0.001)
    t2 = monotonic()
    assert t2 > t1


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    test_time()
