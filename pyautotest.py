#!/usr/bin/env python
#encoding:utf-8
#author:dbr/Ben
#project:pyautotest
#repository:http://github.com/dbr/pyautotest
#license:Creative Commons GNU GPL v2
# (http://creativecommons.org/licenses/GPL/2.0/)

"""Like ZenTest's autotest command, but for Python modules
"""
__version__ = (1, 0)

import os
import sys
import time
import types
import hashlib
import unittest
import subprocess

from StringIO import StringIO
from optparse import OptionParser

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

####################
# Helper functions #
####################

class FileModChecker:
    """Checks if a file has been modified.
    Can compare either a sha1 hash of the file (which checks for content
    modification) or timestamp modification (which will trigger whenever
    even if the files content has not changed).
    sha1 is recommended, but could be slow with many or very large files.
    """
    valid_methods = ["time", "sha1"]
    
    def __init__(self, filename, method="time"):
        if method not in self.valid_methods:
            raise TypeError("method must be one of: %s" % (
                    ", ".join(self.valid_methods)
            ))
        
        self.filename = filename
        self.method = method
        
        self.prev_stamp = None
    
    def __repr__(self):
        return "<FileModChecker for %s" % (self.filename)
    
    def _get_stamp(self):
        """Calculates a "stamp" of the file.
        "time" uses the files mtime.
        "sha1" uses the hashlib.sha1 module to hash the files content
        """
        return {
            'time':
                os.path.getmtime(self.filename),
            'sha1':
                hashlib.sha1(open(self.filename).read()).hexdigest()
        }[self.method]
    
    def modified(self):
        """Checks if the file has been modified since either the
        class is initalised, or modified was last called
        """
        new_stamp = self._get_stamp()
        if new_stamp > self.prev_stamp:
            self.prev_stamp = new_stamp
            return True
        else:
            return False


#################
# Main function #
#################

def find_files(base, extension = "py", include_hidden = False):
    """Recursivly finds files in a directory
    """
    out = []
    if os.path.isdir(base):
        for cur_file in os.listdir(base):
            if not include_hidden:
                if os.path.split(cur_file)[1].startswith("."):
                    continue
        
            if extension is not None:
                if not os.path.splitext(cur_file)[1] == "." + extension:
                    continue
        
            cur_file = os.path.join(base, cur_file)
            if os.path.isdir(cur_file):
                out.extend(find_files(cur_file, extension, include_hidden))
            else:
                out.append(cur_file)
    elif os.path.isfile(base):
        out.append(base)
    
    return out

def main():
    """Takes a bunch of files, runs the tests when files are modified
    """
    prs = OptionParser()
    prs.add_option("-d", "--delay", dest="delay", type="int", default = 2,
                  help = "delay between running tests (integer)")
    prs.add_option("-m", "--method", dest="method", default="sha1",
               help = "method used to detect file modification. sha1 or time.")
    prs.add_option("-i", "--invisible", dest="invisible", action="store_true",
                help = "Include hidden (dot) files when looking for test-cases")
    opts, args = prs.parse_args()
    
    if len(args) == 0:
        prs.error("No files supplied!")

    print "## pyautotest starting.."
    
    all_files = []
    for cur_arg in args:
        all_files.extend(
            [FileModChecker(x) 
            for x in find_files(cur_arg, 
                                include_hidden = opts.invisible)
            ])
    
    print "# %s files found" % (len(all_files))
    
    last = { 'error':{}, 'failure':{} }
    while True:
        # Wait for a file to be modified
        for cur_file in all_files:
            if cur_file.modified():
                print "files modified"
                break # A file is modified, break out of for loop
        else:
            # No files were modified, wait then skip to start of while loop
            time.sleep(opts.delay)
            continue
        
        to_test = []
        for cur_file in all_files:
            try:
                to_test.extend( find_testcases(cur_file.filename) )
            except SyntaxError, e:
                print "SyntaxError while importing %s:\n%s" % (
                    cur_file.filename,
                    e
                )
        
        if len(to_test) == 0:
            # No tests found
            time.sleep(opts.delay)
            continue # Start while loop again
        
        try:
            print "# Running tests..."
            cur = run_tests(to_test)
            print "# ..done"
        except KeyboardInterrupt:
            print "Tests aborted!"
        diff_results(last, cur)
        
        last = cur
        time.sleep(opts.delay)

if __name__ == '__main__':
    main()
