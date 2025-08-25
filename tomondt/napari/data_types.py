import enum
import numpy as np
from ..structs import TiltSeriesNDt, VolumeNDt

class NDt_Operations:
    Align = 1
    Project = 2
    Quantify = 3
    Reconstruct = 4
    Segment = 5
    Simulate =  6
"""
This File is used for defining the types for Napari layer data using the Tomo NDt Plugin
Hence these are not the same as the Data Types used in the standalone package.

Note: Perform the following for all NDt Types:
    Add converion into the convert_type_to_layer and convert_layer_to_type functions
    Provide Enum list for Supported files to read and write NDT types to
    Add read write support to the napari yaml 
"""   
class NDt_Types(enum.Enum):
    Volume = 'Volume'
    TiltSeriesNDt = 'TiltSeries NDt'
    VolumeSeriesNDt = 'VolumeSeries NDt'

"""_summary_
 Supported File Formats for the TiltSeries NDt Data Type
"""
class TiltSeriesFormats(enum.Enum):
    H5 = '.h5'
    MAT = '.mat'
    
"""_summary_
 Supported File Formats for the TiltSeries NDt Data Type
"""    
class VolumeSeriesFormats(enum.Enum):
    VMF = '.vmf'

"""
_getlabels:
Returns the labels for the dimensions of the data based on the type of the data

Arguments:
layer: np.ndarray, TiltSeriesnDt or VolumenDt
type: NDt_Types

Returns:
labels: list

Exceptions:
ValueError: Data is not a valid nDt Type
"""
def _getlabels(layer, type):
    labels = []
    match type:
        case NDt_Types.Volume.value:
            if len(layer.data.shape) == 3:
                labels = ['x', 'y', 'z']
            else:
                labels = ['x', 'y', 'z''Signals']
                
        case NDt_Types.TiltSeriesNDt.value:
            if len(layer.data.shape) == 3:
                labels = ['x', 'y','Projections']
            else:
                labels = ['x', 'y','Signals', 'Projections']
                
        case NDt_Types.VolumeSeriesNDt.value:
            if len(layer.data.shape) == 3:
                labels = ['x', 'y', 'z', 'Times']
            else:
                labels = ['x', 'y', 'z', 'Signals', 'Times']
        case _:
            raise ValueError('Data is not a valid nDt Type')
    return labels

""" convert_type_to_layer:
Converts the Types of the Standalone Tomo nDt Package to Annottated Napari Layer Types

Arguments: 
obj: np.ndarray, TiltSeriesnDt or VolumenDt

Returns:
value = np.ndarray
metadata: dict

Exceptions:
ValueError: Data is not a valid nDt Type 

"""
def convert_type_to_layer(obj):  
     # if the data is a ndarray
    metadata = {}
    if isinstance(obj, np.ndarray):
        metadata['NDt Type'] = NDt_Types.Volume.value
        metadata['NDt Dim Labels'] =  _getlabels(obj, NDt_Types.Volume.value)
        value = obj
        
    elif isinstance(obj, TiltSeriesNDt):
        metadata['NDt Type'] = NDt_Types.TiltSeriesNDt.value
        metadata['NDt Dim Labels'] =  _getlabels(obj.data, NDt_Types.TiltSeriesNDt.value)
        metadata['NDt Times'] =  obj.times
        metadata['NDt Angles'] =  obj.angles
        value = obj.data
        
    elif isinstance(obj, VolumenDt):
        metadata['NDt Type'] = NDt_Types.VolumeSeriesNDt.value
        metadata['NDt Dim Labels'] =  _getlabels(obj.data, NDt_Types.VolumeSeriesNDt.value)
        metadata['NDt Times'] =  obj.times
        value = obj.data
        
    else:
        raise ValueError('Data is not a valid nDt Type')
    
    return value, metadata
 
""" convert_layer_to_type:
Converts the Annottated Napari Layer Types to the Types of the Standalone Tomo nDt Package

Arguments:
layer: napari.layers.Layer

Returns:
data: np.ndarray, TiltSeriesnDt or VolumenDt

Exceptions:
ValueError: Data is not a valid nDt Type

"""
def convert_layer_to_type(layer, attributes = None): 
     
     # if the data is a ndarray
    if attributes is None:
        metadata = layer.metadata
    else:
        metadata = attributes['metadata']
    match metadata['NDt Type']:
        case NDt_Types.Volume.value:
            data = np.array(layer.data)
            return data
        case NDt_Types.TiltSeriesNDt.value:
            data = np.array(layer.data)
            times = metadata['NDt Times']
            angles = metadata['NDt Angles']
            return TiltSeriesNDt(data, angles, times)
        case NDt_Types.VolumeSeriesNDt.value:
            data = np.array(layer.data)
            times = metadata['NDt Times']
            return VolumenDt(data, times)
        case _:
            raise ValueError('Data is not a valid nDt Type')
        
def _checklayertype(layer):
    try:
        if 'NDt Type' in layer.metadata:
            return layer.metadata['NDt Type']
    except:
        return None
        
        
        
        
             
        
        
        
      