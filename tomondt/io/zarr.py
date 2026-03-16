import xarray as xr
import dask.array as da

import pathlib
import os

from ..data import VolumeTimeSeries

def read_zarr(directory: pathlib.Path | str):
    data = xr.open_dataarray(directory, engine="zarr", chunks='auto')
    name = data.attrs['name']

    VolumeTimeSeries.from_dir()