 pyAutotest
===================================
 Quick notifications of unitest failures
--------------------------------------

Author: dbr
Homepage: [GitHub][gh]

Description: Quick notifications of unittest failures

Introduction
============

Inspired by ZenTest's autotest tool (and by inspired I mean "completely stolen").

Why? Growl notifications as you fix tests, or as they fail.

It's very simple.. `pyautotest` locates all the unittests in a file/directory that you specify, then whenever a file is modified, the tests are run.
If something fails for the first time, the `failure` callback (a simple Python function) is executed, same when a test passes again.

Installing
===========

You can see (or easily contribute to) the code on [GitHub][gh]

You can checkout the latest development version from GitHub with the following command:

    git clone git://github.com/dbr/pyautotest.git

The easiest way to install pyautotest is to grab it from the [Cheeseshop][cs]. This means that if you have setuptools you can simply run:

    easy_install pyautotest

..and the `pyautotest` command will be available!


Getting Started
===============

Simply `pyautotest` in your python projects directory.

If you're on OS X, and have the growlnotify command (it's in the [Growl][gwl] Extras on the DMG)

If you're not on OS X, or don't have Growl/growlnotify installed, it'll probably break.. So you must change the functions `cb_break` and `cb_fixed`...

Custom callbacks
================

Each function takes two arguments, `status_name` and `change`:

- `status_name` is either "failure", "error" (in `cb_fixed` this indicates the kind of problem that was fixed)
- `change` is a dict containing two keys, `traceback` (a string version of the traceback) and `name` (the name of the problem test)

The simplest possible callback would contain a couple of print statements:

    def cb_break(status_name, change):
        print "Test %s" % (status_name)
        print "%s\n\n%s" % (
            change['name'],
            change['traceback']
        )
        print "-" * 78

    def cb_fixed(status_name, change):
        print "Fixed %s" % (status_name)
        print "%s" % (
            change['name']
        )
        print "-" * 78


Future
======

Things I want to try, or improve:

- The callback system, perhaps the abilty to have a ~/.pyautotest file containing your callbacks
- More built-in callbacks
- Try to use the code from `revtrace.py` to intelligently determine which unittests need to be run when a file is modified (instead of testing all)

[gh]: http://github.com/dbr/pyautotest/
[cs]: http://pypi.python.org/pypi/pyautotest/
[gwl]: http://growl.info