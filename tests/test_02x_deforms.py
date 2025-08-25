import unittest
import os
import shutil
import tomondt
import numpy as np

import helpers

#Test Functions for v0 vmf file read write conditions 
class TestMethods_02x(unittest.TestCase):
    def setUp(self):
        self.upper_path, self.pandas_path, self.data_path = helpers.get_save_dir()
        self.files = helpers.get_datapath_objs(self.data_path)

        self.testnum = 'test_02'
        self.path = os.path.join(self.upper_path, self.testnum)
        
        self.nanocage = tomondt.load_phantom('nanocage')
        self.times, self.angles = helpers.get_times_angles()
        self.beamdamage = lambda x: tomobase.processes.beamdamage(x, 0.5, 0.05)
        

    """ Beam Damage Operation - Numpy"""
    def test_020_numpy(self):
        helpers.refresh_subdir(self.path)
        name = self.testnum+str(0)
        timer = helpers.EvalTimer(self.pandas_path)

        timer.start()
        vmf_path = os.path.join(self.path, name + "numpy.vmf")
        vmf = tomondt.load_vmf(vmf_path, self.nanocage.astype(float))
        vmf = tomondt.Operator().deform(vmf, self.times,self.beamdamage)
        timer.end(name, 'full')
        timer.end(name, 'single' ,len(self.times))
        helpers.update_data_path(self.data_path, vmf_path, "test_beamdamage_simulation.vmf")

    """ Beam Damage Operation - Cupy"""
    def test_021_cupy(self):
        name = self.testnum+str(1)
        timer = helpers.EvalTimer(self.pandas_path)

        timer.start()
        vmf_path = os.path.join(self.path, name + "cupy.vmf")
        vmf = tomondt.load_vmf(vmf_path, self.nanocage.astype(float))
        vmf = tomondt.Operator('cupy', 0).deform(vmf, self.times,self.beamdamage)
        timer.end(name, 'full')
        timer.end(name, 'single' ,len(self.times))
