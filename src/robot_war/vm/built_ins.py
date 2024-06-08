from robot_war.exceptions import RobotWarSystemExit

BUILT_INS = {
    "IndexError": IndexError, "int": int, "isinstance": isinstance, "list": list, "print": print, "str": str,
    "SystemExit": RobotWarSystemExit
}
