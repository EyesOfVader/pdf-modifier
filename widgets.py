from os.path import expanduser
from abc import abstractmethod

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from pdf_modifier import *


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
    
    def __init__(self, text):
        super(FilePicker, self).__init__(text)
        self.clicked.connect(self.select_files)
    
    def select_files(self, event):
        file_names = QFileDialog.getOpenFileNames(self, filter="pdf Files (*.pdf)")[0]
        self.files_selected.emit(file_names)


class FolderPicker(QLineEdit):
    
    def __init__(self, text=expanduser('~')):
        super(FolderPicker, self).__init__(text)
    
    def mousePressEvent(self, event):
        folder = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        if folder:
            self.setText(folder)


class ToolWidget(QWidget):

    def __init__(self, parent=None):
        super(ToolWidget, self).__init__(parent=parent)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.top_bar = QHBoxLayout()

        self.folder_picker = FolderPicker()
        self.top_bar.addWidget(QLabel("Output location: "))
        self.top_bar.addWidget(self.folder_picker)
        add_button = FilePicker("+")
        merge_button = QPushButton("Merge")
        merge_button.clicked.connect(self.merge_files)
        split_button = QPushButton("Split")
        split_button.clicked.connect(self.split_files)
        rotate_button = QPushButton("Rotate Pages")
        rotate_button.clicked.connect(self.rotate_pages)
        self.top_bar.addWidget(add_button)
        self.top_bar.addWidget(merge_button)
        self.top_bar.addWidget(split_button)
        self.top_bar.addWidget(rotate_button)
        self.layout.addLayout(self.top_bar)

        self.file_table = FileTable()
        self.layout.addWidget(self.file_table)
        add_button.files_selected.connect(self.file_table.add_row)

        self.error_dialog = QMessageBox(self)
        self.error_dialog.setIcon(QMessageBox.Critical)
        self.error_dialog.setWindowTitle("Error")
    
    def get_file_paths(self):
        selected_rows = list(set([x.row() for x in self.file_table.selectedItems()]))
        return [self.file_table.item(row, 4).text() for row in selected_rows]

    def merge_files(self):
        if len(self.get_file_paths()) > 1:
            merge_pdfs(self.get_file_paths(), f"{self.folder_picker.text()}/output.pdf")
        else:
            self.error_dialog.setText("Please select more than one document to merge")
            self.error_dialog.exec_()
    
    def split_files(self):
        if len(self.get_file_paths()):
            for path in self.get_file_paths():
                split_pdf(path, self.folder_picker.text())
        else:
            self.error_dialog.setText("Please select a document to split")
            self.error_dialog.exec_()
    
    def rotate_pages(self):
        if len(self.get_file_paths()) == 1:
            pages = int(self.file_table.selectedItems()[3].text())
            res = RotateDialog(page_count=pages, parent=self)
            if res.exec_():
                page_number, direction = res.get_values()
                rotate_page(self.get_file_paths()[0], page_number, direction, self.folder_picker.text())
        else:
            self.error_dialog.setText("Please select a single document")
            self.error_dialog.exec_()


class RotateDialog(QDialog):

    def __init__(self, *, page_count, parent=None):
        super(RotateDialog, self).__init__(parent=parent)
        self.setModal(True)
        self.setWindowTitle("Split Pages")
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        form = QFormLayout()
        self.page_select = QSpinBox()
        self.page_select.setMaximum(page_count)
        self.page_select.setMinimum(1)
        clockwise = QRadioButton("clockwise")
        clockwise.setChecked(True)
        anti = QRadioButton("anti-clockwise")
        self.direction_group = QButtonGroup()
        self.direction_group.addButton(clockwise)
        self.direction_group.addButton(anti)
        direction_layout = QHBoxLayout()
        direction_layout.addWidget(clockwise)
        direction_layout.addWidget(anti)
        form.addRow("Page Number", self.page_select)
        form.addRow("Direction", direction_layout)

        QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        self.layout.addLayout(form)
        self.layout.addWidget(self.buttonBox)
    
    def get_values(self):
        return self.page_select.value(), self.direction_group.checkedButton().text()
        