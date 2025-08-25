import napari

from qtpy.QtWidgets import QVBoxLayout, QPushButton

from tomondt.utils.widgets import FileSaveWidget, TimeWidget, LayersWidget
from tomondt.napari.data_types import NDt_Types, convert_layer_to_type
from tomondt.napari.plugin_register import plugin_manager

from .plugins import PluginFunctionWidget

class AlignWidget(PluginFunctionWidget):
    def __init__(self, viewer: 'napari.viewer.Viewer', parent=None):
        super().__init__(viewer, parent, plugin_key='Alignments')
        self._viewer = viewer
        self.selection = self._viewer.layers.selection.active
        # Create the layout
        self.layout = QVBoxLayout()
        
        self.alignmentwidget = PluginFunctionWidget(self._viewer, plugin_key = 'Alignments')
        
        self.runbutton = QPushButton('Run Task')
        
        self.tiltseriesWidget.comboBox.currentTextChanged.connect(self.set_layer)
        self.runbutton.clicked.connect(self.run_task)
        
        self.layout.addWidget(self.tiltseriesWidget)
        self.layout.addWidget(self.alignmentwidget)
        self.layout.addWidget(self.runbutton)

        self.setLayout(self.layout)
        self.show()

    def set_layer(self):
        if self.tiltseriesWidget.comboBox.currentText() == 'Select':
            self.layer = None
        else:
            index = self.tiltseriesWidget.dict[self.tiltseriesWidget.comboBox.currentText()]
            self.alignmentwidget.layer = self._viewer.layers[index]
            self.alignmentwidget.layer = convert_layer_to_type(self.alignmentwidget.layer)
            
    def run_task(self):
        index = self.tiltseriesWidget.dict[self.tiltseriesWidget.comboBox.currentText()]
        layer = self._viewer.layers[index]
        #find layer with the name in the combobox
        ts = convert_layer_to_type(layer)
        
        func = self.alignmentwidget.get_function()
        ts = NDT_Align().run(ts, func)
        self._viewer.layers[index].data = ts.data
        
