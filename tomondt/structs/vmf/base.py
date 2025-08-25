import os
import struct
import numpy as np
from ..base import DataNDt
""" VolumenDt class:
Wrapper for working with vmf files the metadata is retained and the volumes are accessed from file as required.
The data format is dependent on the vmf file format. 
Hence slight differences may occur between versions however the wrapper should be backwards compatible for all existing versions.
This here is the parent class all VolumenDt versions inherit from. 

Attributes:
    dependent on versioning of vmf file format see read_vmf_metadata for details
    dir (str): directory of the vmf file
    version (tuple): version of the vmf file format
    shape (tuple): shape of the volumes in the vmf file
    pixelsize (float): pixelsize of the volumes in the vmf file
    times (np.array): times of the volumes in the vmf file
    times_start (np.array): start times of the volumes in the vmf file
    times_end (np.array): end times of the volumes in the vmf file
    empty (bool): True if no file exists at the specified location. If empty the latest version is assumed
    write_index (int): index of the next write operation
    

Methods:
    check vmf version for specific implementation
    Internal:
    _new_file: creates a new vmf file when an object is supplied and no file exists -external implementation can erase existing files!!!!

Raises: Exception: None

Returns: None

Version History:    
    1.0.0: Initial release
    0.0.1: Legacy release - not supported for new files. For backwards compatibility of files created before release of this package

"""
class VolumeNDt(DataNDt):
    def __init__(self, dir):
        super().__init__()
        self.dir: str = dir
        self.version = [0,0,0]
        self.shape = [0,0,0]
        self.voxelsize = 1.0
        
        self.times = np.array([],dtype=np.float32)
        self.times_start = np.array([], dtype=np.float32)
        self.times_end = np.array([], dtype=np.float32)

        self.write_index = 28
        self.empty = not os.path.isfile(self.dir)

    def setcontext(self, context, device):
        super().setcontext(context, device)

    """ _new_file
    Creates a new vmf file with base metadata
    Args:
        shape (tuple): shape of the volumes in the vmf file
    
    Returns: None

    Raises: Exception: None
    """
    def _new_file(self,shape):
        with open(self.dir,'wb') as file:
            file.write(struct.pack('3I', *self.version))
            file.write(struct.pack('3I', *shape))
            file.write(struct.pack('f', self.voxelsize))

        self.shape = shape
        self.empty = False

    """ _read_metadata
    Reads the metadata from the vmf file

    Args: None

    Returns: None

    Raises: Exception: None
    """
    def _read_metadata(self):
        with open (self.dir, 'rb') as file:
            self.version = tuple(struct.unpack('3I',file.read(12)))
            self.shape = tuple(struct.unpack('3I',file.read(12)))
            self.voxelsize = struct.unpack('f',file.read(4))[0]


