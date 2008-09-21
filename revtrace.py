"""
Demonstrates determining which functions a command depends on.

May use this to intellimigentalylly determine which tests to
run when code changes.
"""

def mystart():
    print subcall("Yay!")

def subcall(hmmm):
    return hmmm * 2

import trace
tracer = trace.Trace(countfuncs = 1)

tracer.runfunc(mystart)
res = tracer.results()
cf = res.calledfuncs

for k, v in cf.items():
    print k, v