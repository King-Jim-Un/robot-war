import os
from subprocess import run, check_call
from sys import executable
from unittest import main, TestCase

from robot_war.constants import CONSTANTS


class TestStatic(TestCase):
    def test_mypy(self):
        """Check source for syntax errors"""
        os.environ["MYPYPATH"] = str(CONSTANTS.PATHS.ROOT / "stubs")
        os.chdir(CONSTANTS.PATHS.SOURCE)
        results = run([str(CONSTANTS.PATHS.SCRIPTS / "mypy"), "."], capture_output=True, text=True)
        print()
        num_errors = 0
        for line in results.stdout.split("\n"):
            print(line)
            if ": error: " in line:
                num_errors += 1
        assert num_errors == 0, f"mypy found {num_errors} errors"

    def test_freewvs(self):
        """Check packages for vulnerabilities"""
        os.chdir(CONSTANTS.PATHS.SOURCE)
        check_call([executable, str(CONSTANTS.PATHS.SCRIPTS / "update-freewvsdb")])
        check_call([executable, str(CONSTANTS.PATHS.SCRIPTS / "freewvs"), "."])


if __name__ == "__main__":
    main()
