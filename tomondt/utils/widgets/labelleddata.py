import napari
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel,QSizePolicy,  QComboBox, QPushButton, QGridLayout, QTableWidget, QTableWidgetItem
from PyQt5.QtCore import Qt

class LabelledDataWidget(QWidget):
    def __init__(self, viewer: 'napari.viewer.Viewer', name='default', value='default', parent=None):
        super().__init__(parent)
        self._viewer = viewer
        self.layout = QHBoxLayout()
        
        self.labelwidget = QLabel(name)
        self.valuewidget = QLabel(value)
        
        self.layout.addWidget(self.labelwidget)
        self.layout.addWidget(self.valuewidget)
        
        self.layout.setAlignment(Qt.AlignTop)
        self.setLayout(self.layout)
        self.show()