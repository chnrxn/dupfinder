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

from collections import OrderedDict
import inspect
import logging
import json
import os

class Journal:

    logger = logging.getLogger("journal")

    @classmethod
    def emit(cls, _action):
        cls.logger.debug(str(_action))

    class UnimplementedAction(Warning): pass

    class Action:
        str_order = ['action', '_src', '_dst', '_msg']
        def __init__(self, _src, _dst=None, _msg=None):
            argspec = inspect.getargvalues(inspect.currentframe())
            self._locals = OrderedDict(action=self.__class__.__name__)
            for k in self.str_order:
                if k in argspec.locals:
                    self._locals[k] = argspec.locals[k]

        def __str__(self):
            return json.dumps(self._locals)

        def doit(self):
            raise UnimplementedAction(self._locals['action'])

    class Noop(Action):
        def doit(self):
            pass

    class Move(Action):
        def doit(self):
            return os.renames(self._locals['_src'].lower(), self._locals['_dst'])

    class Delete(Action):
        def doit(self):
            return os.remove(self._locals['_src'])

def main():
    print Journal.Move(r'c:\Pictures\PANA\IMG_8723.JPG', r'c:\.trash\Pictures\PANA\IMG_8723.JPG', "IMG_8723.JPG")
    print Journal.Delete(r'c:\Pictures\PANA\IMG_8723.JPG', None, "remove IMG_8723.JPG")
    pass

if __name__ == '__main__':
    main()
