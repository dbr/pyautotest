import unittest

class test_one(unittest.TestCase):
    def test_actualtestone(self):
        self.assertEquals(True, True)
        self.assertEquals(True, 0)

class test_one(unittest.TestCase):
    def test_panic(self):
        self.assertEquals(True, False)