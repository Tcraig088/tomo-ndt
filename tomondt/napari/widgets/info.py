import napari
import numpy as np

from qtpy.QtWidgets import QWidget, QRadioButton,  QVBoxLayout, QHBoxLayout, QLabel,QSizePolicy, QTableWidget, QTableWidgetItem
from qtpy.QtCore import Qt

from tomondt.utils.widgets import GroupBoxWidget, LabelledDataWidget
from tomondt.napari.data_types import NDt_Types


class SizeTableWidget(QWidget):
    def __init__(self, viewer: 'napari.viewer.Viewer', parent=None):
        super().__init__(parent)
        self._viewer = viewer
        self.selection = self._viewer.layers.selection.active
        self.table = QTableWidget(1, len(self.selection.data.shape))
        
        if 'NDt Type' in self.selection.metadata:
            self.table.setHorizontalHeaderLabels(self.selection.metadata['NDt Dim Labels'])
              
        for i in range(len(self.selection.data.shape)):
            item = QTableWidgetItem(str(self.selection.data.shape[i]))
            item.setFlags(item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(0, i, item)
            
        self.table.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)   
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.table)
        
        self.layout.setAlignment(Qt.AlignTop)
        self.setLayout(self.layout)
        self.show() 
            
class SortOptionWidget(QWidget):
    def __init__(self, viewer: 'napari.viewer.Viewer', parent=None):
        super().__init__(parent)
        self._viewer = viewer
        self.layout = QHBoxLayout()
        
        self.label = QLabel('Sort By:')
        self.rbtn1 = QRadioButton('Time', self)
        self.rbtn2 = QRadioButton('Angle', self)
        
        self.rbtn1.toggled.connect(self.get_sort_option)
        self.rbtn2.toggled.connect(self.get_sort_option)
        self.rbtn1.setChecked(True)
        
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.rbtn1)
        self.layout.addWidget(self.rbtn2)
        
        self.layout.setAlignment(Qt.AlignTop)
        self.setLayout(self.layout)
        self.show()
        
    def get_sort_option(self):
        selected = self._viewer.layers.selection.active
        if self.rbtn1.isChecked():
            sorted_indices = selected.metadata['NDt Times'].argsort()
        else:
            sorted_indices = selected.metadata['NDt Angles'].argsort()
        selected.metadata['NDt Times'] = selected.metadata['NDt Times'][sorted_indices]
        selected.metadata['NDt Angles'] = selected.metadata['NDt Angles'][sorted_indices]
        dim = len(selected.data.shape)
        if dim == 3:
            selected.data = selected.data[:,:,sorted_indices]
        else:
            selected.data = selected.data[:,:,:,sorted_indices]
        selected.refresh()
           
        
class TiltSeriesInfoWidget(QWidget):
    def __init__(self, viewer: 'napari.viewer.Viewer', parent=None):
        super().__init__(parent)
        
        self._viewer = viewer
        self.selected = self._viewer.layers.selection.active
        self.dims = len(self.selected.data.shape)

        self.layout = QVBoxLayout()
        self.sortwidget = SortOptionWidget(self._viewer)

        self._viewer.dims.events.ndisplay.connect(self.update_dims)
        self._viewer.dims.events.order.connect(self.update_dims)
        self._viewer.dims.events.current_step.connect(self.update_dims)
        self.sortwidget.rbtn1.toggled.connect(self.update_dims)
        self.sortwidget.rbtn2.toggled.connect(self.update_dims)
        
        self.layout.addWidget(self.sortwidget)
        self.layout.setAlignment(Qt.AlignTop)
        self.setLayout(self.layout)
        self.show()
     
        self.update_dims()
        
    def update_dims(self):
        if hasattr(self, 'labelswidget'):
            for i in range(len(self.labelswidget)):
                self.layout.removeWidget(self.labelswidget[i])
                self.labelswidget[i].hide()
            
        if self.dims > self._viewer.dims.ndisplay:
            label_dict =  {}
            for i in range(self.dims - self._viewer.dims.ndisplay):
                dim_index = self._viewer.dims.order[i]
                label = self.selected.metadata['NDt Dim Labels'][dim_index]
                val_index = self._viewer.dims.current_step[dim_index]
                if label == 'Projections':
                    times = self.selected.metadata['NDt Times'][val_index]
                    #covert time in seconds to a string hh:mm:ss:ms
                    hours, remainder = divmod(times, 3600)
                    minutes, seconds = divmod(remainder, 60)
                    milliseconds = (seconds % 1) * 1000
                    times =  f"{int(hours)} h: {int(minutes)} m: {int(seconds)} s: {int(milliseconds)} ms"

                    label_dict['Time (s):']= times
                    label_dict['Angle (deg):']= np.round(self.selected.metadata['NDt Angles'][val_index],2)
                elif label == 'Signals':
                    if 'NDt Signal Labels' in self.selected.metadata:
                        label_dict['Signal:'] = self.selected.metadata['Signal Labels'][val_index]
                    else:
                        label_dict['Signal:'] = val_index
                else:
                    label_dict[label] = val_index
                     
            self.labelswidget = [] 
            i = 0   
            for key, value in label_dict.items():
                self.labelswidget.append(LabelledDataWidget(self._viewer, key, str(value)))
                
                self.layout.addWidget(self.labelswidget[i])
                i+=1
                
            self.layout.setAlignment(Qt.AlignTop)
            self.show()


class LayerInfoWidget(GroupBoxWidget):
    def __init__(self, viewer: 'napari.viewer.Viewer', parent=None):
        super().__init__(parent, title ='Layer Info')
        
        self._viewer = viewer
        self.layout = QVBoxLayout()
        
        self.datawidget = LabelledDataWidget(self._viewer, 'Dataset:', 'No Selected Layer')
        self.datatypewidget = LabelledDataWidget(self._viewer, 'Data Type:', 'No NDT Type')
        
        self._viewer.layers.selection.events.changed.connect(self.update_info)
        
        self.layout.addWidget(self.datawidget)
        self.layout.addWidget(self.datatypewidget)

        self.layout.setAlignment(Qt.AlignTop)
        self.setLayout(self.layout)
        self.update_info()
     
    def update_info(self):
        # Get the selected napari layer name and change the label
        selected = self._viewer.layers.selection.active
        if hasattr(self, 'widget'):
            self.layout.removeWidget(self.widget)
            self.widget.hide()
            
        if hasattr(self, 'table'):
            self.layout.removeWidget(self.table)
            self.table.hide()
              
        if selected is not None:
            self.show()
            self.datawidget.valuewidget.setText(selected.name)
            if 'NDt Type' in selected.metadata:
                print(selected.metadata['NDt Type'])
                self.datatypewidget.valuewidget.setText(selected.metadata['NDt Type'])
                match selected.metadata['NDt Type']:
                    case NDt_Types.Volume.value:
                        self.widget = QWidget()
                    case NDt_Types.TiltSeriesNDt.value:
                        self.widget = TiltSeriesInfoWidget(self._viewer)

                self.table= SizeTableWidget(self._viewer)      
                self.layout.addWidget(self.widget)
                self.layout.addWidget(self.table)
                self.layout.setAlignment(Qt.AlignTop)
                self.show()
            else:
                self.datatypewidget.valuewidget.setText('Data Type Not Supported')
        else:
            self.hide()

