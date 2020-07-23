import os
import sys
import traceback

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from widgets import *

class Main(QMainWindow):

    def __init__(self, parent=None):
        super(Main, self).__init__(parent)
        self.setWindowTitle("PDF Modifier")
        self.setCentralWidget(ToolWidget())
        self.resize(QDesktopWidget().availableGeometry().size() * 0.7)
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
