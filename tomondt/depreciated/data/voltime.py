from tomobase.core.data_classes import ImageAbstract
import xarray as xr
import dask.array as da
import pathlib
import os 
import numpy as np
import coolname
from tomobase.core.log import logger

class VolumeTimeSeries(ImageAbstract):
    readers: dict[str, callable] = {}
    writers: dict[str, callable] = {}
    record_writers: dict[str, callable] = {}

    def __init__(self, path=None, name=None, data=None, pixel_size=1.0, times=None, chunks=None, metadata=None, *args, **kwargs):
        if name is None:
            name = coolname.generate_slug(2)
        
        if path is None:
            project_root = pathlib.Path(__file__).resolve().parents[3] 
            autosave_dirs = list(project_root.rglob("autosave"))
            path = pathlib.Path(os.path.join(autosave_dirs[0], f'{name}.zarr'))
            
        self.path = path
        if isinstance(path, str):
            self.path = pathlib.Path(path)

        if not isinstance(data, xr.DataArray):
            print(data.shape)
            if len(data.shape) == 4:
                dims = ['indices', 'z', 'y', 'x']
                chunks = (1, 64, 256, 256)
            elif len(data.shape) == 5:
                dims = ['indices', 'signals', 'z', 'y', 'x']
                chunks = (1, 1, 64, 256, 256)

            data = da.from_array(data, chunks=chunks) 
        else:
            dims = data.dims
            pixel_size = data.attrs.get('pixel_size', pixel_size)
        super().__init__(name, data, dims, pixel_size=pixel_size, metadata=metadata, *args, **kwargs)

        len_indices = self._data.sizes['indices']
        times = kwargs.get('times', np.arange(len_indices)+1)

        if len(times) != len_indices:
            raise ValueError(f"Length of times {len(times)} does not match length of indices {len_indices}")
        self._data = self._data.assign_coords(indices = np.arange(len_indices), times = ('indices', times))
            
        if not os.path.exists(self.path):
            logger.info(f"Path {self.path} does not exist. Writing data to {self.path}.")
            self.write(self.path)
            self.read(self.path)


        #self.data.to_zarr(self.path, mode='w')
        #self.data = xr.open_dataarray(self.path, engine="zarr", chunks='auto')

    def append(self, volume, axis='indices'):
        if axis == 'indices':
            start = self._data.sizes[axis]
            print(volume.dims, volume.sizes)
            n_new = volume.sizes[axis]
            volume = volume.assign_coords({axis: np.arange(start, start + n_new)})

            if 'times' in volume.coords:
                start_time = self._data.coords['times'].values[-1]
                volume = volume.assign_coords(times = ('indices', volume.coords['times'].values + start_time))

        volume.to_zarr(self.path, append_dim=axis)
        self._data = xr.open_dataarray(self.path, engine="zarr", chunks='auto')

    def _copy_from(self, other:'VolumeTimeSeries'):
        return super()._copy_from(other=other)
    
    def _deepcopy_from(self, other:'VolumeTimeSeries', memo:dict={}):
        return super()._deepcopy_from(other=other, memo=memo)


VolumeTimeSeries.readers = {}
VolumeTimeSeries.writers = {}
VolumeTimeSeries.record_writers = {}