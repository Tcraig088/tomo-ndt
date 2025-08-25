import napari

from qtpy.QtWidgets import QWidget, QButtonGroup, QVBoxLayout

from tomondt.utils.widgets import GroupBoxWidget
from tomondt.napari.widgets.operation_widgets import SimulateWidget, AlignWidget, ProjectionWidget, PluginFunctionWidget

class CurrentOperationWidget(GroupBoxWidget):
    def __init__(self, viewer: 'napari.viewer.Viewer', parent=None):
        super().__init__(parent, title ='Current Task')
        self._viewer = viewer

        # Create the layout
        self.layout = QVBoxLayout()

        # Create a button group to make the radio buttons mutually exclusive
        self.buttonGroup = QButtonGroup()

        self.widget = QWidget()
        self.layout.addWidget(self.widget)

        self.setLayout(self.layout)
        self.show()
        
    def removeall(self):
        #clear the self.widget
        if hasattr(self, 'widget'):
            self.layout.removeWidget(self.widget)  # Remove the table from the layout
            self.widget.hide()  # Hide the table
            self.widget.deleteLater()  # Schedule the table to be deleted

    def setWidget(self, widget_name):
        self.removeall()
        match widget_name:
            case 'Simulate':
                self.widget = SimulateWidget(self._viewer)
            case 'Align':
                self.widget = PluginFunctionWidget(self._viewer, plugin_key='Alignments')
            case 'Project':
                self.widget = ProjectionWidget(self._viewer)
        
        self.layout.addWidget(self.widget)
        self.show()