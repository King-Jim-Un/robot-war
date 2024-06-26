from pathlib import Path
import sys

CODE_CLASS = compile("0", "", "eval").__class__  # There's gotta be a better way!


class CONSTANTS:
    class TIMING:
        FRAME_RATE = 30
        FRAMES = 1.0 / FRAME_RATE

    class PATHS:
        SCRIPTS = Path(sys.executable).parent
        ROOT = Path(__file__).parents[2]
        ROBOT_IMAGE = ROOT / "assets" / "robot1.png"
        FIREBALL_IMAGE = ROOT / "assets" / "fireball1.png"
        SOURCE = ROOT / "src" / "robot_war"

        class TEST:
            EXTERNALS = Path(__file__).parents[2] / "test" / "externals"
