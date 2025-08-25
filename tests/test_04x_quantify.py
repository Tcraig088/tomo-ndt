import unittest
import os
import shutil
import tomondt
import numpy as np
from datetime import datetime
import pandas as pd
import time
import pickle

from tomondt import Operator
from tomondt import metrics

import unittest
import os
import shutil
import tomondt
import numpy as np
from datetime import datetime
import pandas as pd
import time

import unittest
import os
import shutil
import tomondt
import numpy as np

import helpers

#Test Functions for v0 vmf file read write conditions 
class TestMethods_04x(unittest.TestCase):
    def setUp(self):
        self.upper_path, self.pandas_path, self.data_path = helpers.get_save_dir()
        self.files = helpers.get_datapath_objs(self.data_path)
        self.testnum = 'test_04'
        self.path = os.path.join(self.upper_path, self.testnum)

        self.times, self.angles = helpers.get_times_angles()
        self.ts = Operator('cupy',0).fp(tomondt.load_vmf(self.files[0]), self.angles)

    """ Volume Volume Comparison- numpy"""
    def test_040_volvol_numpy(self):
        helpers.refresh_subdir(self.path)
        name = self.testnum+str(0)
        timer = helpers.EvalTimer(self.pandas_path)
        ref = tomondt.load_vmf(self.files[0])
        vol = tomondt.load_vmf(self.files[1])
        ssiml = lambda x,y: metrics.ssim(x, y)
        
        qr_path = os.path.join(self.path, 'test_qr.h5df')
        qr = tomondt.QualityReport(qr_path)
        qr.add_test('SSIM', tomondt.TestType.VolVol, ssiml)
        qr.add_testdata('TestSample', ref,S001=vol )

        timer.start()
        qr2 = Operator().evaluate(qr,0)
        timer.end(name, 'Verbosity 0',1.0)

        timer.start()
        qr2 = Operator().evaluate(qr,1)
        timer.end(name, 'Verbosity 1',1.0)

        timer.start()
        qr2 = Operator().evaluate(qr, 2)
        timer.end(name, 'Verbosity 2',1.0)
        qr2.write_report()

    """ Volume Volume Comparison, verbosity 0 - cupy"""
    def test_041_volvol_cupy(self):
        name = self.testnum+str(1)
        name = self.testnum+str(1)
        timer = helpers.EvalTimer(self.pandas_path)
        ref = tomondt.load_vmf(self.files[0])
        vol = tomondt.load_vmf(self.files[1])
        ssiml = lambda x,y: metrics.ssim(x, y)
        
        qr_path = os.path.join(self.path, 'test_qr.h5df')
        qr = tomondt.QualityReport(qr_path)
        qr.add_test('SSIM', tomondt.TestType.VolVol, ssiml)
        qr.add_testdata('TestSample', ref,S001=vol )

        timer.start()
        qr2 = Operator('cupy', 0).evaluate(qr,0)
        timer.end(name, 'Verbosity 0',1.0)

        timer.start()
        qr2 = Operator('cupy',0).evaluate(qr,1)
        timer.end(name, 'Verbosity 1',1.0)

        timer.start()
        qr2 = Operator('cupy',0).evaluate(qr, 2)
        timer.end(name, 'Verbosity 2',1.0)
        qr2.write_report()
        helpers.copy_file(qr.dir, "test_qr.h5df")

 