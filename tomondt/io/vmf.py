import struct
import os 
import pandas as pd

from ..structs import VolumeNDt_0v, VolumeNDt_1v

"""vmf_read
returns a volumendt object from a vmf file supports version control

Args:   
    path (str): path to vmf file
    obj (np.ndarray): optional volume to initialize 0 time point vmf file 
    version (tuple): optional version number to force read as a specific version
Returns:
    volumendt object

"""
def read_vmf(path, version = (1,0,0)):
    if os.path.isfile(path):
        with open(path,'rb') as file:
            version = struct.unpack('3I',file.read(12))
    else:
        raise Exception('File does not Exist: '+ path)
    match(version[0]):
        case 0:
            return VolumeNDt_0v(path)
        case 1:
            return VolumeNDt_1v(path)
        case _:
            raise Exception('Unsupported version or corrupted file format')  

        
def new_vmf(path, obj=None, version = (1,0,0)):
    if os.path.isfile(path):
        raise Exception('File already exists: '+ path)
    if obj is None:
        match(version[0]):
            case 0:
                obj = VolumeNDt_0v(path)
            case 1:
                obj = VolumeNDt_1v(path)
            case _:
                raise Exception('Unsupported version or corrupted file format')
    else:
        match(version[0]):
            case 0:
                obj = VolumeNDt_0v(path,obj)
            case 1:
                obj = VolumeNDt_1v(path,obj)
            case _:
                raise Exception('Unsupported version or corrupted file format')
    return obj

import os
import struct
import numpy as np
import pickle 
import bz2

from tomobase.data import Volume

class VMF():
    """ VMF class:
    Wrapper for working with vmf files the metadata is retained and the volumes are accessed from file as required. The data format is used to allow BZ2 data compression for volume time series that can be very large.

    Attributes:
        dependent on versioning of vmf file format see read_vmf_metadata for details
        dir (str): directory of the vmf file
        version (tuple): version of the vmf file format

    """
    def __init__(self, dir):
        super().__init__()
        self.dir: str = dir
        self.version = [0,0,3]
        self.metadata = pd.DataFrame(columns=['times','times_start','times_end','dsize','position'])

        self.write_index = 28
        self.empty = not os.path.isfile(self.dir)

    def write_volume(self, obj:Volume, time:float, **kwargs):
        """ write_volume
        Writes a single volume to the vmf file

        Args:
            obj (Volume): volume to be written
            time (float): time of collection for the volume
            time_start (float): time of collection of the first projection used to reconstruct volume
            time_end (float): time of collection of the last projection used to reconstruct volume

        Returns: None

        Raises: Exception: None
        """
        time_start = kwargs.get('time_start', time)
        time_end = kwargs.get('time_end', time)

        if time_start is None or time_end is None:
            time_start, time_end = time, time

        if self.empty: 
            self._new_file(obj.data.shape, obj.pixelsize)

        self._clear_metadata()
        obj_comp = bz2.compress(pickle.dumps(obj))
        dsize = len(obj_comp)

        arr= [time,time_start,time_end,dsize, self.write_index]
        self.metadata.loc[len(self.metadata)]= arr

        with open(self.dir,'ab') as file:
            file.seek(self.write_index)
            file.write(obj_comp)
            self.write_index += int(dsize)

            index = file.tell()
            md = pickle.dumps(self.metadata)
            file.write(md)
            file.write(struct.pack('Q', index))
            file.write(struct.pack('I', len(md)))


    def read_volume(self, i , indexbytime=True):
        """ read_volume
        Reads a single volume from the vmf file

        Args:
            i (int): index of the volume to be read can be either the collection time or the index of the volume stored in metadata.
                e.g. 1 is ether the second volume collected or the volume collected at time 1 depending on indexbytime 
            indexbytime (bool): if true i is interpreted as the collection time if false i is interpreted as the index of the volume stored in metadata

        Returns: Volume

        Raises:
            Exception: 001: the time index does not exist in the set of volumes
        """
    
        if indexbytime:
            try:
                i = self.metadata.loc[self.metadata.times==i].index[0]
            except:
                raise Exception('001: the time index does not exist in the set of volumes')
            
        with open(self.dir, 'rb') as file:
            dsize = self.metadata['dsize'].iloc[i]
            position = self.metadata['position'].iloc[i]
            file.seek(int(position))
            obj = file.read(int(dsize))
            s = len(obj)
            obj = pickle.loads(bz2.decompress(obj))

        
        return Volume(obj)

    def _clear_metadata(self):
        with open(self.dir,'rb+') as file:
            file.seek(self.write_index)
            file.truncate()


    def read_metadata(self):
        """ read_metadata
        Reads the metadata from the end of the file
        Args: None

        Returns: None

        Raises: Exception: None
        """

        with open(self.dir,'rb') as file:
            version = tuple(struct.unpack('3I',file.read(12)))
            shape = tuple(struct.unpack('3I',file.read(12)))
            pixelsize = struct.unpack('f',file.read(4))[0]

            file.seek(-12,2)
            index = struct.unpack('Q',file.read(8))[0]
            size = struct.unpack('I',file.read(4))[0]
            file.seek(int(index))
            self.metadata = pickle.loads(file.read(size))
            file.seek(int(index))

            times = np.array(self.metadata.times)
            times_start = np.array(self.metadata.times_start)
            times_end = np.array(self.metadata.times_end)
            a, b = np.array(self.metadata.dsize), np.array(self.metadata.position)
            self.write_index = int(a[-1]+b[-1])


            _dict = {
                'version': version,
                'shape': shape,
                'pixelsize': pixelsize,
                'times': times,
                'times_start': times_start,
                'times_end': times_end
            }
            return _dict

    def _new_file(self, shape, pixelsize):
        with open(self.dir,'wb') as file:
            file.write(struct.pack('3I', *self.version))
            file.write(struct.pack('3I', *shape))
            file.write(struct.pack('f', pixelsize))

        self.empty = False



    
