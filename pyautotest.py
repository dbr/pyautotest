import unittest
from optparse import OptionParser
import time
from StringIO import StringIO

from rawr import rawr
from findtests import find_testcases

def run_tests(modules):
    for m in modules:
        suite = unittest.TestLoader().loadTestsFromTestCase(m[1])
    report = StringIO()

    runner = unittest.TextTestRunner(report)
    results = runner.run(suite)

    status = {
        'error':{},
        'failure':{},
        'pass':{}
    }

    #print "Failures:", results.failures
    for tcinstance, tb in results.failures:
        status['failure'][str(tcinstance.id())] = {
            'name':tcinstance,
            'traceback': tb
        }

    #print "Errors:", results.errors
    for tcinstance, tb in results.errors:
        status['error'][str(tcinstance.id())] = {
            'name':tcinstance.id(),
            'traceback': tb
        }

    #print "Tests run:", results.testsRun
    #print "Success?", results.wasSuccessful()
    return status


def reg_growl():
    x = rawr(
        "pyautotest", "localhost", "yay",
        ntypes = ["error", "failure", "pass"]
    )
    x.regApp()
    return x

def cb_break(status_name, change):
    x = reg_growl()
    title = "Test %s" % (status_name)
    body = "%s\n\n%s" % (
        change['name'],
        change['traceback']
    )
    x.sendnotif(title, body, ntype = status_name)

def cb_fixed(status_name, change):
    x = reg_growl()
    title = "Fixed %s" % (status_name)
    body = "%s" % (
        change['name']
    )
    x.sendnotif(title, body, ntype = status_name)


def diff_results(last, cur):
    for status_name, contents in cur.items():
        for k, v in contents.items():
            if not last[status_name].has_key(k):
                cb_break(status_name, cur[status_name][k])
    
    for status_name, contents in last.items():
        for k, v in contents.items():
            if not cur[status_name].has_key(k):
                cb_fixed(status_name, last[status_name][k])

def main():
    p = OptionParser()
    opts, args = p.parse_args()
    
    if len(args) == 0:
        p.error("No files supplied!")

    last = None
    while True:
        to_test = []
        for ca in args:
            to_test.extend(find_testcases(ca))

        if len(to_test) == 0:
            print "Nothing found!"
            time.sleep(10)
        else:
            cur = run_tests(to_test)
            if last == None:
                last = cur

            diff_results(last, cur)

            last = cur
            time.sleep(1)

if __name__ == '__main__':
    main()
