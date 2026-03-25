#import tomosipo as tp
import os 
import numpy as np

from ...structs import DataNDt
from ...utils import utils

def forwardproject(vol, ang):
    context  = DataNDt().setfromarray(vol)
    ang = np.radians(ang+90)          
    s, d = vol.shape[0], 0
    if len(vol.shape) == 2:
        d = 1
        vol = vol[None, :,:]
    elif len(vol.shape) == 3:
        vol = vol
        d = vol.shape[1]
    else:
        raise Exception("The Volume must be a two or 3D array")
    vol = utils.permute(vol,(1,0,2))
    pg = tp.parallel(angles = ang, shape = (d,s), size = (1,1))
    vg = tp.volume(shape = (d,s,s), size = (1,1,1))

    A = tp.operator(vg,pg)
    vol = A(vol)
    vol = utils.permute(vol,(2,0,1)).squeeze()
    return vol