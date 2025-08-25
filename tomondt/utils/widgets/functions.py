
from qtpy.QtWidgets import QHBoxLayout, QVBoxLayout, QComboBox, QLabel, QWidget, QFrame
from PyQt5.QtCore import Qt

def _deletewidget(obj,widget):
    if hasattr(obj, widget):
        getattr(obj, widget).hide()    
        obj.layout.removeWidget(getattr(obj, widget))
        getattr(obj, widget).deleteLater()
        delattr(obj, widget)