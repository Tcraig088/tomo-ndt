import numpy as np

from ..structs import VolumeNDt
from ..utils.context import device_context
from ..utils.output import progressbar

from .base import NDtOperator
from tomondt.plugins.algorithms import forwardproject
from tomondt.structs import TiltSeriesNDt
import logging

class NDtProject(NDtOperator):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def run(self, vmf, angles, times=None):
        vmf.setcontext(self.context, self.device)
        data = np.zeros([vmf.shape[0], vmf.shape[1], len(angles)])
        additive = 0
        if vmf.times[0]==0:
            additive = 1

        aggregate_times = True
        if times is None:
            aggregate_times = False
            times = vmf.times[additive:None]
            
        if len(times) != len(angles):
            raise Exception("001: times and angles array must be the same size")
            
        if aggregate_times == False:
            i = 0
            for angle in angles:
                obj = vmf.read_record(vmf.times[i+additive])
                data[:,:,i] = forwardproject(obj, angle)
                i +=1
        elif aggregate_times == True:
            i = 0
            for time in times:
                img_list = []
                end_i = np.argmax(vmf.times_start>time)
                start_i = np.argmax(vmf.times_end<time)
                for j in range(start_i,end_i+1):
                    if vmf.times_start[j]<=time<=vmf.times_end[j]:
                        obj = vmf.read_record(vmf.times[j])
                        img_list.append(forwardproject(obj, angles[i]))
                img = data[:,:,i].squeeze()
                for j in range(len(img_list)):
                    img += img_list[j]
                img = img/len(img_list)
                data[:,:,i] = img
                i += 1
        ts = TiltSeriesNDt(data,angles,times).setcontext(self.context, self.device)
        if vmf.version[0]>=1:
            ts.pixelsize = vmf.voxelsize
            ts.timeunit = vmf.timeunit
            ts.spaceunit = vmf.spaceunit
        return ts