import os
import coolname
import numpy as np
from typing import Callable
from magicgui.tqdm import tqdm

from tomobase.data import Volume, Sinogram
from tomobase.processes import project

from .data import VolumeNDt

    
def segment_ndt(vndt : VolumeNDt, algor: Callable, **kwargs):
    """Segment a VolumeNDt object. In the case of the NDt library every process where a volume is converted to another volume is treated as a segmentation. 

    Args:
        vndt (VolumeNDt): The input VolumeNDt object to be segmented.
        algor (Callable): The algorithm to be applied for segmentation.

    Returns:
        VolumeNDt: The segmented VolumeNDt object.
    """

    #TODO setup a temp directory
    segmented_vndt = kwargs.pop('saveas', coolname.generate_slug(2) + '.vmf')
    replace = kwargs.pop('replace', False)

    #TODO check new struct for vmf
    segmenter = lambda x: algor(x, **kwargs)
    for i in tqdm(range(len(vndt.times)), desc="Segmenting NDt"):
        obj = segmenter(vndt.read_record(vndt.times[i]))
        segmented_vndt.write_record(obj, vndt.times[i], vndt.metadata['start_time'][i], vndt.metadata['end_time'][i])
    
    #replace vndt file with segmented_vndt
    if replace:
        os.remove(vndt.dir)
        os.rename(segmented_vndt.dir, vndt.dir)
    return segmented_vndt


def deform_ndt(vol: Volume, times:np.ndarray, algor: Callable, **kwargs):
    """Deform a Volume object over specified time points using a given algorithm.

    Args:
        vol (Volume): The input Volume object to be deformed.
        times (np.ndarray): The time points at which to apply the deformation.
        algor (Callable): The algorithm to be applied for deformation.
        **kwargs: Additional keyword arguments to be passed to the algorithm.

    Returns:
        VolumeNDt: The deformed Volume object.
    """

    deformed_vndt = kwargs.pop('saveas', coolname.generate_slug(2) + '.vmf')
    #TODO check new struct for vmf

    deformer = lambda x: algor(x, **kwargs)
    for i in tqdm(range(len(times)), desc="Deforming Volume"):
        obj = deformer(vol.read_record(times[i]))
        deformed_vndt.write_record(obj, times[i], vol.metadata['start_time'][i], vol.metadata['end_time'][i])
    return deformed_vndt

def project_ndt(vndt: VolumeNDt, angles: np.ndarray, times:np.ndarray|None=None):
    """Project a VolumeNDt object over specified angles and time points.

    Args:
        vmf (VolumeNDt): The input VolumeNDt object to be projected.
        angles (np.ndarray): The angles at which to project the volume.
        times (np.ndarray|None, optional): The time points at which to apply the projection. Defaults to None.

    Returns:
        Sinogram: a sinogram
    """
    sino = Sinogram.empty([len(angles), vndt.shape[0], vndt.shape[1]], vndt.pixelsize)

    # if no times are specified assume the time is the same as each volume
    # Note: zero time is reserved for ground truth data and is not used for projection
    if times is None:
        times = vndt.times[vndt.times != 0]
        if len(times) != len(angles):
            raise Exception("times and angles array must be the same size - when unspecified the number of volume must be the same as the number of angles")
        for i in tqdm(range(len(times)), desc="Projecting Tilt Series"):
            obj = vndt.read_record(times[i])
            sino_temp = project(obj, angles[i])
            sino.fill(sino_temp)

    else:
        # amalgams is a metadata used for calculating motion blurring error
        sino.metadata['amalgams'] = []
        if len(times) != len(angles):
            raise Exception("times and angles array must be the same size")
        
        for i in tqdm(range(len(angles)), desc="Projecting Tilt Series"):
            # Reconstruct every volume where the time is between the start and end time
            counts = []
            for j in range(len(vndt.times)):
                counts.append(0)
                if vndt.metadata['start_time'][j]<=times[i]<=vndt.metadata['end_time'][j]:
                    counts[j] += 1
            amalgam_sino = Sinogram.empty([sum(counts), vndt.shape[0], vndt.shape[1]], vndt.pixelsize)
            for j in range(len(vndt.times)):
                if counts[j] > 0:
                    obj = vndt.read_record(vndt.times[j])
                    sino_temp = project(obj, angles[i])
                    sino.fill(sino_temp)
    
    return sino


