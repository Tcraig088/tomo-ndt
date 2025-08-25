import os 
import enum
import random
class DeviceContextEnum(enum.Enum):
    NUMPY = 0
    TORCH = 1
    CUPY = 2      
    LIST = 3    


class DtypesEnum(enum.Enum):
    FLOAT32 = 0
    FLOAT64 = 1
    INT8 = 2
    INT16 = 3
    INT32 = 4
    INT64 = 5
    UINT8 = 6
    UINT16 = 7
    UINT32 = 8
    UINT64 = 9
    BOOL = 10
class DeviceAvailabilty:
    def __init__(self):
        self.torch = False
        self.torch_cuda = False
        self.cupy_cuda = False
        self.cupy = False
        self.numpy = True
        self.ngpus = 0 
        self.refresh()

    def refresh(self):
        try :
            import torch
            self.torch = True
            try:
                self.torch_cuda = torch.cuda.is_available()
            except ImportError:
                self.torch_cuda = False
        except ImportError:
            self.torch = False
            self.torch_cuda = False

        try:
            import cupy
            self.cupy = True
            try:
                self.cupy_cuda = cupy.cuda.is_available()
            except ImportError:
                self.cupy_cuda = False
        except ImportError:
            self.cupy = False
            self.cupy_cuda = False

        if self.torch_cuda:
            self.ngpus = torch.cuda.device_count()
        elif self.cupy_cuda:
            self.ngpus = cupy.cuda.runtime.getDeviceCount()

    def to_dict(self):
        return {'torch':self.torch, 'torch_cuda':self.torch_cuda, 'cupy':self.cupy, 'cupy_cuda':self.cupy_cuda, 'numpy':self.numpy, 'ngpus':self.ngpus}
class DeviceContextManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.availability = DeviceAvailabilty()
            cls._instance.dir = os.path.join(os.getcwd(),'temp_data')
            cls._instance._makedir()
        return cls._instance
    
    def _makedir(self):
        #if path exists empty it 
        if os.path.exists(self.dir):
            for file in os.listdir(self.dir):
                os.remove(os.path.join(self.dir,file))
        if not os.path.exists(self.dir):
            os.makedirs(self.dir)
    
    def changepath(self, path):
        #delete old directory and everything in it
        if os.path.exists(self.dir):
            for file in os.listdir(self.dir):
                os.remove(os.path.join(self.dir,file))
            os.rmdir(self.dir)
        self.dir = path
        self._makedir()

    def getfile(self, name):
        #check if temp exists in directory if it does add random number to name recheck if it exists until new name doesnt exist
        while os.path.exists(os.path.join(self.dir,name)):
            #split ext before addding random number 
            name, ext = os.path.splitext(name)
            name = 'temp'+str(random.randint(0,100000))+ext
        return os.path.join(self.dir,name)
    
    def to_dict(self):
        return {'dir':self.dir, 'availability':self.availability.to_dict()}
device_context = DeviceContextManager()
