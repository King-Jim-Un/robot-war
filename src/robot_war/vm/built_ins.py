from robot_war.exceptions import RobotWarSystemExit

BUILT_INS = {
    "getattr": lambda obj, name: getattr(obj, "get_attr")(name), "IndexError": IndexError, "int": int,
    "isinstance": isinstance, "list": list, "print": print, "range": range, "repr": repr, "str": str,
    "SystemExit": RobotWarSystemExit
}
