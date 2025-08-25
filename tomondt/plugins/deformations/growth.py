import numpy as np
from scipy  import ndimage as scin
import copy

from ..decorators import *
from ...utils.context import device_context
if device_context.availability.cupy:
    import cupy as cp
    from cupyx.scipy import ndimage as scicp

class Weibull():
    def __init__(self, shape, scale, yscale):
        self.shape = shape
        self.scale = scale
        self.yscale = yscale
        self.iters = 1
    
    def calclayers(self):
        layers = (self.shape/self.scale)*np.power(self.iters/self.scale, (self.shape-1))*np.exp(-np.power(self.iters/self.scale, self.shape))
        layers = layers*self.yscale
        self.iters += 1
        return layers
 
class ParticleGrowth():
    def __init__(self, shape, scale, yscale, faces_modifiers):
        self.seed = 0
        self.weibull = Weibull(shape, scale, yscale)
        self.kernel = np.ones((3,3,3))
        self.face_modifiers = faces_modifiers
        self.face_growth = copy.deepcopy(faces_modifiers)
        self.growthrate = 0

        self.stored_obj = None

    def _get_convolution(self, obj):
        mask = (obj != 0).astype(int)
        if isinstance(obj, cp.ndarray):
            surface_mask = scicp.convolve(mask, self.kernel, mode='constant')
        else:   
            surface_mask = scin.convolve(mask, self.kernel, mode='constant', cval=0)
        return surface_mask

    def grow(self, obj):
        if isinstance(obj, cp.ndarray):
            self.kernel = cp.asarray(self.kernel)
            rand_matrix = cp.random.rand(obj.shape[0],obj.shape[1],obj.shape[2])
        else:
            rand_matrix = np.random.rand(obj.shape[0],obj.shape[1],obj.shape[2])

        if self.weibull.iters == 1:
            self.stored_obj = obj

        self.growthrate = self.weibull.calclayers()
        self.obj = self.stored_obj

        for key, value in self.face_modifiers.items():
            self.face_growth[key] += (value * self.growthrate)
        
        layers_to_grow = True
        while layers_to_grow:
            layers_to_grow = False
            surface_mask = self._get_convolution(obj)
            for key, value in self.face_modifiers.items():  
                if value > 1:
                    obj[surface_mask == key] = 1
                    self.face_growth[key] -= 1
                if value > 1:
                    layers_to_grow = True
      
        self.stored_obj = obj
        surface_mask = self._get_convolution(obj)
        obj[surface_mask >= 4] = 1
        for key, value in self.face_modifiers.items():
            if (self.face_growth[key] - np.floor(self.face_growth[key])) > 0:
                obj[(self.face_growth[key]>rand_matrix) & (surface_mask == key)] = 1
            self.face_growth[key] -= np.floor(self.face_growth[key])
        return obj

