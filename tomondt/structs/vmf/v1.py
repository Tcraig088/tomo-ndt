import os
import numpy as np
import pandas as pd
import struct 
import blosc
from tomondt.utils.context import DeviceContextEnum, DtypesEnum
from tomondt import utils
from . import VolumeNDt
# Supported Compression algorithms for the vmf file format
compression_codes = [
    'none', # No compression
    'blosclz',  # Bloscs default 
    'lz4', # LZ4 compression library.
    'lz4hc', # High Compression variant of LZ4.
    'snappy', # fast library
    'zlib',   # high compression library
    'zstd'
]
"""
Supported dtypes for the vmf file format
"""
type_codes = [
    'b',  # signed byte
    'B',  # unsigned byte
    'h',  # signed short
    'H',  # unsigned short
    'i',  # signed int
    'I',  # unsigned int
    'l',  # signed long
    'L',  # unsigned long
    'q',  # signed long long
    'Q',  # unsigned long long
    'f',  # 32-bit float
    'd',  # 64-bit (double precision) float
    '?',  # boolean
]

""" VolumenDt_v0 class:
Inherits from VolumenDt class. Version 0 of the vmf file format

Attributes:
    base class attributes (see VolumenDt)
    metadata (pd.DataFrame): metadata of the vmf file
    read_info (list/tuple): information on how to read the vmf file
        index 0: compression algorithm used
        index 1: dtype of the data
    timeunit (str): unit of time for the vmf file
    spaceunit (str): unit of space for the vmf file
    notes (str): notes for the vmf file

Methods:
    base class methods (see VolumenDt)
    read_record: reads a single volume from the vmf file
    write_record: writes a single volume to the vmf file
    Internal:
    _new_file: creates a new vmf file when an object is supplied and no file exists -external implementation can erase existing files!!!!
    _read_metadata: reads the metadata from the end of the file
    _write_metadata: writes the metadata to the end of the file
    _binarize_obj: converts the object to bytes and compresses it
    _debinarize_obj: decompresses the object and converts it to the correct dtype


Raises: 
    Exception:
        001: Cannot overwrite existing directory with new file

Returns: None

"""
class VolumeNDt_1v(VolumeNDt):
    def __init__(self, dir, obj=None):
        super().__init__(dir)

        self.metadata = pd.DataFrame(columns=['times','times_start','times_end','dsize','position'])
        self.read_info = [1,8]
        self.timeunit = 's'
        self.spaceunit = 'voxels'
        self.notes = ''

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
            self._new_file(obj)

        self.times = np.append(self.times,time)
        self.times_start = np.append(self.times_start, time_start)
        self.times_end = np.append(self.times_end, time_end)

        obj = self._binarize_obj(obj)

        arr= [time,time_start,time_end, len(obj), self.write_index + 20]
        self.metadata.loc[len(self.metadata)]= arr

        with open(self.dir,'ab') as file:
            file.seek(self.write_index)
            file.write(struct.pack('fff', time, time_start, time_end))
            file.write(struct.pack('Q', len(obj)))
            self.write_index = file.tell()
            file.write(obj)

            self.write_index = file.tell()

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
                obj = self._debinarize_obj(obj)
                obj = utils.convertcontext(obj, self.context, self.device)
                return obj

    """ _new_file
    Creates a new vmf file with base metadata
    
    Args:  
        obj (np.array): volume to be written

    Returns: None

    Raises: Exception: None
    """
    def _new_file(self, obj):
        self.version = (1,0,0) 
        super()._new_file(obj.shape)
        dtype = obj.dtype.char
        dtype = type_codes.index(dtype)
        self.read_info = tuple([self.read_info[0], dtype])
        with open(self.dir,'ab') as file:
            file.seek(self.write_index)
            file.write(struct.pack('2I', *self.read_info))
            file.write(struct.pack('2I', len(self.timeunit),len(self.spaceunit)))
            file.write(self.timeunit.encode('utf-8'))
            file.write(self.spaceunit.encode('utf-8'))

            file.write(struct.pack('I', len(self.notes)))
            if len(self.notes)>0:
                file.write(struct.pack(str(len(self.notes))+'s', self.notes.encode('utf-8')))

            self.write_index = file.tell()

    """ _read_metadata
    Reads the metadata from the end of the file
    Args: None

    Returns: None

    Raises: Exception: None
    """
    def _read_metadata(self):
        super()._read_metadata()

        end  = os.path.getsize(self.dir)
        with open(self.dir,'rb') as file:
            file.seek(28)
            self.read_info = tuple(struct.unpack('2I',file.read(8)))
            ntime,nspace = struct.unpack('2I',file.read(8))
            self.timeunit,self.spaceunit = file.read(ntime).decode('utf-8'),file.read(nspace).decode('utf-8')
            nnote = struct.unpack('I',file.read(4))[0]
            if nnote >0:
                self.notes = file.read(nnote).decode('utf-8')

            while file.tell()<end:
                self.write_index = file.tell()
                time,time_start,time_end = struct.unpack('fff',file.read(12))
                dsize = struct.unpack('Q',file.read(8))[0]
                self.metadata.loc[len(self.metadata)]= [time,time_start,time_end,dsize,self.write_index+20]
                self.times = np.array(self.metadata.times)
                self.times_start = np.array(self.metadata.times_start)
                self.times_end = np.array(self.metadata.times_end)
                file.seek(int(dsize)+self.write_index + 20)

    """ _binarize_obj
    Reads the metadata from the end of the file
    Args: 
        obj (np.array): volume to be written

    Returns: 
        obj (binary): compressed binary for writing

    Raises: Exception: None
    """
    def _binarize_obj(self,obj):

        obj = obj.astype(type_codes[self.read_info[1]]).tobytes()
        if 0:
            return obj
        elif 1 <= self.read_info[0] <= 6:
            return blosc.compress(obj, cname=compression_codes[self.read_info[0]])
        else:
            raise Exception('001: Unsupported Compression Algorithm - see docstring for details')

    """ _debinarize_obj
    Reads the metadata from the end of the file
    Args:
        obj (binary): compressed binary for writing 

    Returns: 
       obj (np.array): volume to be written

    Raises: 
        Exception: 
            001: Unsupported Compression Algorithm - see docstring for details
    """
    def _debinarize_obj(self,obj):
        if 0:
            pass
        elif 1<= self.read_info[0] <= 6:
            obj =  blosc.decompress(obj)
        else:
            raise Exception('001: Unsupported Compression Algorithm - see docstring for details')

        obj = np.frombuffer(obj, dtype=type_codes[self.read_info[1]])
        return obj.reshape(self.shape)
    
