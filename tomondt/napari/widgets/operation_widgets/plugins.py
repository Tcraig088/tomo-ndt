import napari
 
from qtpy.QtWidgets import QVBoxLayout, QComboBox, QLabel, QWidget, QPushButton, QDialog, QGridLayout
from qtpy.QtWidgets import QDialog

from tomondt.napari.data_types import NDt_Types, convert_layer_to_type, convert_type_to_layer
from tomondt.napari.plugin_register import plugin_manager
from tomondt.utils.widgets import _deletewidget
from tomondt.utils.output import progressbar

class SettingsDialog(QDialog):
    def __init__(self, viewer:'napari.viewer.Viewer', parent=None, plugin_key = 'default', key='default', obj = None):
        super().__init__(parent)
        #Check if widget is a class 
        self.layout = QVBoxLayout()
        self._viewer = viewer
        
        self.widget = plugin_manager.plugins[plugin_key][key].widget(viewer= viewer, obj = obj)
        
        self.widget.show()
        self.button = QPushButton('Set')
            
        self.button.clicked.connect(self.get_settings)
        
        self.layout.addWidget(self.widget)
        self.layout.addWidget(self.button)

        self.setLayout(self.layout)
        self.show()
        
    def get_settings(self):
        self.settings = self.widget.get_settings()
        self.close()

class PluginFunctionWidget(QWidget):
    def __init__(self, viewer: 'napari.viewer.Viewer', parent=None, plugin_key='default'):
        super().__init__(parent)
        self._viewer = viewer
        self.selection =  self._viewer.layers.selection.active
        self.func = None

        self.plugin_key = plugin_key
        self.layout = QGridLayout()
        
        self.label = QLabel(plugin_key+':')
        self.combobox = QComboBox()
        self.combobox.addItem('Select')
        for key in plugin_manager.plugins[plugin_key].keys():
            self.combobox.addItem(key)
        self.pushbutton = QPushButton('Run')
        
        self.combobox.currentTextChanged.connect(self.get_plugin_settings)
        self.pushbutton.clicked.connect(self.run_function)
        progressbar.isActiveChanged.connect(self.showprogress)
        
        self.layout.addWidget(self.label,0,0)
        self.layout.addWidget(self.combobox,0, 1)
        self.layout.addWidget(self.pushbutton, 2, 0)

        self.setLayout(self.layout)
        self.show()
    
    def get_plugin_settings(self):
        _deletewidget(self, 'settingsbutton')   
        _deletewidget(self, 'widget')
        if hasattr(self, 'settings'):
            del self.settings
        if self.combobox.currentText() != 'Select':
            if plugin_manager.plugins[self.plugin_key][self.combobox.currentText()].widget is not None:
                self.settingsbutton = QPushButton('Settings')
                self.settingsbutton.clicked.connect(self.open_menu)
                self.layout.addWidget(self.settingsbutton, 0, 2)
                
    def open_menu(self):
        widget= plugin_manager.plugins[self.plugin_key][self.combobox.currentText()].widget
        if widget is not None:
            self.widget = widget(self._viewer)
        if isinstance(self.widget, QDialog):
            self.widget.exec_()
            self.settings = self.widget.settings
        else:
            self.layout.addWidget(self.widget, 1, 1, 1, 5)    
            self.show()
        
    def run_function(self):
        plugin = plugin_manager.plugins[self.plugin_key][self.combobox.currentText()]
        selection = convert_layer_to_type(self._viewer.layers.selection.active)
         
        action_keys = [0, 0]
        if hasattr(self, 'widget'):
            if (self.widget is not None) & ~isinstance(self.widget, QDialog) :
                self.settings = self.widget.exec()

        if hasattr(self, 'settings'):
            action_keys[0] = 1
            
        if plugin.isclass:
            action_keys[1] = 1
            
        match action_keys:
            case [1, 1]:
                result  = plugin.obj.exec(selection, **self.settings)
            case [1, 0]:
                result  = plugin.obj(selection, **self.settings)
            case [0, 1]:
                result = plugin.obj.exec(selection)
            case [0, 0]:
                result = plugin.obj(selection)
            case _:
                raise Exception('Invalid action keys')
             
        result, metadata = convert_type_to_layer(result)
        self._viewer.add_image(result, name = self._viewer.layers.selection.active.name + self.plugin_key, metadata = metadata)
        
    def showprogress(self, value):
        if value == True:
            self.bar = progressbar.qtbar
            self.layout.addWidget(self.bar, 3, 0, 1, 5)

        else:
            _deletewidget(self, 'bar')