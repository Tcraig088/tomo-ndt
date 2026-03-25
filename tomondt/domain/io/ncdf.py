import xarray as xr
import dask.array as da

import pathlib
import os

from ...depreciated.data import VolumeTimeSeries

def _read_netcdf(directory: pathlib.Path | str, *args, **kwargs):
    data = xr.open_dataarray(directory, chunks='auto')
    name = data.attrs['name']
    metadata = data.attrs.get('metadata', {})
    return VolumeTimeSeries(path=directory, name=name, data=data, metadata=metadata)


def _write_netcdf(vts: VolumeTimeSeries, directory: pathlib.Path | str, *args, **kwargs):
    if isinstance(directory, str):
        directory = pathlib.Path(directory)

    name = vts.name
    metadata = vts.metadata
    vts._data.attrs['name'] = name
    vts._data.attrs['metadata'] = metadata
    vts._data.to_netcdf(directory, engine="netcdf4", format='NETCDF4')


VolumeTimeSeries.readers['.nc'] = _read_netcdf
VolumeTimeSeries.writers['.nc'] = _write_netcdf
