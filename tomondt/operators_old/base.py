from ..structs.base import DataNDt
from ..utils.utils import DeviceContextEnum


class NDtOperator(DataNDt):
    def __init__(self, **kwargs):
        super().__init__()
        self.setcontext(kwargs.get('context',DeviceContextEnum.NUMPY), kwargs.get('device',0))

    def __call__(self, **kwargs):
        self._setcontext(kwargs.get('context',DeviceContextEnum.NUMPY), kwargs.get('device',0))