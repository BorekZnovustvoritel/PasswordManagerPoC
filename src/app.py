from __future__ import annotations

import string
from typing import List
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import QModelIndex, Qt
from PyQt5.uic.properties import QtGui

import src.interface as iface
import src.config as config
from src.ui import auth, main_w, add


class LoginDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = auth.Ui_Dialog()
        self.ui.setupUi(self)
        self.child = None

        self.ui.pushButton.clicked.connect(self.authenticate)
        self.rejected.connect(self.parent().close)
        self.setWindowState(Qt.WindowActive)
        self.show()

    def authenticate(self) -> MainWindow:
        try:
            manager = iface.PasswordManager(self.ui.lineEdit.text())
            self.parent().manager = manager
            self.parent().init_data()
            self.parent().resize_table()
            self.parent().ui.pushButton.setEnabled(True)
            self.accept()
        except ValueError:
            self.ui.label.setText("Wrong Password!")
        return self


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.ui = main_w.Ui_MainWindow()
        self.ui.setupUi(self)
        self.set_location()
        self.setWindowTitle("Password Manager")

        self.manager = None
        self.ui.pushButton.setDisabled(True)

        self.login_dialog = LoginDialog(self)
        self.login_dialog.setWindowTitle("Unlock the application:")

        self.ui.tableView.setSelectionBehavior(QtWidgets.QTableView.SelectionBehavior.SelectRows)
        self.ui.tableView.verticalHeader().setVisible(False)
        self.ui.tableView.clicked.connect(self.copy_password)
        self.ui.actionDelete.triggered.connect(self.delete_item)
        self.ui.tableView.addAction(self.ui.actionDelete)

        self.ui.pushButton.clicked.connect(self.add_service)

        self.child = AddServiceDialog(self)
        self.show()

    def copy_password(self, item: QModelIndex):
        password = self.ui.tableView.model().data[item.row()][1]
        QtWidgets.QApplication.clipboard().setText(password)

    def add_service(self):
        self.child.show()

    def init_data(self):
        self.ui.tableView.setModel(
            ServiceTableModel([(o.name, self.manager.generate(o.name)) for o in self.manager.services]))

    def resize_table(self):
        self.ui.tableView.setColumnWidth(0, self.ui.tableView.width() // 2)
        self.ui.tableView.setColumnWidth(1, self.ui.tableView.width() - self.ui.tableView.columnWidth(0) - 2)

    def delete_item(self):
        indexes = self.ui.tableView.selectedIndexes()
        names = set()
        for i in indexes:
            names.add(self.ui.tableView.model().data[i.row()][0])
        if not names:
            return
        reply = QtWidgets.QMessageBox.question(self, "Are you sure?",
                                               f"Do you really want to delete {', '.join(names)}?",
                                               QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if reply == QtWidgets.QMessageBox.Yes:
            for name in names:
                self.manager.remove_service(name)
            self.init_data()

    def resizeEvent(self, a0: QtGui.QResizeEvent) -> None:
        super(MainWindow, self).resizeEvent(a0)
        self.resize_table()

    def set_location(self):
        geometry = QtWidgets.QDesktopWidget().availableGeometry()
        widget = self.geometry()
        x = geometry.width() - widget.width()
        y = geometry.height() - widget.height()
        self.move(x, y)


class ServiceTableModel(QtCore.QAbstractTableModel):
    def __init__(self, data: List[(str, str)], parent=None):
        super(ServiceTableModel, self).__init__(parent)
        self.data = data

    def rowCount(self, parent: QModelIndex = ...) -> int:
        return len(self.data)

    def columnCount(self, parent: QModelIndex = ...) -> int:
        return 2

    def data(self, index: QModelIndex, role: int = ...) -> str:
        if role == QtCore.Qt.DisplayRole:
            row = index.row()
            col = index.column()
            return self.data[row][col]

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = ...):
        if role == QtCore.Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                if section == 0:
                    return "Service"
                elif section == 1:
                    return "Password"


class AddServiceDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = add.Ui_Dialog()
        self.ui.setupUi(self)
        self.ui.buttonBox.accepted.connect(self.accept)
        self.ui.buttonBox.rejected.connect(self.reject)
        self.setWindowTitle("Add a service")

    def accept(self) -> None:
        name = self.ui.lineEditName.text()
        if not name:
            return self.reject()
        length = self.ui.lineEditLength.text()
        if not length:
            length = 32
        else:
            length = int(length)
        alphabet: str = ""
        if self.ui.checkBoxEnforceLowercase.isChecked():
            alphabet += "\[" + string.ascii_lowercase + "\]"
        elif self.ui.checkBoxAllowLowercase.isChecked():
            alphabet += string.ascii_lowercase
        if self.ui.checkBoxEnforceUppercase.isChecked():
            alphabet += "\[" + string.ascii_uppercase + "\]"
        elif self.ui.checkBoxAllowUppercase.isChecked():
            alphabet += string.ascii_uppercase
        if self.ui.checkBoxEnforceNumbers.isChecked():
            alphabet += "\[" + "".join([str(i) for i in range(10)]) + "\]"
        elif self.ui.checkBoxAllowNumbers.isChecked():
            alphabet += "".join([str(i) for i in range(10)])
        special_symbols = "".join(set(self.ui.lineEditSpecialSymbols.text()))
        if not special_symbols:
            special_symbols = "!\"#$%&'()*+,-./:;<=>?@[]^_`{|}~ \\"
        elif "\[" in special_symbols or "\]" in special_symbols:
            special_symbols = special_symbols.replace("\\", "")
            special_symbols += "\\"
        if self.ui.checkBoxEnforceSpecialSymbols.isChecked():
            alphabet += "\[" + special_symbols + "\]"
        elif self.ui.checkBoxAllowSpecialSymbols.isChecked():
            alphabet += special_symbols

        try:
            self.parent().manager.add_service(name, length, config.default_iterations, alphabet)
        except Exception as e:
            message = QtWidgets.QMessageBox(self)
            message.setText(str(e))
            message.show()
            self.reject()
            return

        self.parent().init_data()
        self.hide()
        self.parent().child = AddServiceDialog(self.parent())

    def reject(self) -> None:
        self.hide()
        self.parent().child = AddServiceDialog(self.parent())


def main():
    app = QtWidgets.QApplication([])
    rw = MainWindow()
    app.exec_()
