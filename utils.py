#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      kokcheng
#
# Created:     11/11/2013
# Copyright:   (c) kokcheng 2013
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import os
import logging

class Utils:
    trashdir = '.trash'
    delete = False

    @classmethod
    def trashpath(cls, _fpath):
        d = os.path.dirname(_fpath)
        m,n = os.path.splitdrive(os.path.abspath(_fpath))
        l = os.path.abspath(_fpath).split(os.sep)[1:]
        q = os.path.join(m, os.sep, cls.trashdir, *l)
        return q

    @classmethod
    def iterate_dirs(cls, _dirlist, _dirs=True, _files=True):
        """@return: parent_directory, basename, full_path"""
        for p in _dirlist:
            if type(p)==str:
                p = unicode(p, "utf-8")
            for t, d, f in os.walk(p):
                if _dirs:
                    for x in d:
                        yield t, x, os.path.join(t, x)
                if _files:
                    for x in f:
                        yield t, x, os.path.join(t, x)

    @classmethod
    def prune(cls, _dirlist):
        if cls.trashdir in _dirlist:
            _dirlist.remove(cls.trashdir)

    @classmethod
    def trash_old(cls, _fpath):
        d = os.path.dirname(_fpath)
        t = os.path.join(d, cls.trashdir)
        p = os.path.join(t, os.path.basename(_fpath))
        if not os.path.isdir(t):
            os.makedirs(t)
        logging.info( "rename %s -> %s" % (_fpath, p) )
        os.rename(_fpath, p)

    @classmethod
    def trash(cls, _fpath):
        if not cls.delete: return False
        tpath = cls.trashpath(_fpath)
        logging.debug("Utils.trash %s -> %s" % (_fpath, tpath))
        return os.renames(_fpath, tpath)

def main():
    print Utils.trashpath(r'e:\pictures\PANA\IMG1234.jpg')
    pass

if __name__ == '__main__':
    main()
