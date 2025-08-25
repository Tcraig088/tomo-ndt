from typing import Union
import numpy as np
import cupy as cp
import torch

GenericArray = Union[np.ndarray, cp.ndarray, torch.Tensor]
