import numpy as np
import random
import os
import pandas as pd

from tomondt.utils.context import device_context
from ..structs import VolumeNDt, TiltSeriesNDt
from ..io import new_vmf
from .base import NDtOperator

class NDtReconstruct(NDtOperator):
    def __init__(self, **kwargs):
        super().__init__()
        random_number = random.randint(100000, 999999)
        fname = f"file_{random_number}.txt"
        self.file = kwargs.get('saveas', os.path.join(device_context.dir, fname))
        self.isdynamic = kwargs.get('isdynamic', False)
        if self.isdynamic == False:
            self.frame = kwargs.get('frame', None)
            self.offset = kwargs.get('offset', 1)
        else:
            self.evaluation_method = kwargs.get('evaluation_method', None)
            self.metric = kwargs.get('metric', None)
            if (self.evaluation_method is None):
                raise ValueError('Criterion must be set for dynamic reconstruction')
                    
    def __call__(self, **kwargs):
        super().__init__()
        random_number = random.randint(100000, 999999)
        fname = f"file_{random_number}.txt"
        self.file = kwargs.get('saveas', os.path.join(device_context.dir, fname))
        self.isdynamic = kwargs.get('isdynamic', False)
        if self.isdynamic == False:
            self.frame = kwargs.get('frame', None)
            self.offset = kwargs.get('offset', 1)
        else:
            self.evaluation_method = kwargs.get('evaluation_method', None)
            self.metric = kwargs.get('metric', None)
            if (self.evaluation_method is None):
                raise ValueError('Criterion must be set for dynamic reconstruction')


    def optimize(self, eval, ts, algor, verbosity=False):
        i=0 
        df = pd.DataFrame(columns=['framesize', 'metric'])
        filename = os.path.splitext(os.path.basename(self.file))[0]
        directory = os.path.dirname(self.file, filename)
        while i < len(ts.times):
            tempfile = os.path.join(directory, 'temp_calc'+str(i)+'.vmf')
            vol  = NDtReconstruct(saveas=tempfile, offset=self.offset, frame=i).run(ts, algor)
            qdata = eval.run(vol).mean()
            qdata['framesize'] = i
            if not self.verbose:
                os.remove(tempfile)
            new_row = pd.DataFrame(qdata)
            df = pd.concat([df, new_row])
            i+=self.offset
        self.df = df
        match self.metric:
            case 'min':
                self.frame = df[df['metric'] == df['metric'].min()]
            case 'max':
                self.frame = df[df['metric'] == df['metric'].max()]
            case 'mean':
                self.frame = df[df['metric'] == df['metric'].mean()]
            case None:
                pass
            case _:
                raise Exception('Invalid metric')
            
        if not self.verbose:
            os.rmdir(directory)
        return self

    def run(self, tiltseries, algor):
        tiltseries.setcontext(self.context, self.device)
        vol = new_vmf(self.file)
        if vol.version[0]>=1:
            vol.voxelsize = tiltseries.pixelsize
            vol.timeunit = tiltseries.timeunit
            vol.spaceunit = tiltseries.spaceunit
            
        iters  = self._get_iters(tiltseries)
    
        def mapper(i, vol, algor):
            sino = TiltSeriesNDt(tiltseries.data[:,:,i[0]:i[1]], tiltseries.angles[i[0]:i[1]], tiltseries.times[i[0]:i[1]])
            time_start, time_end, time_ave = np.min(sino.times)-sino.frametime, np.max(sino.times), np.mean(sino.times)+sino.frametime
            obj = algor(sino)
            vol.write_record(obj, time_ave, time_start, time_end)
            return vol
        
        vol = map(lambda i: mapper(i, vol, algor), iters)
        return vol
    
    def _get_iters(self, tiltseries):
        """
            returns array of tuples with the start and end values for the iteration
            
        """
        iters = []
        nprojections = len(tiltseries.angles)
        if self.frame is None:
            self.frame = nprojections
        i = 0
        while i+self.frame<nprojections:
            start = i
            end = i+self.frame  
            iters.append((start, end))
        return iters 