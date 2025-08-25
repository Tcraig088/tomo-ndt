import numpy as np
from tomondt.utils.context import device_context
from tomondt.structs.base import DataNDt
""" TiltSeriesnDt class:
Class for storing projection data and associated metadata.

Attributes:
    data (numpy.ndarray): projection images
    angles (numpy.ndarray): projection angles convention is +/-180 tomographic convention in degrees
    times (numpy.ndarray): time of collection
    pixelsize (float): pixel size
    frametime (float): time taken to collect a single projection if specified
    timeunit (str): time unit - units dont really matter in the class but are here just so they aren't lost
    spaceunit (str): space unit

Methods:  None

Raises: Exception: None

Returns: None
"""
class TiltSeriesNDt(DataNDt):
    def __init__(self, data, angles, times=None):
        super().__init__()
        self.data: np.array = data
        self.angles: np.array = angles
        self.times: np.array = times
        self.pixelsize: float = 1.0
        self.frametime: float = 0.0
        self.timeunit = 's'
        self.spaceunit = 'nm'

        if times is None:
            self.times = np.linspace(1, len(angles), len(angles))

        self.setcontext(self.context, self.device)

    def setcontext(self, context, device):
        super().setcontext(context, device)
        return self

    def astype(self, dtype):
        super().astype(dtype)
        return self

