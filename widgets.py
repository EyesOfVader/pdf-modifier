from os.path import expanduser

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
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.viewport().setAcceptDrops(True)
        self.setDragDropOverwriteMode(False)
        self.setDropIndicatorShown(True)

        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setDragDropMode(QAbstractItemView.InternalMove)
    
    def dropEvent(self, event: QDropEvent):
        if not event.isAccepted() and event.source() == self:
            drop_row = self.drop_on(event)

            rows = sorted(set(item.row() for item in self.selectedItems()))
            rows_to_move = [[QTableWidgetItem(self.item(row_index, column_index)) for column_index in range(self.columnCount())]
                            for row_index in rows]
            for row_index in reversed(rows):
                self.removeRow(row_index)
                if row_index < drop_row:
                    drop_row -= 1

            for row_index, data in enumerate(rows_to_move):
                row_index += drop_row
                self.insertRow(row_index)
                for column_index, column_data in enumerate(data):
                    self.setItem(row_index, column_index, column_data)
            event.accept()
            for row_index in range(len(rows_to_move)):
                self.item(drop_row + row_index, 0).setSelected(True)
                self.item(drop_row + row_index, 1).setSelected(True)
        super().dropEvent(event)

    def drop_on(self, event):
        index = self.indexAt(event.pos())
        if not index.isValid():
            return self.rowCount()

        return index.row() + 1 if self.is_below(event.pos(), index) else index.row()

    def is_below(self, pos, index):
        rect = self.visualRect(index)
        margin = 2
        if pos.y() - rect.top() < margin:
            return False
        elif rect.bottom() - pos.y() < margin:
            return True
        # noinspection PyTypeChecker
        return rect.contains(pos, True) and not (int(self.model().flags(index)) & Qt.ItemIsDropEnabled) and pos.y() >= rect.center().y()

    
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
    
    def __init__(self, text, filter):
        super(FilePicker, self).__init__(text)
        self.filter = filter
        self.clicked.connect(self.select_files)
    
    def select_files(self, event):
        file_names = QFileDialog.getOpenFileNames(self, filter=self.filter)[0]
        self.files_selected.emit(file_names)


class FolderPicker(QPushButton):

    folder_selected = pyqtSignal(str)
    
    def __init__(self, text):
        super(FolderPicker, self).__init__(text)
        self.clicked.connect(self.select_files)
    
    def select_files(self, event):
        folder = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        print(folder)
        self.folder_selected.emit(folder)
    

class PDFPushButton(QPushButton):
    
    def __init__(self, *args, **kwargs):
        super(PDFPushButton, self).__init__(*args, **kwargs)
        self.setFixedHeight(100)
        self.setFixedWidth(100)


class ToolWidget(QWidget):
        
    def __init__(self, *args, **kwargs):
        super(ToolWidget, self).__init__(*args, **kwargs)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.top_bar = QHBoxLayout()
        self.layout.addLayout(self.top_bar)


class MergeWidget(ToolWidget):
    
    def __init__(self, *args, **kwargs):
        super(MergeWidget, self).__init__(*args, **kwargs)
        fp = FilePicker("Load Files", "pdf Files (*.pdf)")
        ft = FileTable()
        fp.files_selected.connect(ft.add_row)
        output_location = QLineEdit(expanduser('~'))
        output_selector = FolderPicker('..')
        self.top_bar.addWidget(fp)
        self.top_bar.addWidget(QLabel("Output location: "))
        self.top_bar.addWidget(output_location)
        self.top_bar.addWidget(output_selector)
        self.layout.addWidget(ft)