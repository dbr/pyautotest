import unittest
import types
import os
import sys

def load(name):
    """Given a dotted name, return the last-named module instead of the first.
    http://docs.python.org/lib/built-in-funcs.html
    """
    module = __import__(name)
    reload(module)
    for _name in name.split('.')[1:]:
        module = getattr(module, _name)
    return module

def load_testcases(module):
    """Given a module, return a list of TestCases defined there.
    We only keep the TestCase if it has tests.
    """
    testcases = []
    for name in dir(module):
        obj = getattr(module, name)
        if isinstance(obj, (type, types.ClassType)):
            if issubclass(obj, unittest.TestCase):
                for _name in dir(obj):
                    if _name.startswith('test'):
                        name_dotted = module.__name__+'.'+obj.__name__
                        testcases.append((name_dotted, obj))
                        break
    return testcases

def find_testcases(module):
    """Store a list of TestCases below the currently named module.
    """
    
    # If the supplied arg is a (path to a) file,
    # get the directory name, append it to the path,
    # then load the filename.
    if os.path.isfile(module):
        path, file = os.path.split(module)
        module, ext = os.path.splitext(file)
        sys.path.append(path)
        
    basemod = load(module)
    testcases = load_testcases(basemod)
    path = os.path.dirname(basemod.__file__)
    for name in sorted(sys.modules):
        if name == basemod.__name__:
            continue
        if not name.startswith(module):
            continue
        module = sys.modules[name]
        if module is None:
            continue
        if not module.__file__.startswith(path):
            # Skip external modules that ended up in our namespace.
            continue
        testcases.extend(load_testcases(module))
    return testcases
