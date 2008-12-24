#!/usr/bin/env python
#encoding:utf-8
#author:dbr/Ben
#project:pyautotest
#repository:http://github.com/dbr/pyautotest
#license:Creative Commons GNU GPL v2
# (http://creativecommons.org/licenses/GPL/2.0/)

"""Like ZenTest's autotest command, but for Python modules
"""

import os
import sys
import time
import types
import hashlib
import unittest
import subprocess

from optparse import OptionParser
from StringIO import StringIO

###############################
# Test-case finding functions #
###############################

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
        path, cfile = os.path.split(module)
        module = os.path.splitext(cfile)[0]
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

####################
# Test-case runner #
####################

def run_tests(modules):
    """Takes a bunch of modules, runs them though unittest.TextTestRunner.
    Returns a dict-of-dicts, containing error and failure
    """
    suite = unittest.TestSuite()
    for cur_modules in modules:
        suite.addTests(
            unittest.TestLoader().loadTestsFromTestCase(cur_modules[1])
        )
    
    report = StringIO()
    runner = unittest.TextTestRunner(report)
    results = runner.run(suite)
    
    status = {
        'error':{},
        'failure':{},
    }
    
    for tcinstance, traceb in results.failures:
        status['failure'][str(tcinstance.id())] = {
            'name':tcinstance,
            'traceback': traceb
        }
    
    for tcinstance, traceb in results.errors:
        status['error'][str(tcinstance.id())] = {
            'name':tcinstance.id(),
            'traceback': traceb
        }
    
    return status


def diff_results(last, cur):
    """Diffs two run_tests results, calling the appropriate callbacks.
    """
    for status_name in cur.keys():
        set_last = set(last[status_name])
        set_cur = set(cur[status_name])
        
        broken = set_cur - set_last
        fixed = set_last - set_cur
        
        for change in broken:
            cb_break(status_name, cur[status_name][change])
        for change in fixed:
            cb_fixed(status_name, last[status_name][change])


#############
# Callbacks #
#############

def cb_break(status_name, change):
    """Called when a test starts failing
    """
    title = "Test %s" % (status_name)
    body = "%s\n\n%s" % (
        change['name'],
        change['traceback']
    )
    subprocess.Popen(
        ["growlnotify", title, 
        "--name", "pyautotest",
        "-i", "py",
        "-m", body]
    )
    print title
    print body
    print "-" * 78

def cb_fixed(status_name, change):
    """Called when a test is fixed
    """
    title = "Fixed %s" % (status_name)
    body = "%s" % (
        change['name']
    )
    subprocess.Popen(
        ["growlnotify", title, 
        "--name", "pyautotest",
        "-i", "py",
        "-m", body]
    )
    print title
    print body
    print "-" * 78

#################
# Main function #
#################

class ModificationChecker:
    valid_methods = ["time", "sha1"]
    
    def __init__(self, f, method="time"):
        if method not in self.valid_methods:
            raise TypeError("Modification detection method must be one of: %s" % (
                ", ".join(self.valid_methods)
            ))
        
        self.f = f
        self.method = method
        
        self.prev_stamp = self._get_stamp()
    
    def _get_stamp(self):
        return {
            'time':
                os.path.getmtime(self.f),
            'sha1':
                hashlib.sha1(open(self.f).read()).hexdigest()
        }[self.method]
    
    def modified(self):
        new_stamp = self._get_stamp()
        if new_stamp > self.prev_stamp:
            self.prev_stamp = new_stamp
            return True
        else:
            return False
        

def main():
    """Takes a bunch of files, runs the tests when files are modified
    """
    prs = OptionParser()
    prs.add_option("-d", "--delay", dest="delay", type="int", default = 2,
                 help = "delay between running tests")
    opts, args = prs.parse_args()
    
    if len(args) == 0:
        prs.error("No files supplied!")
    
    last = None
    while True:
        to_test = []
        for cur_arg in args:
            to_test.extend( find_testcases(cur_arg) )
        
        if len(to_test) == 0:
            print "No tests found! Waiting 10 seconds"
            time.sleep(10)
        else:
            cur = run_tests(to_test)
            
            if last == None:
                last = { 'error':{}, 'failure':{} }
            
            diff_results(last, cur)
            
            last = cur
            time.sleep(opts.delay)

if __name__ == '__main__':
    main()
