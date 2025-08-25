import numpy as np
import skimage
import scipy
import enum
from tomondt.utils.context import device_context, DeviceContextEnum, DtypesEnum
import logging

if device_context.availability.torch:
    import torch
    import torch.nn.functional as F
    import torchvision.transforms.functional as TF

if device_context.availability.cupy:
    import cupy as cp


def _checkdevice(array):
    context = _checkcontext(array)
    match context:
        case DeviceContextEnum.NUMPY:
            return 0
        case DeviceContextEnum.TORCH:
            return array.device.index
        case DeviceContextEnum.CUPY:
            return cp.cuda.Device().id
        case _:
            return -1
        

def _checkcontext(array):
    context =  None
    try:
        if isinstance(array, list):
            context = DeviceContextEnum.LIST
    except:
        pass
    try: 
        if isinstance(array, np.ndarray):
            context = DeviceContextEnum.NUMPY
    except:
        pass
    try:
        if isinstance(array, torch.Tensor):
            context = DeviceContextEnum.TORCH
    except:
        pass
    try:
        if isinstance(array, cp.ndarray):
            context = DeviceContextEnum.CUPY
    except:
        pass
    return context

def _astype(array, context, dtype):
    dtype = _gettype(context, dtype)
    context = _checkcontext(array)
    match context:
        case DeviceContextEnum.NUMPY:
            return np.astype(array,dtype)
        case DeviceContextEnum.TORCH:
            return array.to(dtype)
        case DeviceContextEnum.CUPY:
            return cp.astype(array,dtype)

def _gettype(context, dtype):
    match (context, dtype):
        case (DeviceContextEnum.NUMPY, DtypesEnum.FLOAT32):
            return np.float32
        case (DeviceContextEnum.NUMPY, DtypesEnum.FLOAT64):
            return np.float64
        case (DeviceContextEnum.NUMPY, DtypesEnum.INT8):
            return np.int8
        case (DeviceContextEnum.NUMPY, DtypesEnum.INT16):
            return np.int16
        case (DeviceContextEnum.NUMPY, DtypesEnum.INT32):
            return np.int32
        case (DeviceContextEnum.NUMPY, DtypesEnum.INT64):
            return np.int64
        case (DeviceContextEnum.NUMPY, DtypesEnum.UINT8):
            return np.uint8
        case (DeviceContextEnum.NUMPY, DtypesEnum.UINT16):
            return np.uint16
        case (DeviceContextEnum.NUMPY, DtypesEnum.UINT32):
            return np.uint32
        case (DeviceContextEnum.NUMPY, DtypesEnum.UINT64):
            return np.uint64
        case (DeviceContextEnum.NUMPY, DtypesEnum.BOOL):
            return np.bool
        case (DeviceContextEnum.TORCH, DtypesEnum.FLOAT32):
            return torch.float32
        case (DeviceContextEnum.TORCH, DtypesEnum.FLOAT64):
            return torch.float64
        case (DeviceContextEnum.TORCH, DtypesEnum.INT8):
            return torch.int8
        case (DeviceContextEnum.TORCH, DtypesEnum.INT16):
            return torch.int16
        case (DeviceContextEnum.TORCH, DtypesEnum.INT32):
            return torch.int32
        case (DeviceContextEnum.TORCH, DtypesEnum.INT64):
            return torch.int64
        case (DeviceContextEnum.TORCH, DtypesEnum.UINT8):
            return torch.uint8
        case (DeviceContextEnum.TORCH, DtypesEnum.UINT16):
            return torch.uint16
        case (DeviceContextEnum.TORCH, DtypesEnum.UINT32):
            return torch.uint32
        case (DeviceContextEnum.TORCH, DtypesEnum.UINT64):
            return torch.uint64
        case (DeviceContextEnum.TORCH, DtypesEnum.BOOL):
            return torch.bool
        case (DeviceContextEnum.CUPY, DtypesEnum.FLOAT32):
            return cp.float32
        case (DeviceContextEnum.CUPY, DtypesEnum.FLOAT64):
            return cp.float64
        case (DeviceContextEnum.CUPY, DtypesEnum.INT8):
            return cp.int8
        case (DeviceContextEnum.CUPY, DtypesEnum.INT16):
            return cp.int16
        case (DeviceContextEnum.CUPY, DtypesEnum.INT32):
            return cp.int32
        case (DeviceContextEnum.CUPY, DtypesEnum.INT64):
            return cp.int64
        case (DeviceContextEnum.CUPY, DtypesEnum.UINT8):
            return cp.uint8
        case (DeviceContextEnum.CUPY, DtypesEnum.UINT16):
            return cp.uint16
        case (DeviceContextEnum.CUPY, DtypesEnum.UINT32):
            return cp.uint32
        case (DeviceContextEnum.CUPY, DtypesEnum.UINT64):
            return cp.uint64
        case (DeviceContextEnum.CUPY, DtypesEnum.BOOL):
            return cp.bool
        case (_, _):
            raise Exception('001 - Invalid Data Type', context, dtype)
    

def _checkavailable(context, device=0):
    available = False
    match context:
        case DeviceContextEnum.LIST :
            return True
        case DeviceContextEnum.NUMPY:
            return True
        case DeviceContextEnum.TORCH:
            available = device_context.availability.torch
            if device != -1 and device < device_context.availability.ngpus:
                available = device_context.availability.torch_cuda
            return available
        case DeviceContextEnum.CUPY:
            available = device_context.availability.cupy
            if device != -1 and device < device_context.availability.ngpus:
                available = device_context.availability.cupy_cuda
            return available
        case _ :
            return False

