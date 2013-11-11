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

import os, sys, logging
from argparse import ArgumentParser
from pony.orm import *
from collections import defaultdict
from summer import internal as checksum
from functools import wraps
from utils import Utils
from journal import Journal

def exportclass(_cls):
    setattr(sys.modules['__main__'], _cls.__name__, _cls)
    return _cls

class Counters:
    counts = defaultdict(int)

class Handlers:
    actions = defaultdict()
    @classmethod
    def register(cls, _func):
        cls.actions[_func.__name__] = _func
        return _func

    @classmethod
    def dispatch(cls, _action, *args, **kw):
        return cls.actions[_action](*args, **kw)


def register_new(_func):
    print '########## register ##########'
    wraps(_func)
    def call(cls, *args, **kw):
        print self, args, kw
        self.actions[_func.__name__] = _func
    return call

class Commands:
    @staticmethod
    @Handlers.register
    @db_session
    def scan(_opts, _args):
        for d, b, p in Utils.iterate_dirs(_args, _dirs=False, _files=True):
            s = checksum(p)
            logging.debug("cksum=%s fname=%s dpath=%s" % (s, b, d))
            row = Sums.get(fname=b, dpath=d)
            if not row:
                Sums(cksum=s, fname=b, dpath=d)
            else:
                row.cksum = s
        commit()

    @staticmethod
    @Handlers.register
    @db_session
    def trim(_opts, _args):
        for p in _args:
            count = Sums.select(lambda w: w.dpath==p).count()
            print count
            t = 1
            for i in xrange(0, count, 1000):
                for x in Sums.select(lambda w: w.dpath==p)[i:i+1000]:
                    print t, x
                    fpath = os.path.join(x.dpath, x.fname)
                    if not os.path.isfile(fpath):
                        x.delete()
                    t += 1

        pass

    @staticmethod
    @Handlers.register
    @db_session
    def dump(_opts, _args):
        count = Sums.select().count()
##        print count
        t = 1
        for i in xrange(0, count, 1000):
            for x in Sums.select()[i:i+1000]:
                print t, x
                t += 1


    @staticmethod
    @Handlers.register
    @db_session
    def find(_opts, _args):
        for d, b, q in Utils.iterate_dirs(_args, _dirs=False, _files=True):
##        for p in _args:
##            for t, d, f in os.walk(p):
##                Utils.prune(d)
##                for y in f:
##                    q = os.path.join(t, y)
                    # skip files that are too large, or empty
                    if _opts.maxsize and os.path.getsize(q) > _opts.maxsize \
                        or os.path.getsize(q) == 0 :
                        logging.warn("Skipping %s %d" % (q, os.path.getsize(q)))
                        continue

                    # calculate checksum
                    s = checksum(q)

                    # remove entries for which the corresponding file is missing
                    existing_entries = []
                    for p in Sums.find(s): # p is pathname (dirpath + filename)
                        if p==q: continue
                        if not os.path.isfile(p):
                            Sums.remove(p)
                        else:
                            existing_entries.append(p)

                    # if we actually found something existing
                    if existing_entries:
                        logging.debug("duplicate files:")
                        logging.debug("\t%s" % (q))
                        for x in existing_entries:
                            logging.debug("\t%s" % (x))

                        Counters.counts["bytes_saved"] += os.path.getsize(q)

                        Journal.emit(Journal.Move(q, Utils.trashpath(q)))

                        # remove the file (must be explicitly asked for)
                        if _opts.delete:
                            Utils.trash(q)

                        Sums.remove(q)

        logging.info("%d bytes saved" % Counters.counts["bytes_saved"])

    @staticmethod
    @Handlers.register
    @db_session
    def mvtrash(_opts, _args):
        for d, b, p in Utils.iterate_dirs(_args, _dirs=True, _files=False):
            if b == Utils.trashdir:
                m,n = os.path.splitdrive(os.path.abspath(p))
                l = os.path.abspath(d).split(os.sep)[1:]
                q = os.path.join(m, os.sep, Utils.trashdir, *l)
                logging.info("mvtrash %s -> %s" % (p, q))
                os.renames(p, q)

def init(_db):
    @exportclass
    class Sums(_db.Entity):
        cksum = Required(str)
        fname = Required(unicode)
        dpath = Required(unicode)
        composite_key(cksum, fname, dpath)

        def __str__(self):
            return str((self.id, self.cksum, self.dpath, self.fname))

        @classmethod
        def find(cls, _checksum):
            """@return: list of paths to files with a matching checksum"""
            clause = lambda w: w.cksum==_checksum
            for r in cls.select(clause):
                yield os.path.join(r.dpath, r.fname)


        @classmethod
        def remove(cls, _fullpath):
            d, f = os.path.dirname(_fullpath), os.path.basename(_fullpath)
            clause = lambda w: w.dpath==d and w.fname==f
            for r in cls.select(clause):
                logging.debug("Sums::remove %s" % (r))
                r.delete()
                flush()

    _db.generate_mapping(create_tables=_db.create_tables)


def main():
    parser = ArgumentParser()
    parser.add_argument("--dbfile", default="sums.db")
    parser.add_argument("--action", default="scan")
    parser.add_argument("--trashcan", default="trash.zip")
    parser.add_argument("--delete", action="store_true")
    parser.add_argument("--loglevel", type=int, default=10)
    parser.add_argument("--maxsize", type=int, default=(10*1024**2))
    opts,args = parser.parse_known_args()

    args = map(lambda x: unicode(x, "utf8"), args)

    if opts.delete:
        raise Exception("delete is true")

    Utils.delete = opts.delete

    if opts.loglevel:
        logging.getLogger().setLevel(opts.loglevel)

    db = Database('sqlite', os.path.abspath(opts.dbfile), create_db=True)
    init(db)
    Handlers.dispatch(opts.action, opts, args)

    pass

if __name__ == '__main__':
    main()
