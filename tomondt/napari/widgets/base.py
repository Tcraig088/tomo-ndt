import napari
import logging

from qtpy.QtWidgets import  QVBoxLayout, QWidget

from .select_operation import SelectOperationWidget
from .context import ContextWidget
from .info import LayerInfoWidget
from ..data_types import NDt_Types, _checklayertype
from tomondt.utils.widgets import _deletewidget
from tomondt.utils.output import progressbar


class BaseWidget(QWidget):
    def __init__(self, viewer: 'napari.viewer.Viewer', parent=None):
        super().__init__(parent)
        progressbar.isnapari = True
        self._viewer = viewer
        logging.basicConfig(level=logging.INFO)
        logging.info('Test Log')
        self._viewer.layers.selection.events.changed.connect(self.selection_changed)
        self.selection = self._viewer.layers.selection.active

        self.contextWidget = ContextWidget(viewer)
        
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.contextWidget)
  
        # Connect up the menu2 widget to an event
        self.setLayout(self.layout)
        self.show()

        self.selection_changed()
        

    def selection_changed(self):
        self.selection = self._viewer.layers.selection.active   
          
        ndttype = _checklayertype(self.selection) 
        print('call', ndttype) 

        _deletewidget(self, 'infoWidget')
        _deletewidget(self, 'soperationWidget')
        _deletewidget(self, 'coperationWidget')
        if ndttype is None:
            return
        
        logging.info('Test Log')    
        self.infoWidget = LayerInfoWidget(self._viewer)
        self.infoWidget.group_box.setChecked(True)

        self.soperationWidget = SelectOperationWidget(self._viewer)
        self.soperationWidget.group_box.setChecked(True)

        
        self.soperationWidget.buttons.buttonClicked.connect(self.operator_changed)
        
        self.layout.addWidget(self.infoWidget)
        self.layout.addWidget(self.soperationWidget)
        self.show()
        self.update()
        
    def operator_changed(self, button):
        id = self.soperationWidget.buttons.id(button)
        if hasattr(self, 'coperationWidget'):
            self.coperationWidget.hide()    
            self.layout.removeWidget(self.coperationWidget)
            self.coperationWidget.deleteLater()

        coperationWidget = self.soperationWidget.get_operation(id=id)
        if coperationWidget is not None:
            self.coperationWidget = coperationWidget
            self.layout.addWidget(self.coperationWidget)
            self.coperationWidget.show()
            self.update()