def _numpy_to_torch(array, device=0):
    return torch.from_numpy(array).to(device)

def _numpy_to_cupy(array, device=0):
    if device == -1:
        return cp.asarray(array)  
    cp.cuda.Device(device).use()
    return cp.asarray(array)

def _torch_to_numpy(array):  
    return array.cpu().detach().numpy()

def _torch_to_cupy(array, device=0):
    array = _torch_to_numpy(array)
    if device == -1:
        return cp.asarray(array)
    cp.cuda.Device(device).use()
    return cp.asarray(array)

def _cupy_to_numpy(array):
    return cp.asnumpy(array)

def _cupy_to_torch(array, device=0):
    array = cp.asnumpy(array)
    return _numpy_to_torch(array, device)



def permute(array, index):
    context = _checkcontext(array)
    match context:
        case DeviceContextEnum.NUMPY:
            return np.transpose(array, index)
        case DeviceContextEnum.TORCH:
            return torch.permute(array, index)
        case DeviceContextEnum.CUPY:
            return cp.transpose(array, index)

def rot90(array, k=1, axes=(0,1)):
    context = _checkcontext(array)
    match context:
        case DeviceContextEnum.NUMPY:
            return np.rot90(array, k=k, axes=axes)
        case DeviceContextEnum.TORCH:
            return torch.rot90(array, k=k, dims=axes)
        case DeviceContextEnum.CUPY:
            return cp.rot90(array, k=k, axes=axes)
        
def zeros(shape, context, device=0):
    if not _checkavailable(context,device):
        logging.warning('The context selected is not available - returning numpy array')
        context = DeviceContextEnum.NUMPY
    match context:
        case DeviceContextEnum.NUMPY:
            return np.zeros(shape)
        case DeviceContextEnum.TORCH:
            return torch.zeros(shape).to(device)
        case DeviceContextEnum.CUPY:
            return cp.zeros(shape)
        
def empty(self, context, device=0):
    if not _checkavailable(context,device):
        logging.warning('The context selected is not available - returning numpy array')
        context = DeviceContextEnum.NUMPY
    match self.context:
        case DeviceContextEnum.NUMPY:
            return np.array([])
        case DeviceContextEnum.TORCH:
            return torch.tensor([]).to(self.device)
        case DeviceContextEnum.CUPY:
            return cp.array([])
        

def shape(array):
    context = _checkcontext(array)
    match context:
        case DeviceContextEnum.NUMPY:
            return np.shape(array)
        case DeviceContextEnum.TORCH:
            return torch.shape(array)
        case DeviceContextEnum.CUPY:
            return cp.shape(array)


def convertcontext(array, context_out, device=0):
        context = _checkcontext(array)
        if not _checkavailable(context_out,device):
            logging.warning('The context selected is not available - returning numpy array')
            context_out = DeviceContextEnum.NUMPY

        if context == context_out:
            return array
        
        if context == DeviceContextEnum.LIST:
            array = np.array(array)
            context = DeviceContextEnum.NUMPY

        match (context, context_out):
            case (DeviceContextEnum.NUMPY, DeviceContextEnum.TORCH):
                return _numpy_to_torch(array, device)
            case (DeviceContextEnum.NUMPY, DeviceContextEnum.CUPY):
                return _numpy_to_cupy(array, device)
            case (DeviceContextEnum.NUMPY, DeviceContextEnum.NUMPY):
                return array
            case (DeviceContextEnum.TORCH, DeviceContextEnum.NUMPY):
                return _torch_to_numpy(array)
            case (DeviceContextEnum.TORCH, DeviceContextEnum.CUPY):
                return _torch_to_cupy(array, device)
            case (DeviceContextEnum.TORCH, DeviceContextEnum.TORCH):
                return array
            case (DeviceContextEnum.CUPY, DeviceContextEnum.NUMPY):
                return _cupy_to_numpy(array)
            case (DeviceContextEnum.CUPY, DeviceContextEnum.TORCH):
                return _cupy_to_torch(array, device)
            case (DeviceContextEnum.CUPY, DeviceContextEnum.CUPY):
                return array
            case (_, _):
                raise Exception('001 - Invalid Data Type', context, context_out)

        """Past this point is stuff that needs to be implemented correctly later: todo
        """
def min_max(obj, axis=0):
    if torch.is_tensor(obj):
        return torch.min(obj, axis=axis), torch.max(obj, axis=axis)
    elif isinstance(obj,np.ndarray):
        return np.min(obj,axis=axis), np.max(obj,axis=axis)
    elif isinstance(obj,cp.ndarray):
        return cp.min(obj,axis=axis), cp.max(obj,axis=axis)
    else:
        raise Exception('001 - Invalid Data Type')
    


        

    
def var(obj):
    if torch.is_tensor(obj):
        return torch.var(obj)
    elif isinstance(obj,np.ndarray):
        return np.var(obj)
    elif isinstance(obj,cp.ndarray):
        return cp.var(obj)
    else:
        raise Exception('001 - Invalid Data Type')
    
def cov(obj1, obj2):
    if torch.is_tensor(obj1) and torch.is_tensor(obj2):
        return torch.cov(obj1,obj2)
    elif isinstance(obj1,np.ndarray) and isinstance(obj2,np.ndarray):
        return np.cov(obj1,obj2)
    elif isinstance(obj1,cp.ndarray) and isinstance(obj2,cp.ndarray):
        return cp.cov(obj1,obj2)
    else:
        raise Exception('001 - Invalid Data Type')