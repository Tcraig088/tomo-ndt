import xarray as xr
import dask.array as da

import pathlib
import os

from ...core.data_classes import VolumeNDt

def _read_netcdf(directory: pathlib.Path | str, *args, **kwargs):
    data = xr.open_dataarray(directory, chunks='auto')
    name = data.attrs['name']
    metadata = data.attrs.get('metadata', {})
    return VolumeNDt(path=directory, name=name, data=data, metadata=metadata)


def _write_netcdf(vts: VolumeNDt, directory: pathlib.Path | str, *args, **kwargs):
    if isinstance(directory, str):
        directory = pathlib.Path(directory)

    name = vts.name
    metadata = vts.metadata
    vts._data.attrs['name'] = name
    vts._data.attrs['metadata'] = metadata
    vts._data.to_netcdf(directory, engine="netcdf4", format='NETCDF4')


VolumeNDt.readers['.nc'] = _read_netcdf
VolumeNDt.writers['.nc'] = _write_netcdf
