import napari

from qtpy.QtWidgets import QWidget, QHBoxLayout, QComboBox, QLabel
from PyQt5.QtCore import Qt

from tomondt.napari.data_types import NDt_Types

class LayersWidget(QWidget):
    def __init__(self, viewer: 'napari.viewer.Viewer', ndttype, parent=None):
        super().__init__(parent)
        self._viewer = viewer
        self.ndttype = ndttype
        self.dict = {}
        self.layout = QHBoxLayout()
        # Create the first combo box
        self.comboBox = QComboBox()  
          
        self.comboBox.addItem('Select')
        # get index and date on loop
        for index, layer in enumerate(self._viewer.layers):
            #check if layer has a NDTType metadata  
            if 'NDt Type' in layer.metadata:
                if layer.metadata['NDt Type'] == ndttype:
                    self.comboBox.addItem(layer.name)
                    self.dict[layer.name] = index
        print(self.dict)
        
        self._viewer.layers.events.inserted.connect(self.reset_combobox)
        self._viewer.layers.events.removed.connect(self.reset_combobox)
        self._viewer.layers.selection.events.changed.connect(self.reset_combobox)
        
        name = ''
        match ndttype:
            case NDt_Types.TiltSeriesNDt.value:
                name = 'TiltSeries'
            case NDt_Types.VolumeSeriesNDt.value:
                name = 'Volume'
            case _:
                name = ndttype
                
        self.layout.addWidget(QLabel(name))
        self.layout.addWidget(self.comboBox)
        
        self.layout.setAlignment(Qt.AlignTop)
        self.setLayout(self.layout)
        self.show()
        
    def reset_combobox(self):
        self.comboBox.clear()
        self.dict = {}
        self.comboBox.addItem('Select')
        for index, layer in enumerate(self._viewer.layers):
            #check if layer has a NDTType metadata  
            if 'NDt Type' in layer.metadata:
                if layer.metadata['NDt Type'] == self.ndttype:
                    self.comboBox.addItem(layer.name)
                    self.dict[layer.name] = index
        print(self.dict)        

