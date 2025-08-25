import logging

from tomondt.utils import utils
from tomondt.utils.context import DeviceContextEnum, device_context

import numpy
if device_context.availability.torch:
    import torch
    import torch.nn.functional as F
    import torchvision.transforms.functional as TF

if device_context.availability.cupy:
    import cupy as cp


class DataNDt:
    def __init__(self):
        self.context = DeviceContextEnum.NUMPY
        self.device = 0
    
    def _setcontext(self, context, device):
        if not utils._checkavailable(context, device):
            logging.warning('the context selected is not available - context not changed')
            return
        self.context = context
        self.device = device

    def setcontext(self, context, device=0):
        self._setcontext(context, device)
        for attr, value in self.__dict__.items():
            if attr not in ['context', 'device']:
                if utils._checkavailable(utils._checkcontext(value), self.device):
                    setattr(self, attr, self.ascontext(value))
                

    def setfromarray(self, array):
        self.context = utils._checkcontext(array)
        self.device = utils._checkdevice(array)
        return self
    
    def asnumpy(self, array):
        return utils.convertcontext(array, DeviceContextEnum.NUMPY, 0)

    def ascontext(self, array):
        return utils.convertcontext(array, self.context, self.device)
    
    def astype(self, dtype):
        for attr, value in self.__dict__.items():
            if attr not in ['context', 'device']:
                setattr(self, attr, utils._astype(value, self.context, dtype))
        return self
            
