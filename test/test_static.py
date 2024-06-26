import os
from subprocess import run
from sys import executable
from unittest import main, TestCase

from robot_war.constants import CONSTANTS


class TestStatic(TestCase):
    def test_mypy(self):
        """Check source for syntax errors"""
        os.environ["MYPYPATH"] = str(CONSTANTS.PATHS.ROOT / "stubs")
        os.chdir(CONSTANTS.PATHS.SOURCE)
        results = run([str(CONSTANTS.PATHS.SCRIPTS / "mypy"), "."], capture_output=True, text=True)
        errors = ""
        num_errors = 0
        for line in results.stdout.split("\n"):
            if ": error: " in line:
                errors += f"{line}\n"
                num_errors += 1
            elif ": note: " in line:
                errors += f"{line}\n"
        if num_errors:
            errors += f"mypy found {num_errors} errors"
            assert errors == ""

    def test_freewvs(self):
        """Check packages for vulnerabilities"""
        results = run([executable, str(CONSTANTS.PATHS.SCRIPTS / "update-freewvsdb")])
        assert results.returncode == 0
        os.chdir(CONSTANTS.PATHS.SOURCE)
        results = run([executable, str(CONSTANTS.PATHS.SCRIPTS / "freewvs"), "."], capture_output=True, text=True)
        if results.returncode:
            assert results.stdout == ""


if __name__ == "__main__":
    main()
