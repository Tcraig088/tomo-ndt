from qtpy.QtWidgets import QHBoxLayout, QGridLayout, QVBoxLayout, QComboBox, QLabel, QWidget,QSpinBox, QFrame, QLineEdit, QPushButton, QDialog, QTableWidget, QTableWidgetItem
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QDialog

#from tomondt.hooks import hooks_manager


class PhantomDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.select = QComboBox()
        self.select.addItem('Select')
        for key in hooks_manager.plugins['phantom'].keys():
            self.select.addItem(key)
        self.widget = QWidget()
        self.button = QPushButton('Generate Volume')
        
        self.layout = QGridLayout()
        self.layout.addWidget(QLabel('Phantoms'),0,0)
        self.layout.addWidget(self.select,0,1)
        self.layout.addWidget(self.widget,1,0,1,2)
        self.layout.addWidget(self.button,2,0,1,2)
        # Connect the currentIndexChanged signal to the update_widget method
        self.select.currentIndexChanged.connect(self.update_widget)
        self.button.clicked.connect(self.get_volume)

        self.layout.setAlignment(Qt.AlignTop)   
        self.setLayout(self.layout)
        self.show()
        
    def update_widget(self):
        # Get the current selection
        key = self.select.currentText()

        # If the key is 'Select', don't show any widget
        if key == 'Select':
            if self.widget is not None:
                self.widget.hide()
            return

        # Remove the old widget from the layout
        if self.widget is not None:
            self.layout.removeWidget(self.widget)
            self.widget.deleteLater()

        # Create the new widget and add it to the layout
        self.widget = hooks_manager.plugins['phantom'][key]()
        self.layout.addWidget(self.widget, 1, 0, 1, 2)
        
        
    def get_volume(self):
        key = self.select.currentText()
        self.volume = self.widget.get_volume()
        self.close()
        