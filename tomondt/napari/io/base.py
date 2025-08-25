import os
import enum
import dask.array as da
from dask.delayed import delayed

from typing import Callable, List, Optional, Sequence, Union, Any, Dict
from napari.types import LayerData

from ...io import read_vmf, read_h5, read_mat, write_mat, write_h5
from ..data_types import convert_type_to_layer, convert_layer_to_type

# example_plugin.some_module
PathLike = str
PathOrPaths = Union[PathLike, Sequence[PathLike]]
ReaderFunction = Callable[[PathOrPaths], List[LayerData]]

class TiltSeriesFormats(enum.Enum):
    H5 = '.h5',
    MAT = '.mat'

def get_reader_volumendt(path: PathOrPaths) -> Optional[ReaderFunction]:
    # If we recognize the format, we return the actual reader function
    if isinstance(path, str) and path.endswith(".vmf"):
        return vmf_file_reader
    # otherwise we return None.
    return None

def vmf_file_reader(path: PathOrPaths) -> List[LayerData]:
    obj = read_vmf(path)
    shape = obj.shape
    dtype = obj.read_record(0, False).dtype

    lazy_imread = delayed(obj.read_record)
    lazy_arrays = [lazy_imread(t) for t in obj.times]
    dask_arrays = [
        da.from_delayed(delayed_reader, shape=shape, dtype=dtype)
        for delayed_reader in lazy_arrays
    ]
    stack = da.stack(dask_arrays, axis=0)
    #get file pathname
    name = os.path.basename(path)
    metadata = {"NDTType":"VolumeNDT", "times":obj.times}
    layer_attributes = {"name": name, "metadata":metadata}
    return [(stack, layer_attributes)]


def get_reader_tiltseriesndt(path: PathOrPaths) -> Optional[ReaderFunction]:
    # If we recognize the format, we return the actual reader function
    if isinstance(path, str):
        #if path ends with a supported format
        if any(path.endswith(format.value) for format in TiltSeriesFormats):
            return tiltseriesndt_file_reader
    return None


def tiltseriesndt_file_reader(path: PathOrPaths) -> List[LayerData]:
    name = os.path.basename(path)
    if path.endswith(TiltSeriesFormats.H5.value):
        obj = read_h5(path)
    elif path.endswith(TiltSeriesFormats.MAT.value):
        obj = read_mat(path)
        
    data, metadata = convert_type_to_layer(obj)
    layer_attributes = {"name": name, "metadata":metadata}
    return [(data, layer_attributes)]

# example_plugin.some_module
def tiltseriesndt_file_writer(path: str, data: Any) -> List[str]:
    ts = convert_layer_to_type(data[0][0], data[0][1])
    if path.endswith(TiltSeriesFormats.H5.value):
        write_h5(path, ts)
    elif path.endswith(TiltSeriesFormats.MAT.value):
        write_mat(path, ts)
    else:
        path = path + TiltSeriesFormats.H5.value
        write_h5(path, ts)
        
    # return path to any file(s) that were successfully written
    return [path]