def func1a():
    import sub1.sub2.ext2a

    return sub1.sub2.ext2a.func2a()


def func1b():
    import sub1.sub2

    return sub1.sub2.func2()


def func1c():
    from sub1.sub2.ext2a import func2a

    return func2a()


def func1d():
    from sub1.sub2 import ext2a

    return ext2a.func2a()


def func1e():
    from sub1.sub2 import func2, ext2a

    return func2() + ext2a.func2a()


def func1f():
    from sub1.sub2.ext2a import func2a, func2b

    return func2a() + func2b()


def func1g():
    from .sub2.ext2a import func2a

    return func2a()


def func1h():
    from .sub2 import ext2a

    return ext2a.func2a()


def func1i():
    from .sub2 import func2, ext2a

    return func2() + ext2a.func2a()


def func1j():
    from .sub2.ext2a import func2a, func2b

    return func2a() + func2b()


def func1k():
    from .ext1h import func1v, func1w

    return func1v() + func1w()
