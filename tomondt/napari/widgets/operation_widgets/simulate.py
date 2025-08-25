import napari

from qtpy.QtWidgets import QHBoxLayout, QVBoxLayout, QComboBox, QLabel, QWidget, QFrame, QGridLayout, QPushButton, QSpinBox, QDialog
from PyQt5.QtCore import Qt

from tomondt.utils.widgets import FileSaveWidget, TimeWidget
from tomondt.napari.plugin_register import plugin_manager
from .plugins import PluginFunctionWidget



class VolumeWidget(QWidget):
    def __init__(self, viewer: 'napari.viewer.Viewer', parent=None):
        super().__init__(parent)
        self._viewer = viewer
        
        # Create the layout
        self.layout = QHBoxLayout()

        # Create the first combo box
        self.comboBox1 = QComboBox()    
        self.comboBox1.addItem('Select')
        for layer in self._viewer.layers:
            #check if layer has a NDTType metadata  
            if 'NDTType' in layer.metadata:
                if layer.metadata['NDTType'] == 'Volume':
                    self.comboBox1.addItem(layer.name)
                    
        self.volume_button = QPushButton('New Volume')
        
        self.volume_button.clicked.connect(self.open_dialog)
        self._viewer.layers.events.inserted.connect(self.reset_combobox)
        self._viewer.layers.events.removed.connect(self.reset_combobox)
        self._viewer.layers.selection.events.changed.connect(self.reset_combobox)
        
        self.layout.addWidget(QLabel("Volume:"))
        self.layout.addWidget(self.comboBox1)
        self.layout.addWidget(self.volume_button)

        self.layout.setAlignment(Qt.AlignTop)
        self.setLayout(self.layout)
        self.show()

    def open_dialog(self):
        # We will need to add the layer data to the dialog later
        dialog = PhantomDialog()
        dialog.exec_()
        data = dialog.volume
        self._viewer.add_image(data, metadata ={'NDTType':'Volume'})
        return data
    
    def reset_combobox(self):
        self.comboBox1.clear()
        self.comboBox1.addItem('Select')
        for layer in self._viewer.layers:
            #check if layer has a NDTType metadata  
            if 'NDTType' in layer.metadata:
                if layer.metadata['NDTType'] == 'Volume':
                    self.comboBox1.addItem(layer.name)
    
class SimulateWidget(QWidget):
    def __init__(self, viewer: 'napari.viewer.Viewer', parent=None):
        super().__init__(parent)
        self._viewer = viewer

        # Create the layout
        self.layout = QVBoxLayout()
        
        self.volumeWidget = VolumeWidget(self._viewer)
        self.filesaveWidget = FileSaveWidget(self._viewer)
        self.timesWidget = TimeWidget(self._viewer)
        self.deformation = PluginFunctionWidget(self._viewer, plugin_key = 'Deformation')
        
        self.runbutton = QPushButton('Run Task')
        
        self.runbutton.clicked.connect(self.run_task)
        self.layout.addWidget(self.volumeWidget)
        self.layout.addWidget(self.filesaveWidget)
        self.layout.addWidget(self.timesWidget)
        self.layout.addWidget(self.deformation)
        self.layout.addWidget(self.runbutton)
    
        self.layout.setAlignment(Qt.AlignTop)
        self.setLayout(self.layout)
        self.show()

        
        
    def run_task(self):
        NDT_Deform.run(self.filesaveWidget.LineEntry.value(), self.timesWidget.times, algor = None)
