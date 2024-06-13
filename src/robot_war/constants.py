from pathlib import Path

CODE_CLASS = compile("0", "", "eval").__class__  # There's gotta be a better way!


class CONSTANTS:
    class TEST:
        class PATH:
            EXTERNALS = Path(__file__).parents[2] / "test" / "externals"
