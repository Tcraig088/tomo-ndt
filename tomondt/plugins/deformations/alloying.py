import skimage
import copy
import numpy as np

from ...utils.context import device_context
if device_context.availability.cupy:
    import cupy as cp
    from cupyx.scipy import ndimage as scicp

class Alloying():
    def __init__(self, obj, density, threshold,  sig, noise):
        # Density Equation
        # Each voxel contains material A or B and has an intensity Coefficient B is less intense than A
        # I(B=0)=1 
        # I = IA(A)*IB(B)
        # D =  A + B
        # By this logic IB is the minimum intensity
        self.threshold = threshold
        self.density =  density
        self.spread = sig
        self.intensityA = 1/self.density
        self.intensityB = threshold/self.density
        self.m1=obj
        self.m1[self.m1>=self.threshold] = 0
        self.m1[self.m1<self.threshold] = 1*self.density
        self.noise =noise

    def run(self, obj):
        #new = scicp.gaussian_filter(obj, self.spread)
        #kernel = cp.ones((self.spread,self.spread,self.spread))
        # generate random kernel
        
        mask = cp.zeros(obj.shape)
        mask[obj>0] = 1
        #3D convolution
        new = scicp.gaussian_filter(obj, self.spread)
        mask = scicp.gaussian_filter(mask, self.spread)
        #mask = scicp.convolve(mask, kernel, mode='constant')/(self.spread**3)
        #new = scicp.convolve(obj, kernel, mode='constant')
        #new[obj==0] = 0
        #new = new/mask    
        new[obj>0] = new[obj>0]/mask[obj>0]
        new[obj==0] = 0
        for i in range(self.noise):
            kernel = cp.random.rand(3,3,3)
            kernel = kernel/cp.sum(kernel)
            new = scicp.convolve(new, kernel, mode='constant')
            #mask = scicp.convolve(mask, kernel, mode='constant')
            #new[obj>0] = new[obj>0]*mask[obj>0]
            new[obj==0] = 0
        return new
