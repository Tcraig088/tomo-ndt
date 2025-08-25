import unittest
import os
import shutil
import tomondt
import numpy as np
from datetime import datetime
import pandas as pd
import time

from tomondt import Operator

import unittest
import os
import shutil
import tomondt
import numpy as np

import helpers

#Test Functions for v0 vmf file read write conditions 
class TestMethods_03x(unittest.TestCase):
    def setUp(self):
        self.upper_path, self.pandas_path, self.data_path = helpers.get_save_dir()
        self.files = helpers.get_datapath_objs(self.data_path)
        self.testnum = 'test_03'
        self.path = os.path.join(self.upper_path, self.testnum)
        
        self.times, self.angles = helpers.get_times_angles()
        self.framesize = 15

    """ Forward Projection - Numpy"""
    def test_030_numpy(self):
        helpers.refresh_subdir(self.path)
        name = self.testnum+str(0)
        timer = helpers.EvalTimer(self.pandas_path)
        ref = tomondt.load_vmf(self.files[0])

        timer.start()
        ts = Operator().fp(ref, self.angles)
        timer.end(name, 'full' ,1.0)
        timer.end(name, 'single' ,len(self.angles))

    """ Forward Projection - Cupy"""
    def test_031_cupy(self):
        name = self.testnum+str(1)
        timer = helpers.EvalTimer(self.pandas_path)
        ref = tomondt.load_vmf(self.files[0])

        timer.start()
        ts = Operator('cupy',0).fp(ref, self.angles)
        timer.end(name, 'full' ,1.0)
        timer.end(name, 'single' ,len(self.angles))

    """ Forward Projection - Torch"""
    def test_032_torch(self):
        name = self.testnum+str(2)
        timer = helpers.EvalTimer(self.pandas_path)
        ref = tomondt.load_vmf(self.files[0])

        timer.start()
        ts = Operator('torch',0).fp(ref, self.angles)
        timer.end(name, 'full' ,1.0)
        timer.end(name, 'single' ,len(self.angles))

    """ Back Projection - Numpy"""
    def test_033_numpy(self):
        name = self.testnum+str(3)
        timer = helpers.EvalTimer(self.pandas_path)
        ref = tomondt.load_vmf(self.files[0])
        ts = Operator().fp(ref, self.angles)

        timer.start()
        vmf = Operator().bp(os.path.join(self.path,'rec_033_numpy.vmf'), ts, lambda x: tomondt.algorithms.sirt(x), self.framesize)
        timer.end(name, 'full' ,1.0)
        timer.end(name, 'single' ,len(vmf.times))

    def test_034_cupy(self):
        name = self.testnum+str(4)
        timer = helpers.EvalTimer(self.pandas_path)
        ref = tomondt.load_vmf(self.files[0])
        ts = Operator().fp(ref, self.angles)

        timer.start()
        vmf = Operator('cupy',0).bp(os.path.join(self.path,'rec_034_cupy.vmf'), ts, lambda x: tomondt.algorithms.sirt(x), self.framesize)
        timer.end(name, 'full' ,1.0)
        timer.end(name, 'single' ,len(vmf.times))

    def test_035_torch(self):
        name = self.testnum+str(5)
        timer = helpers.EvalTimer(self.pandas_path)
        ref = tomondt.load_vmf(self.files[0])
        ts = Operator().fp(ref, self.angles)

        timer.start()
        vmf = Operator('torch',0).bp(os.path.join(self.path,'rec_035_torch.vmf'), ts, lambda x: tomondt.algorithms.sirt(x), self.framesize)
        timer.end(name, 'full' ,1.0)
        timer.end(name, 'single' ,len(vmf.times))
        helpers.update_data_path(self.data_path, os.path.join(self.path,'rec_035_torch.vmf'), "test_bp.vmf")
