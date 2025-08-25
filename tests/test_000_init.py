import unittest
import os
import shutil
import tomondt
import numpy as np

from tests import helpers

#Test Functions for v0 vmf file read write conditions 
class TestMethods_010x(unittest.TestCase):
    def setUp(self):
        helpers.define_save_dir()
        self.path, self.pandas_path, self.data_path = helpers.get_save_dir()

    """ Read/Write to New VMF File"""
    def test_0000_setup(self):
        pass
