
from tomobase.core import registers, base_classes
from ...core import data_classes

class VolumeNDtController(base_classes.ImageAbstractController):
    def __init__(self, model):
        super().__init__(model)

registers.controller_pairs.register()(data_classes.VolumeNDt, VolumeNDtController)