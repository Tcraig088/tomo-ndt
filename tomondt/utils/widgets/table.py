from qtpy.QtWidgets import QHBoxLayout,QCheckBox, QVBoxLayout, QComboBox, QLabel, QWidget,QDoubleSpinBox, QSpinBox, QFrame, QLineEdit, QPushButton, QDialog, QTableWidget, QTableWidgetItem
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QDialog

import numpy as np
import pandas as pd

class TableWidget(QWidget):
    def __init__(self, parent=None, labels=None, readonly=False, selectable=False):
        super().__init__(parent)
        # make empty pandas array with columes index and labels
        self.columns = labels
        
        self.selectable = selectable
        self.readonly = readonly
        
        self.setup_table()

        self.layout = QVBoxLayout()
        if hasattr(self, 'addbutton'):
            self.layout.addWidget(self.addbutton)
        self.layout.addWidget(self.table)

        self.layout.setAlignment(Qt.AlignTop)
        self.setLayout(self.layout)
        self.show()
    
    def set_selection(self, setall):
        if self.selectable == True:
            for i in range(self.table.rowCount()):
                item = self.table.cellWidget(i, self.table.columnCount()-1)
                item.setChecked(setall)
                
                
    def setup_table(self):
        self.ncolumns = len(self.columns)
        self.offset = 0
        if self.selectable == True:
            self.ncolumns += 1
            self.columns.append('Select')
            columns  = self.columns
        if self.readonly == False:
            self.ncolumns += 1
            self.offset = 1
            columns = ['Delete']  + self.columns
            self.add_button = QPushButton('Add') 
            self.addbutton.clicked.connect(self.add_row)
        
        self.df = pd.DataFrame(columns=self.columns)    
        self.table = QTableWidget(0, self.ncolumns)
        self.table.setHorizontalHeaderLabels(columns)
        
    def add_row(self):
        row = [0] * len(self.columns)
        self.df.loc[len(self.df.index)] = row
        self.table.setRowCount(self.table.rowCount() + 1)

        button = QPushButton('Delete')
        button.clicked.connect(lambda checked, row=self.table.rowCount()-1: self.delete_row(row))
        self.table.setCellWidget(self.table.rowCount()-1, 0, button)
        self.table.setItem(self.table.rowCount()-1, 1, QTableWidgetItem(str(self.table.rowCount()-1)))
        for i in range(len(self.columns)):
            value = self.df[self.columns[i]].iloc[-1]
            if self.columns[i] == 'Select':
                checkBox = QCheckBox()
                checkBox.setChecked(value)
                self.table.setCellWidget(self.table.rowCount()-1, i+self.offset, checkBox)
            else:
                spinBox = QDoubleSpinBox()
                spinBox.setRange(-100000, 100000)
                spinBox.setValue(value)
                if self.readonly:
                    spinBox.setReadOnly(True)
                self.table.setCellWidget(self.table.rowCount()-1, i+self.offset, spinBox)

    def update_table(self, df): 
        self.table.setRowCount(0)
        self.df = df

        self.table.setRowCount(len(df))
        for i in range(len(df)):
            if self.readonly == False:
                button = QPushButton('Delete')
                button.clicked.connect(lambda checked, row=i: self.delete_row(row))
                self.table.setCellWidget(i, 0, button)
            self.table.setItem(i, 1, QTableWidgetItem(str(i)))
            for j in range(len(self.columns)):
                value = self.df[self.columns[j]].iloc[i]
                if self.columns[j] == 'Select':
                    widget = QCheckBox()
                    widget.setChecked(value)
                else:
                    widget = QDoubleSpinBox()
                    widget.setRange(-100000, 100000)
                    widget.setValue(value)
                    if self.readonly:
                        widget.setReadOnly(True)
                self.table.setCellWidget(i, j+self.offset, widget)


    def confirm_data(self):
        #set self.df to the data from the table
        df = pd.DataFrame(columns=self.columns)

        
        for i in range(self.table.rowCount()):
            row = []
            for j in range(self.offset, self.table.columnCount()):  
                item = self.table.cellWidget(i, j)
                if self.columns[j] == 'Select':
                    checkbox = item
                    row.append(checkbox.isChecked())
                else:
                    row.append(item.value())
            df.loc[i] = row
        self.df = df
        return self.df
    
    def delete_row(self, row):
        # If you also want to delete the row from the dataframe
        self.confirm_data()
        self.df = self.df.drop(self.df.index[row])
        self.df = self.df.reset_index(drop=True)
        self.update_table(self.df)

