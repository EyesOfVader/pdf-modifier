from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from pdf_modifier import read_pdf_info


class FileTable(QTableWidget):
    
    def __init__(self, *args, **kwargs):
        super(FileTable, self).__init__(*args, **kwargs)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setColumnCount(5)
        self.header_labels = ['Title', 'Author', 'Subject', 'Page Count', 'File Path']
        self.setHorizontalHeaderLabels(self.header_labels)
    
    @pyqtSlot(list)
    def add_row(self, files):
        for f in files:
            self.insertRow(self.rowCount())
            info = read_pdf_info(f)
            for index, header in enumerate(self.header_labels):
                self.setItem(self.rowCount()-1, index, QTableWidgetItem(str(info[header])))
        self.resizeColumnToContents(4)


class FilePicker(QPushButton):

    files_selected = pyqtSignal(list)
    
    def __init__(self):
        super(FilePicker, self).__init__("Load Files")
        self.clicked.connect(self.select_files)
    
    def select_files(self, event):
        file_names = QFileDialog.getOpenFileNames(self, filter="pdf Files (*.pdf)", caption="Select your PDFs")[0]
        self.files_selected.emit(file_names)

    


    

    

    

    