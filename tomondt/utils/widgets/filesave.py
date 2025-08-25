import napari

from qtpy.QtWidgets import QHBoxLayout, QVBoxLayout, QComboBox, QLabel, QWidget, QFrame, QLineEdit, QPushButton
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFileDialog

class FileSaveWidget(QWidget):
    def __init__(self, viewer: 'napari.viewer.Viewer', parent=None):
        super().__init__(parent)
        self._viewer = viewer

        # A line to enter the file name
        self.Label = QLabel('File name:')
        self.LineEntry = QLineEdit()
        self.LineEntry.setPlaceholderText('Enter file name')
        self.BrowseButton = QPushButton('Browse')

        # Connect Browse Button to file Save dialog
        self.BrowseButton.clicked.connect(self.save_file)

        self.layout = QHBoxLayout()
        self.layout.addWidget(self.Label)
        self.layout.addWidget(self.LineEntry)
        self.layout.addWidget(self.BrowseButton)
        self.layout.setAlignment(Qt.AlignTop)
        self.setLayout(self.layout)
        self.show()

    def save_file(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getSaveFileName(None,"QFileDialog.getSaveFileName()","","All Files (*);; Volume-Time Files (*.vmf)", options=options)
        # Change LineEntry text to the file name
        self.LineEntry.setText(fileName)