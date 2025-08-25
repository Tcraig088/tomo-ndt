import unittest
import os
import shutil
import tomondt
import numpy as np

import helpers

#Test Functions for v0 vmf file read write conditions 
class TestMethods_010x(unittest.TestCase):
    def setUp(self):
        self.upper_path, self.pandas_path, self.data_path = helpers.get_save_dir()
        self.files = helpers.get_datapath_objs(self.data_path)
        self.testnum = 'test_010'
        self.path = os.path.join(self.upper_path, self.testnum)

        self.nanocage = tomondt.load_phantom('nanocage')

    """ Read/Write to New VMF File"""
    def test_0100_readwrite_new(self):
        helpers.refresh_subdir(self.path)
        name = self.testnum+str(0)
        timer = helpers.EvalTimer(self.pandas_path)

        vmf_path = os.path.join(self.path, name + "_v0.vmf")
        vmf = tomondt.load_vmf(vmf_path, self.nanocage,(0,0,1)) 

        timer.start()
        vmf.write_record(self.nanocage, 1.0)
        timer.end(name, 'write' ,1.0)

        vmf.write_record(self.nanocage, 3.0, 1.5, 2.5)

        timer.start()
        vmf.read_record(3)
        timer.end(name, 'read' ,1.0)

        vmf.read_record(3)
        vmf.read_record(2,False)
        helpers.update_data_path(self.data_path, vmf_path, "test_load_vmf_v0.vmf")

    def test_0101_readwrite_loaded(self):
        name = self.testnum+str(1)
        vmf_path = os.path.join(self.files[0])
        vmf = tomondt.load_vmf(vmf_path)

        vmf.read_record(3)
        vmf.read_record(2,False)

        np.testing.assert_array_equal(vmf.times_start, np.array([0.0, 1.0 ,1.5]))
        np.testing.assert_array_equal(vmf.times_end, np.array([0.0, 1.0 ,2.5]))
        os.remove(vmf_path)

    """ same as test 0101 but without a zero time record on init"""
    def test_0102_readwrite_new(self):
        name = self.testnum+str(2)
        vmf_path = os.path.join(self.path, name + "_v0.vmf")
        vmf = tomondt.load_vmf(vmf_path,version=(0,0,1))

        vmf.write_record(self.nanocage, 1.0)
        vmf.write_record(self.nanocage, 3.0, 1.5, 2.5)

        vmf.read_record(3)
        vmf.read_record(1,False)
        
        np.testing.assert_array_equal(vmf.times_start, np.array([1.0 ,1.5]))
        np.testing.assert_array_equal(vmf.times_end, np.array([1.0 ,2.5]))
        os.remove(vmf_path)