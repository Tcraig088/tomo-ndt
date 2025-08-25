import os
import coolname
import numpy as np

from tomobase.data.base import Data
from tomobase.log import logger
from tomobase.globals import TOMOBASE_DATATYPES

from tomondt.io.vmf import VMF
import dask.array as da
from dask.delayed import delayed

TOMOBASE_DATATYPES.append(VolumeNDt=None)

class VolumeNDt(Data):
    """A class representing a time series of volumes.

    Supported File Types:
        .vmf: Volume Metadata Format (custom compressed format)

    Attributes:
        directory (str): The directory containing the volume files.
        times (np.array): The collection times of the volumes.

    """
    def __init__(self, path=None, volume=None, time=None, metadata={}):
        if path is None:
            self.path = os.path.join(os.getcwd(), coolname.generate_slug(2)+'.vmf')
        else: 
            self.path = path
        self.get_readers_writers()

        if os.path.isfile(self.path):
            if os.path.getsize(self.path) < (4*10^6):
                self._setup_new(volume)
            else:
                self.setup_from_path()
        else:
            self._setup_new(volume)

    def _setup_new(self, volume, time=0):
        if volume is None:
            raise ValueError("Volume data must be provided for a new file.")
        self.io.write_volume(volume, time)
        self.metadata = self.io.read_metadata()
        self.times = self.metadata.pop('times', None)
        self.shape = self.metadata.pop('shape', None)
        self.dtype = self.metadata.pop('dtype', None)
        self.pixelsize = self.metadata.pop('pixelsize', 1.0)
        super().__init__(pixelsize=self.pixelsize, metadata=self.metadata)

    def setup_from_path(self):
        self.read_metadata()
        super().__init__(pixelsize=self.pixelsize, metadata=self.metadata)

    def get_readers_writers(self):
        ext = os.path.splitext(self.path)[1]
        match ext:
            case '.vmf':
                self.io = VMF(self.path)
            case _:
                raise ValueError(f"Unsupported file type: {ext}")

    _readers = {}
    _writers = {}

    @staticmethod
    def _read_file(cls, path):
        return cls(path)

    def layer_attributes(self, attributes={}):
        attr = super().layer_attributes(attributes)
        attr['name'] = attributes.get('name', 'Volume')
        attr['scale'] = attributes.get('pixelsize', (self.pixelsize, self.pixelsize, self.pixelsize))
        attr['colormap'] = attributes.get('colormap', 'magma')
        attr['rendering'] = attributes.get('rendering', 'attenuated_mip')
        attr['contrast_limits'] = attributes.get('contrast_limits', [0, np.max(self.data)*1.5])
        return attr

    

    def layer_metadata(self, metadata={}):
        meta = super().layer_metadata(metadata)
        meta['ct metadata']['type'] = TOMOBASE_DATATYPES.VOLUMENDT.value
        meta['ct metadata']['axis'] = ['t', 'z', 'y', 'x']
        meta['ct metadata']['times'] = self.times
        return meta


    def to_data_tuple(self, attributes:dict={}, metadata:dict={}):
        attributes = self.layer_attributes(attributes)
        metadata = self.layer_metadata(metadata)
        attributes['metadata'] = metadata


        lazy_imread = delayed(self.read_volume)
        lazy_arrays = [lazy_imread(t) for t in self.times]
        dask_arrays = [
            da.from_delayed(delayed_reader, shape=self.shape, dtype=self.dtype) for delayed_reader in lazy_arrays
        ]
        stack = da.stack(dask_arrays, axis=0)
        layerdata = (stack, attributes, 'image')
        logger.debug(f"Created layerdata tuple: {layerdata}")
        return layerdata
    
    @classmethod
    def from_data_tuple(cls, layer, attributes=None):
        if attributes is None:
            data = layer.data
            scale = layer.scale[0]
            layer_metadata = layer.metadata['ct metadata']
        else:
            data = layer
            scale = attributes['scale'][0]
            layer_metadata = attributes['metadata']['ct metadata']


        return cls(data, scale, layer_metadata)

    def write_volume(self, volume, time, **kwargs):
        self.io.write_volume(volume, time, **kwargs)
        self.io.read_metadata()

    def read_volume(self, time, **kwargs):
        return self.io.read_volume(time, **kwargs)

    def read_metadata(self):
        metadata = self.io.read_metadata() 
        self.times = metadata.pop('times', None)
        self.pixelsize = metadata.pop('pixelsize', 1.0)
        self.shape = metadata.pop('shape', None)
        self.metadata = metadata
        return

# the readers and writers for VolumeNDt do not work the same way as in tomobase
# here it sets up a mapping from file extensions to the appropriate reader/writer methods
VolumeNDt._readers = {
    'vmf': VolumeNDt._read_file
}

