import numpy as np
import random
import os
import pandas as pd
import inspect


from tomondt import utils
from tomondt.utils.context import device_context, DeviceContextEnum, DtypesEnum
from ..structs import VolumeNDt, TiltSeriesNDt
from ..io import new_vmf
from .base import NDtOperator

class NDtEvaluate(NDtOperator):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ref = kwargs.get('ref', None)
                    
    def __call__(self, **kwargs):
        super().__init__()


    def run(self, obj, algor, ref=None):
        #if ref is not none
        obj.setcontext(self.context, self.device)
        if ref is not None:
            self.ref = ref
            self.ref.setcontext(self.context, self.device)

        args = inspect.signature(algor).parameters
        if len(args) == 1:
            useref = False
        elif len(args) == 2:
            useref = True
        else:
            raise ValueError('Invalid number of arguments in evaluation algorithm')

        if useref and self.ref is None:
            raise ValueError('Reference must be set for evaluation algorithm')
        
        if isinstance(obj, VolumeNDt):
            if useref:
                return self._compare_vol(obj, algor)
            else:
                return algor(obj)
            

    def _compare_vol(self, obj, algor):
        df = pd.DataFrame(columns=['time', 'value'])
        for i, t in enumerate(obj.times):   
            condition = (self.ref.times>= obj.times_start[i]) & (self.ref.times<= obj.times_end[i])
            amalgam_volume = utils.zeros(self.ref.shape, self.context, self.device)
            times = self.ref.times[condition]
            for j, time in enumerate(times):
                amalgam_volume += self.ref.read_record(time)
            amalgam_volume /= j+1
            value = algor(obj.read_record(t), amalgam_volume)
            df.loc[i] = [time, value]
        return df





    def _get_iters(self, obj):
        """
            returns array of tuples with the start and end values for the iteration
            
        """
        iters = []
        nprojections = len(obj.angles)
        if self.frame is None:
            self.frame = nprojections
        i = 0
        while i+self.frame<nprojections:
            start = i
            end = i+self.frame  
            iters.append((start, end))
        return iters 