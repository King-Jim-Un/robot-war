import logging

from robot_war.exceptions import RobotWarSystemExit


def is_class(user_cls, cls) -> bool:
    return (user_cls is cls) or any(is_class(parent, cls) for parent in user_cls.parent_classes)


def rw_isinstance(obj, cls) -> bool:
    from robot_war.vm.source_class import SourceInstance
    if isinstance(obj, SourceInstance):
        return is_class(obj.source_class, cls)
    else:
        return isinstance(obj, cls)


def rw_hasattr(obj, name: str) -> bool:
    if hasattr(obj, "get_attr"):
        try:
            obj.get_attr(name)
            return True
        except KeyError:
            return False
    else:
        return hasattr(obj, name)


def rw_getattr(obj, name: str):
    if hasattr(obj, "get_attr"):
        return getattr(obj, "get_attr")(name)
    else:
        return getattr(obj, name)


BUILT_INS = {
    "getattr": rw_getattr, "hasattr": rw_hasattr, "IndexError": IndexError, "int": int, "isinstance": rw_isinstance,
    "IOError": IOError, "list": list, "print": print, "range": range, "str": str, "SystemExit": RobotWarSystemExit,
    "ZeroDivisionError": ZeroDivisionError
}
