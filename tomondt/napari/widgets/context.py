import napari

from qtpy.QtWidgets import QHBoxLayout, QComboBox, QLabel

from tomondt.utils.context import device_context
from tomondt.utils.widgets import GroupBoxWidget


class ContextWidget(GroupBoxWidget):
    def __init__(self, viewer: 'napari.viewer.Viewer', parent=None):
        super().__init__(parent, title='Context')
        self._viewer = viewer

        # Create the layout
        self.layout = QHBoxLayout()

        # Create the first combo box
        self.comboBox1 = QComboBox()
        for item in device_context.get_possible_contexts():
            self.comboBox1.addItem(item)

        # Create the second combo box
        self.comboBox2 = QComboBox()
        for i in range(device_context._num_gpus):
            self.comboBox2.addItem(str(i))

        # Add the combo boxes to the layout
        self.layout.addWidget(QLabel("Context:"))
        self.layout.addWidget(self.comboBox1)
        self.layout.addWidget(QLabel("Device:"))
        self.layout.addWidget(self.comboBox2)

        # Set the layout on the widget
        self.setLayout(self.layout)
        self.show()

        # Connect the combo boxes to the change_context function
        self.comboBox1.currentIndexChanged.connect(self.change_context)
        self.comboBox2.currentIndexChanged.connect(self.change_context)

    def change_context(self):
        device_context.change_context(self.comboBox1.currentText(), int(self.comboBox2.currentText()))