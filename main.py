import os
import sys
import traceback

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from widgets import FileTable, FilePicker

class Main(QMainWindow):

    def __init__(self, parent=None):
        super(Main, self).__init__(parent)
        # Check if we have a value stored for previous window size. If not, use default
        self.setGeometry(QRect(500, 500, 1030, 600))
        self.setWindowTitle("PDF Modifier")
        container = QWidget()
        self.setCentralWidget(container)
        layout = QVBoxLayout()
        container.setLayout(layout)
        top_bar = QHBoxLayout()
        file_picker = FilePicker()
        top_bar.addWidget(file_picker)
        layout.addLayout(top_bar)
        file_table = FileTable()
        file_picker.files_selected.connect(file_table.add_row)
        layout.addWidget(file_table)
        self.center()
        self.show()

    # Open window in center of screen
    def center(self):
        geometry = self.frameGeometry()
        screen = QApplication.desktop().screenNumber(QApplication.desktop().cursor().pos())
        center = QApplication.desktop().screenGeometry(screen).center()
        geometry.moveCenter(center)
        self.move(geometry.topLeft())


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Main()
    sys._excepthook = sys.excepthook

    def exception_hook(exctype, value, trace):
        print(exctype, value, trace)
        sys._excepthook(exctype, value, trace)
        sys.exit(1)

    sys.excepthook = exception_hook
    sys.exit(app.exec_())
