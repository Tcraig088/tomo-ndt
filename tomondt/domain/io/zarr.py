import xarray as xr
import dask.array as da

import pathlib
import os

from ...core.data_classes import VolumeNDt

def _read_zarr(directory: pathlib.Path | str, *args, **kwargs):
    data = xr.open_dataarray(directory, engine="zarr", chunks='auto')
    name = data.attrs['name']
    metadata = data.attrs.get('metadata', {})
    return VolumeNDt(path=directory, name=name, data=data, metadata=metadata)


def _write_zarr(vts: VolumeNDt, directory: pathlib.Path | str):
    if isinstance(directory, str):
        directory = pathlib.Path(directory)

    name = vts.name
    metadata = vts.metadata
    vts._data.attrs['name'] = name
    vts._data.attrs['metadata'] = metadata
    vts._data.to_zarr(directory, mode='w')

def _write_zarr_record(vts: VolumeNDt | str, data: xr.DataArray, *args, **kwargs):
    if isinstance(vts.path, str):
        vts.path = pathlib.Path(vts.path)

    dim = kwargs.get('append_dim', 'indices')
    data.to_zarr(vts.path, append_dim=dim)
    return xr.open_dataarray(vts.path, engine="zarr", chunks='auto')

VolumeNDt.readers['.zarr'] = _read_zarr
VolumeNDt.writers['.zarr'] = _write_zarr
VolumeNDt.record_writers['.zarr'] = _write_zarr_record