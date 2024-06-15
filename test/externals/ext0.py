from sub1 import ext1a, ext1b, ext1c, ext1d, ext1e, ext1f, ext1g
from sub1.sub2 import ext2b, ext2c, ext2d, ext2e

MODULES = {"ext1a": ext1a, "ext1b": ext1b, "ext1c": ext1c, "ext1d": ext1d, "ext1e": ext1e, "ext1f": ext1f,
           "ext1g": ext1g, "ext2b": ext2b, "ext2c": ext2c, "ext2d": ext2d, "ext2e": ext2e}

if __name__ == "__main__":
    import sys

    print(getattr(MODULES[sys.argv[1]], sys.argv[2])())
