import os 
import numpy as np
import pandas as pd
import pickle
import bz2
import struct
import io

from . import VolumeNDt

""" VolumenDt_v0 class:
Inherits from VolumenDt class. Version 0 of the vmf file format

Attributes:
    base class attributes (see VolumenDt)
    self.metadata (pd.DataFrame): metadata of the vmf file

Methods:
    base class methods (see VolumenDt)
    read_record: reads a single volume from the vmf file
    write_record: writes a single volume to the vmf file
    Internal:
    _read_metadata: reads the metadata from the end of the file
    _clear_metadata: clears the metadata from the end of the file

Raises: 
    Exception:
        001: Cannot overweite existing directory with new file

Returns: None

"""
class VolumeNDt_0v(VolumeNDt):
    def __init__(self, dir, obj=None):
        super().__init__(dir)
        self.metadata = pd.DataFrame(columns=['times','times_start','times_end','dsize','position'])
        self.empty = not os.path.isfile(self.dir)

        if not self.empty:
            if obj is None:
                self._read_metadata()
            else:
                raise Exception("001: Cannot overwrite existing directory with new file")
        else:
            if obj is None:
                pass
            else:
                self.write_record(obj,0)


    """ write_record
    Writes a single volume to the vmf file

    Args:
        obj (np.array): volume to be written
        time (float): time of collection for the volume
        time_start (float): time of collection of the first projection used to reconstruct volume
        time_end (float): time of collection of the last projection used to reconstruct volume

    Returns: None

    Raises: Exception: None
    """
    def write_record(self, obj, time, time_start=None, time_end=None):
        if time_start is None or time_end is None:
            time_start, time_end = time, time

        if self.empty: 
            self._new_file(obj.shape)

        self._clear_metadata()

        self.times = np.append(self.times,time)
        self.times_start =np.append(self.times_start, time_start)
        self.times_end = np.append(self.times_end, time_end)

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

    """ read_record
    Reads a single volume from the vmf file

    Args:
        i (int): index of the volume to be read can be either the collection time or the index of the volume stored in metadata.
            e.g. 1 is ether the second volume collected or the volume collected at time 1 depending on indexbytime 
        indexbytime (bool): if true i is interpreted as the collection time if false i is interpreted as the index of the volume stored in metadata

    Returns: None

    Raises:
        Exception: 001: the time index does not exist in the set of volumes
    """
    def read_record(self, i , indexbytime=True):
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
                return obj
    """ _new_file
    Creates a new vmf file with base metadata
    
    Args:  
        shape (tuple): shape of the volumes in the vmf file

    Returns: None

    Raises: Exception: None
    """
    def _new_file(self, shape):
        self.version = (0,0,1) 
        super()._new_file(shape)

    """ _clear_metadata
    Clears the metadata from the end of the file
    #TODO: really dont like this file storage method potential to erase metadata in power shut down - low but not impossible data volatile
    
    Args: None

    Returns: None

    Raises: Exception: None
    """
    def _clear_metadata(self):
        with open(self.dir,'rb+') as file:
            file.seek(self.write_index)
            file.truncate()   

    """ _read_metadata
    Reads the metadata from the end of the file
    Args: None

    Returns: None

    Raises: Exception: None
    """
    def _read_metadata(self):
        super()._read_metadata()

        with open(self.dir,'rb') as file:
            file.seek(-12,2)
            index = struct.unpack('Q',file.read(8))[0]
            size = struct.unpack('I',file.read(4))[0]
            file.seek(int(index))
            self.metadata = pickle.loads(file.read(size))
            file.seek(int(index))

            self.times = np.array(self.metadata.times)
            self.times_start = np.array(self.metadata.times_start)
            self.times_end = np.array(self.metadata.times_end)
            a, b = np.array(self.metadata.dsize), np.array(self.metadata.position)
            self.write_index = int(a[-1]+b[-1])

  