import logging

from robot_war.constants import CONSTANTS
from test.vm import compare_external

# Constants:
LOG = logging.getLogger(__name__)


def test_import_a():
    compare_external("ext0", ["ext1a", "func1a"])


def test_import_b():
    compare_external("ext0", ["ext1a", "func1b"])


def test_import_c():
    compare_external("ext0", ["ext1a", "func1c"])


def test_import_d():
    compare_external("ext0", ["ext1a", "func1d"])


def test_import_e():
    compare_external("ext0", ["ext1a", "func1e"])


def test_import_f():
    compare_external("ext0", ["ext1a", "func1f"])


def test_import_g():
    compare_external("ext0", ["ext1a", "func1g"])


def test_import_h():
    compare_external("ext0", ["ext1a", "func1h"])


def test_import_i():
    compare_external("ext0", ["ext1a", "func1i"])


def test_import_j():
    compare_external("ext0", ["ext1a", "func1j"])


def test_import_k():
    compare_external("ext0", ["ext1a", "func1k"])


def test_import_l():
    compare_external("ext0", ["ext1b", "func1l"])


def test_import_m():
    compare_external("ext0", ["ext1c", "func1m"])


def test_import_n():
    compare_external("ext0", ["ext1d", "func1n"])


def test_import_o():
    compare_external("ext0", ["ext1e", "func1o"])


def test_import_p():
    compare_external("ext0", ["ext1f", "func1p"])


def test_import_q():
    compare_external("ext0", ["ext1g", "func1q"])


def test_import_r():
    compare_external("ext0", ["ext2b", "func2c"])


def test_import_s():
    compare_external("ext0", ["ext2c", "func2d"])


def test_import_t():
    compare_external("ext0", ["ext2d", "func2e"])


def test_import_u():
    compare_external("ext0", ["ext2e", "func2f"])
