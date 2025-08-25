import napari

from qtpy.QtWidgets import QButtonGroup, QPushButton, QHBoxLayout

from tomondt.utils.widgets import GroupBoxWidget
from ..data_types import NDt_Types, NDt_Operations, _checklayertype

from .current_operation import CurrentOperationWidget

class SelectOperationWidget(GroupBoxWidget):
    def __init__(self, viewer: 'napari.viewer.Viewer', parent=None):
        super().__init__(parent, title ='Tasks')
        self._viewer = viewer
        self.selection = self._viewer.layers.selection.active
        
        self.layout = QHBoxLayout()
        
        self._viewer.layers.selection.events.changed.connect(self.update)

        self.update()

        self.setLayout(self.layout)
        self.show()

    def update(self):
        self.selection = self._viewer.layers.selection.active
        ndttype = _checklayertype(self.selection)
        if hasattr(self, 'buttons'):
            self.buttons.deleteLater()
            for button in self.buttons_list:
                button.hide()
                self.layout.removeWidget(button)
                button.deleteLater()
                
        self.buttons = QButtonGroup()
             
        match ndttype:
            case NDt_Types.VolumeSeriesNDt.value:
                self.buttons_list = [QPushButton('Reconstruct'), QPushButton('Segment'), QPushButton('Quantify')] 
                ids = [NDt_Operations.Reconstruct, NDt_Operations.Segment, NDt_Operations.Quantify]
            case NDt_Types.TiltSeriesNDt.value:
                self.buttons_list = [QPushButton('Align'), QPushButton('Project'), QPushButton('Quantify')]
                ids = [NDt_Operations.Align, NDt_Operations.Project, NDt_Operations.Quantify]
            case NDt_Types.Volume.value:
                self.buttons_list = [QPushButton('Simulate')]
                ids = [NDt_Operations.Simulate]
            case _:
                self.hide()
                return
            
        self.show()
        for i, button in enumerate(self.buttons_list):
            self.buttons.addButton(button, id=ids[i])
            self.layout.addWidget(button)
        
    def get_operation(self, id):
        ndttype = _checklayertype(self.selection)
        if ndttype is not None:
            widget = CurrentOperationWidget(self._viewer)
            match id:
                case NDt_Operations.Reconstruct:
                    return None
                case NDt_Operations.Segment:
                    return None
                case NDt_Operations.Quantify:
                    return None
                case NDt_Operations.Align:
                    print('Align')
                    widget.group_box.setTitle('Align Tilt Series NDt')
                    widget.setWidget('Align')
                    return widget
                case NDt_Operations.Project:
                    widget.group_box.setTitle('Project Tilt Series NDt')
                    widget.setWidget('Project')
                    return widget
                case NDt_Operations.Segment:
                    return None
                case NDt_Operations.Simulate:
                    return None
                case _:
                    return None
        else:
            return None    