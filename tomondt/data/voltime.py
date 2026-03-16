from tomobase.data import ImageAbstract
import xarray as xr
import dask.array as da
import pathlib
import os 
import numpy as np

class VolumeTimeSeries(ImageAbstract):
    readers: dict[str, callable] = {}
    writers: dict[str, callable] = {}
    metadata_writers: dict[str, callable] = {}

    def __init__(self, name, path, data, pixelsize: float = 1.0, metadata: dict = {},  *args, **kwargs):
        self.path = path
        self.data = data
        self.pixel_size = pixelsize
        super().__init__(name, data, dims, pixelsize, metadata, *args, **kwargs)


        if path is None:
            project_root = pathlib.Path(__file__).resolve().parents[3] 
            autosave_dirs = list(project_root.rglob("autosave"))
            self.path = pathlib.Path(os.path.join(autosave_dirs[0], f'{name}.zarr'))

            if not isinstance(data, xr.DataArray):
                if len(data.shape) == 4:
                    dims = ['indices', 'z', 'y', 'x']
                    chunks = (1, 64, 256, 256)
                elif len(data.shape) == 5:
                    dims = ['indices', 'signals', 'z', 'y', 'x']
                    chunks = (1, 1, 64, 256, 256)

                data = da.from_array(data, chunks=chunks) 

            super().__init__(name, data, dims, pixelsize, metadata, *args, **kwargs)
            len_indices = self._data.sizes['indices']
            times = kwargs.get('times', np.arange(len_indices)+1)

            if len(times) != len_indices:
                raise ValueError(f"Length of times {len(times)} does not match length of indices {len_indices}")
            self.data = self.data.assign_coords(indices = np.arange(len_indices), times = ('indices', times))
            
            self.write_metadata()

        else:
            if isinstance(path, str):
                path = pathlib.Path(path)
            self.path = pathlib.Path(path)

        
        self.read(path)
        #self.data.to_zarr(self.path, mode='w')
        #self.data = xr.open_dataarray(self.path, engine="zarr", chunks='auto')

    def append(self, volume, axis='indices'):
        if axis == 'indices':
            start = self.data.sizes[axis]
            n_new = volume.sizes[axis]
            volume = volume.assign_coords({axis: np.arange(start, start + n_new)})

            if 'times' in volume.coords:
                start_time = self.data.coords['times'].values[-1]
                volume = volume.assign_coords(times = ('indices', volume.coords['times'].values + start_time))

        volume.to_zarr(self.path, append_dim=axis)
        self.data = xr.open_dataarray(self.path, engine="zarr", chunks='auto')

    def _copy_from(self, other:'VolumeTimeSeries'):
        return super()._copy_from(other=other)
    
    def _deepcopy_from(self, other:'VolumeTimeSeries', memo:dict={}):
        return super()._deepcopy_from(other=other, memo=memo)

    @classmethod
    def from_metadata(cls, directory: pathlib.Path | str):
        if isinstance(directory, str):
            directory = pathlib.Path(directory)

        cls.read(directory)   
        data = xr.open_dataarray(directory, engine="zarr", chunks='auto')
        name = data.attrs['name']
        return cls(name=name, data=data)
    
        self.data = xr.open_dataarray(directory, engine="zarr", chunks='auto')


    def create(self, name, data, dims, pixel_size=1.0, metadata=None, *args, **kwargs):
        return type(self)(name, None, data, pixel_size, metadata, *args, **kwargs   )
VolumeTimeSeries.readers = {}
VolumeTimeSeries.writers = {}
VolumeTimeSeries.metadata_writers = {}