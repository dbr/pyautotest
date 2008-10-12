import unittest

class test_one(unittest.TestCase):
    def test_actualtestone(self):
        self.assertEquals(True, True)
    def test_actualtesttwo(self):
        self.assertEquals(True, False)

class test_two(unittest.TestCase):
    def test_panic(self):
        self.assertEquals(True, False)