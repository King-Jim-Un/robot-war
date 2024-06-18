from robot_war.exceptions import RobotWarSystemExit

BUILT_INS = {
    "getattr": lambda obj, name: getattr(obj, "get_attr")(name), "IndexError": IndexError, "int": int,
    "isinstance": isinstance, "IOError": IOError, "list": list, "print": print, "range": range, "str": str,
    "SystemExit": RobotWarSystemExit, "ZeroDivisionError": ZeroDivisionError
}
