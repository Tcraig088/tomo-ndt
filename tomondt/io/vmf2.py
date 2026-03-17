import xarray as xr
import dask.array as da

import pathlib
import os
import dask
import numpy as np
from ..data import VolumeTimeSeries
from ..structs.vmf.v1 import VolumeNDt_1v
from tomobase.log import logger

def _read_vmf_record_unbound(directory, t):
    vmf = VolumeNDt_1v(directory)
    vmf._read_metadata()
    obj = vmf.read_record(t)
    return obj.astype(np.float32)


def _read_vmf(directory: pathlib.Path | str, *args, **kwargs):
    if isinstance(directory, str):
        directory = pathlib.Path(directory)
    vmf  = VolumeNDt_1v(directory)
    vmf._read_metadata()
    name = kwargs.get('name', directory.parent.name)
    metadata = {}
    times = np.unique(vmf.times)
    
    vols = []
    data = vmf.read_record(times[0])
    dtype = np.float32
    logger.debug(f"Reading VMF from {directory} with name {name} and times {len(times)}")    
    for t in times:
        delayed_vol = dask.delayed(_read_vmf_record_unbound)(directory, t)
        d_array = da.from_delayed(delayed_vol, shape=vmf.shape, dtype=dtype)
        vols.append(d_array)
        logger.debug(f"Scheduled read of time {t} with shape {vmf.shape} and dtype {dtype}")
    logger.debug(f"Scheduled reads for all times: {len(times)}")
    data = da.stack(vols, axis=0)

    indices = np.arange(len(times))
    data = xr.DataArray(data, dims=['indices','z', 'y', 'x'])
    data = data.assign_coords(indices = np.arange(len(indices)), times = ('indices', times))
    logger.debug(f"Stacked data type: {data.data} with map {data}")
    return VolumeTimeSeries(path=directory, name=name, data=data, metadata=metadata)


VolumeTimeSeries.readers['.vmf'] = _read_vmf

