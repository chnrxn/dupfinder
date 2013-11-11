#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      kokcheng
#
# Created:     10/11/2013
# Copyright:   (c) kokcheng 2013
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import pbs as sh
from sys import argv
import hashlib
import time
from functools import wraps

def timed(_func):
    wraps(_func)
    def bar(*args, **kw):
        s = time.time()
        ret = _func(*args, **kw)
        e = time.time()
        print (e-s) * 1000.0, "ms"
        return ret
    return bar

def extern(_fpath):
    ck = sh.Command("md5sum")
##    print ls ('.')
    return ck(_fpath).split()[0].strip()


def internal(_fpath):
    h = hashlib.md5()
    f = file(_fpath, "rb")
    for block in iter(lambda: f.read(1024**2), ""):
        h.update(block)
    return h.hexdigest()


def main():
    ls = sh.Command("ls")
    ck = sh.Command("md5sum")

    sum_int = timed(internal)
    sum_ext = timed(extern)

##    print ls ('.')
    print "internal:", sum_int(argv[1])
    print "external:", sum_ext(argv[1])
    pass

if __name__ == '__main__':
    main()
