def func1a():
    import sub2.ext2

    return sub2.ext2.func2a()


def func1b():
    import sub2

    return sub2.func2()


def func1c():
    from sub2.ext2 import func2a

    return func2a()


def func1d():
    from sub2 import ext2

    return ext2.func2a()


def func1e():
    from sub2 import func2, ext2

    return func2() + ext2.func2a()


def func1f():
    from sub2.ext2 import func2a, func2b

    return func2a() + func2b()


def func1g():
    import sub1.sub2.ext2

    return sub1.sub2.ext2.func2a()


def func1h():
    import sub1.sub2

    return sub1.sub2.func2()


def func1i():
    from sub1.sub2.ext2 import func2a

    return func2a()


def func1j():
    from sub1.sub2 import ext2

    return ext2.func2a()


def func1k():
    from sub1.sub2 import func2, ext2

    return func2() + ext2.func2a()


def func1l():
    from sub1.sub2.ext2 import func2a, func2b

    return func2a() + func2b()


def func1m():
    from .sub2.ext2 import func2a

    return func2a()


def func1n():
    from .sub2 import ext2

    return ext2.func2a()


def func1o():
    from .sub2 import func2, ext2

    return func2() + ext2.func2a()


def func1p():
    from .sub2.ext2 import func2a, func2b

    return func2a() + func2b()


def func1q():
    from ..sub1.sub2.ext2 import func2a

    return func2a()


def func1r():
    from ..sub1.sub2 import ext2

    return ext2.func2a()


def func1s():
    from ..sub1.sub2 import func2, ext2

    return func2() + ext2.func2a()


def func1t():
    from ..sub1.sub2.ext2 import func2a, func2b

    return func2a() + func2b()


def func1u():
    import ext1j

    return ext1f.func1y()


def func1v():
    from ext1j import func1y

    return func1y()


def func1w():
    from .ext1j import func1y, func1z

    return func1y() + func1z()
