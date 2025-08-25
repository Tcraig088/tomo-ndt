import napari

from qtpy.QtWidgets import QWidget, QHBoxLayout, QComboBox, QLabel , QVBoxLayout , QPushButton

from tomondt.utils.widgets import GroupBoxWidget, LayersWidget, TimeWidget

class BackProjectWidget(QWidget):
    def __init__(self, viewer: 'napari.viewer.Viewer', parent=None):
        super().__init__(parent)
        self._viewer = viewer
        
        self.layout = QVBoxLayout()
        
        self.layersWidget = LayersWidget(self._viewer, 'Volume')
        self.pluginWidget = PluginFunctionWidget(self._viewer, plugin_key = 'Algorithms')
        self.runbutton = QPushButton('Run Task')
        
        self.layout.addWidget(self.layersWidget)
        self.layout.addWidget(self.pluginWidget)
        self.layout.addWidget(self.runbutton)
        
        self.setLayout(self.layout)
        self.show()

class ForwardProjectWidget(QWidget):
    def __init__(self, viewer: 'napari.viewer.Viewer', parent=None):
        super().__init__(parent)
        self._viewer = viewer
        
        self.layout = QVBoxLayout()
        
        self.layersWidget = LayersWidget(self._viewer, 'VolumeNDT')
        self.timesWidget = TimeWidget(self._viewer)
        self.runbutton = QPushButton('Run Task')
        
        self.layout.addWidget(self.layersWidget)
        self.layout.addWidget(self.timesWidget)
        self.layout.addWidget(self.runbutton)
        
        self.setLayout(self.layout)
        self.show()

class ProjectionTypeWidget(QWidget):
    def __init__(self, viewer: 'napari.viewer.Viewer', parent=None):
        super().__init__(parent)
        self._viewer = viewer
        
        self.layout = QHBoxLayout()
        self.label = QLabel('Type:')
        self.comboBox = QComboBox()
        self.comboBox.addItem('Select')
        self.comboBox.addItem('Forward')
        self.comboBox.addItem('Backward')
        
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.comboBox)

        self.setLayout(self.layout)
        self.show()
        
        
class ProjectionWidget(QWidget):
    def __init__(self, viewer: 'napari.viewer.Viewer', parent=None):
        super().__init__(parent)
        self._viewer = viewer

        self.layout = QVBoxLayout()
        
        self.projectionTypeWidget = ProjectionTypeWidget(self._viewer)
        self.widget = QWidget()
        
        self.layout.addWidget(self.projectionTypeWidget)
        self.layout.addWidget(self.widget)
        
        self.projectionTypeWidget.comboBox.currentTextChanged.connect(self.update_widget)
        
        self.setLayout(self.layout)
        self.show()
        
    def update_widget(self):
        self.layout.removeWidget(self.widget) 
        self.widget.hide() 
        self.widget.deleteLater()  

        if self.projectionTypeWidget.comboBox.currentText() == 'Forward':
            self.widget = ForwardProjectWidget(self._viewer)
            self.layout.addWidget(self.widget)
        else:
            self.layout.removeWidget(self.widget)
            self.widget = BackProjectWidget(self._viewer)
            self.layout.addWidget(self.widget)
        self.show()