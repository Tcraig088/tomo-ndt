import numpy as np

from ..structs import VolumeNDt
from .base import NDtOperator
from tomobase.data import Volume
from tomondt.utils.context import device_context
from tomondt.io import new_vmf

class NDtDeform(NDtOperator):
    def __init__(self, **kwargs):
        super().__init__()
        self.saveas = kwargs.get('saveas',device_context.getfile('temp.vmf') )

    def run(self, vol, times, algor):
        dif = np.diff(np.append(np.array([0]),times))
        iters = np.round(dif/np.min(dif))

        vmf = new_vmf(self.saveas, vol)
        obj = Volume(vmf.read_record(0))
        dtype = obj.data.dtype
        j = 0
        for index in iters:
            for i in range(int(index)):
                obj = algor(obj)
            vmf.write_record(obj.data,times[j],times[j], times[j])
            j+=1
        return vmf