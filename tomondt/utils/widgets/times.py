import napari
import numpy as np 
import pandas as pd

from qtpy.QtWidgets import QHBoxLayout, QVBoxLayout, QComboBox, QLabel, QWidget,QSpinBox, QFrame, QLineEdit, QPushButton, QDialog, QTableWidget, QTableWidgetItem
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QDialog

#from .table import TableWidget

class ImportTimes(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # A Drop Box of Napari Layers
        self.combobox = QComboBox()
        self.combobox.addItem('Select')
        #for layer in self._viewer.layers:
        #    self.combobox.addItem(layer.name)

        self.layout = QHBoxLayout()
        self.layout.addWidget(QLabel('From:'))
        self.layout.addWidget(self.combobox)
        self.layout.setAlignment(Qt.AlignTop)
        self.setLayout(self.layout)
        self.show()

    def get_times(self):
        layer = self.combobox.currentText()
        if layer != 'Select':
            #times = self._viewer.layers[layer].data
            pass
            #return times
        else:
            return None

class GenerateTimes(QWidget):   
    def __init__(self, parent=None):
        super().__init__(parent)

        # Spin boxes for start and end time can go upt to 1000 default to 0 and 100
        self.starttime = QSpinBox()
        self.starttime.setMaximum(1000)
        self.endtime = QSpinBox()
        self.endtime.setMaximum(1000)
        self.starttime.setValue(0)
        self.endtime.setValue(100)

        # Create the layout
        self.layout = QHBoxLayout()
        self.layout.addWidget(QLabel('Start Time (s):'))
        self.layout.addWidget(self.starttime)
        self.layout.addWidget(QLabel('End Time (s):'))
        self.layout.addWidget(self.endtime)
        self.layout.setAlignment(Qt.AlignTop)
        self.setLayout(self.layout)
        self.show()

    def get_times(self):
        start = self.starttime.value()
        end = self.endtime.value()
        times = np.linspace(start, end, end-start+1)
        return times


class TimeDialog(QDialog):
    def __init__(self, parent=None, times:np.ndarray = []):
        super().__init__(parent)
        self.times = times

        # Add a combobox with two options
        self.combobox = QComboBox()
        self.combobox.addItem('Generate Times')
        self.combobox.addItem('Get Existing Times')
        self.importWidget = ImportTimes(self)
        self.generateWidget = GenerateTimes(self)
        self.gettimesbutton = QPushButton('Get Times')
        
        # Connect the combobox to the function
        self.combobox.activated.connect(self.show_widget)
        self.gettimesbutton.clicked.connect(self.get_times)
        self.table = TableWidget(self, ['Time (s)'])


        # Create the layout
        self.layout = QVBoxLayout()

        # Add the table to the layout
        self.layout.addWidget(self.combobox)
        self.layout.addWidget(self.importWidget)
        self.layout.addWidget(self.generateWidget)
        self.layout.addWidget(self.gettimesbutton)
        self.layout.addWidget(self.table)

        self.setLayout(self.layout)
        self.show()
        self.importWidget.hide()
        
    def get_data(self):
        return self.table.df

    def get_times(self):
        if self.combobox.currentText() == 'Generate Times':
            self.times =  self.generateWidget.get_times()
        else:
            self.times =  self.importWidget.get_times()
        # create a pandas dataframe with the times
        self.table.df = pd.DataFrame(self.times, columns = ['Time (s)'])
        self.table.update_table(self.table.df)
        
    def show_widget(self):
        if self.combobox.currentText() == 'Generate Times':
            self.importWidget.hide()
            self.generateWidget.show()
        else:
            self.importWidget.show()
            self.generateWidget.hide()

class TimeWidget(QWidget):
    def __init__(self, viewer: 'napari.viewer.Viewer', parent=None):
        super().__init__(parent)
        self._viewer = viewer

        # A line to enter the file name
        self.Label = QLabel('Times:')
        self.TimeButton = QPushButton(icon = QIcon('D:\\Tim\\tomo3dt\\tomondt\\assets\icons\\simulate.svg'))

        # Connect Browse Button to file Save dialog
        self.TimeButton.clicked.connect(self.open_dialog)

        self.layout = QHBoxLayout()
        self.layout.addWidget(self.Label)
        self.layout.addWidget(self.TimeButton)
        self.layout.setAlignment(Qt.AlignTop)
        self.setLayout(self.layout)
        self.show()

    def open_dialog(self):
        # We will need to add the layer data to the dialog later
        dialog = TimeDialog()
        dialog.exec_()
        data = dialog.get_data()
        return data
    



