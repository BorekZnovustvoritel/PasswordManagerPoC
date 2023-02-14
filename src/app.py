from __future__ import annotations

import string
from typing import List
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import QModelIndex, Qt
from PyQt5.QtGui import QFont
from PyQt5.uic.properties import QtGui
import re

from src.utils import is_first_init
from src.interface import Usage, Alphabet
import src.interface as iface
import src.config as config
from src.ui import auth, main_w, generate, first_auth, add
from src.persistence import Service


class LoginDialog(QtWidgets.QDialog):
    """Dialog window that appears before the app lets you do anything."""

    def __init__(self, parent=None):
        super().__init__(parent)

        if is_first_init():
            self.ui = first_auth.Ui_Dialog()
            self.ui.setupUi(self)

            self.ui.pushButton.clicked.connect(self.first_authenticate)
        else:
            self.ui = auth.Ui_Dialog()
            self.ui.setupUi(self)
            self.child = None

            self.ui.pushButton.clicked.connect(self.authenticate)
        self.rejected.connect(self.parent().close)
        self.setWindowState(Qt.WindowActive)
        self.show()

    def authenticate(self):
        """Authentication after the user account is set."""
        self._init_manager()

    def first_authenticate(self):
        """Setting up the password."""
        line1 = self.ui.lineEdit.text()
        line2 = self.ui.lineEdit_2.text()
        if not line1 == line2:
            error_dialog = QtWidgets.QMessageBox(self)
            error_dialog.setText("Passwords differ!")
            error_dialog.show()
            self.ui.lineEdit.setText("")
            self.ui.lineEdit_2.setText("")
            return
        elif len(line1) < 8:
            error_dialog = QtWidgets.QMessageBox(self)
            error_dialog.setText("Password is too short!")
            error_dialog.show()
            self.ui.lineEdit.setText("")
            self.ui.lineEdit_2.setText("")
            return
        self._init_manager()

    def _init_manager(self):
        """Tries to authenticate. Displays error message window or initiates the main window."""
        try:
            manager = iface.PasswordManager(self.ui.lineEdit.text())
            self.parent().manager = manager
            self.parent().init_data()
            self.parent().resize_table()
            self.parent().ui.generate_password.setEnabled(True)
            self.parent().ui.store_password.setEnabled(True)
            self.accept()
        except ValueError:
            error_dialog = QtWidgets.QMessageBox(self)
            error_dialog.setText("Wrong password!")
            error_dialog.show()
            self.ui.lineEdit.setText("")


class MainWindow(QtWidgets.QMainWindow):
    """I wonder what this class is..."""

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.ui = main_w.Ui_MainWindow()
        self.ui.setupUi(self)
        self.set_location()
        self.setWindowTitle("Password Manager")

        self.manager = None
        self.ui.generate_password.setDisabled(True)
        self.ui.store_password.setDisabled(True)

        self.login_dialog = LoginDialog(self)
        self.login_dialog.setWindowTitle("Unlock the application:")

        self.ui.tableView.setSelectionBehavior(
            QtWidgets.QTableView.SelectionBehavior.SelectRows
        )
        self.ui.tableView.verticalHeader().setVisible(False)
        self.ui.tableView.clicked.connect(self.copy_password)
        self.ui.actionDelete.triggered.connect(self.delete_item)
        self.ui.tableView.addAction(self.ui.actionDelete)
        self.child_generate_password = None
        self.child_add_password = AddServiceDialogAdd(self)

        self.ui.generate_password.clicked.connect(self.add_service)
        self.ui.store_password.clicked.connect(self.child_add_password.show)

        self.show()

    def copy_password(self, item: QModelIndex):
        """Doubleclick on a service copies the password to your clipboard."""
        service = self.ui.tableView.model().data[item.row()][0]
        QtWidgets.QApplication.clipboard().setText(service.password)
        self.ui.tableView.model().data[item.row()] = (service, service.password)
        self.resize_table()

    def add_service(self):
        """Opens dialog for adding services."""
        self.child_generate_password = AddServiceDialogGenerate(self)
        self.child_generate_password.show()

    def init_data(self):
        """Fills the table and adjust its size."""
        self.ui.tableView.setModel(
            ServiceTableModel(
                [(s, "*****") for s in self.manager.services]
            )
        )
        self.resize_table()

    def resize_table(self):
        """Adjust the size of the table."""
        self.ui.tableView.resizeColumnToContents(0)
        self.ui.tableView.setColumnWidth(
            1, self.ui.tableView.width() - self.ui.tableView.columnWidth(0) - 2
        )

    def delete_item(self):
        """Open dialog to confirm the deletion and proceed to delete."""
        indexes = set([i.row() for i in self.ui.tableView.selectedIndexes()])
        services = [self.ui.tableView.model().data[i][0] for i in indexes]
        if not services:
            return
        reply = QtWidgets.QMessageBox.question(
            self,
            "Are you sure?",
            f"Do you really want to delete {', '.join([s.name for s in services])}?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
        )
        if reply == QtWidgets.QMessageBox.Yes:
            for s in services:
                self.manager.remove_service(s.idx)
            self.init_data()

    def resizeEvent(self, a0: QtGui.QResizeEvent) -> None:
        super(MainWindow, self).resizeEvent(a0)
        self.resize_table()

    def set_location(self):
        """Positions the application to the bottom-right corner of the screen."""
        geometry = QtWidgets.QDesktopWidget().availableGeometry()
        widget = self.geometry()
        x = geometry.width() - widget.width()
        y = geometry.height() - widget.height()
        self.move(x, y)


class ServiceTableModel(QtCore.QAbstractTableModel):
    """Nodel for displaying the data in the table."""

    def __init__(self, data: List[(Service, str)], parent=None):
        super(ServiceTableModel, self).__init__(parent)
        data.sort(key=lambda x: x[0].idx)
        self.data = data

    def rowCount(self, parent: QModelIndex = ...) -> int:
        return len(self.data)

    def columnCount(self, parent: QModelIndex = ...) -> int:
        return 2

    def data(self, index: QModelIndex, role: int = ...) -> str:
        if role == QtCore.Qt.DisplayRole:
            row = index.row()
            col = index.column()
            return str(self.data[row][col])

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = ...):
        if role == QtCore.Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                if section == 0:
                    return "Service"
                elif section == 1:
                    return "Password"


class AddServiceDialogGenerate(QtWidgets.QDialog):
    """Dialog that lets you add a service and change the attributes of its password."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = generate.Ui_Dialog()
        self.ui.setupUi(self)
        self.setWindowTitle("Add a service")
        self.ui.lineEditLength.setPlaceholderText(str(config.default_length))
        self.ui.lineEditSpecialSymbols.setPlaceholderText(config.default_special_characters)

    def accept(self) -> None:
        name = self.ui.lineEditName.text()
        if not name:
            return self.reject()
        length = self.ui.lineEditLength.text()
        if not length or not re.match(r'^\d+$', length):
            length = config.default_length
        else:
            length = int(length)
        lowercase = Usage.DISALLOW
        uppercase = Usage.DISALLOW
        numbers = Usage.DISALLOW
        special_symbols = Usage.DISALLOW
        if self.ui.checkBoxEnforceLowercase.isChecked():
            lowercase = Usage.ENFORCE
        elif self.ui.checkBoxAllowLowercase.isChecked():
            lowercase = Usage.ALLOW
        if self.ui.checkBoxEnforceUppercase.isChecked():
            uppercase = Usage.ENFORCE
        elif self.ui.checkBoxAllowUppercase.isChecked():
            uppercase = Usage.ALLOW
        if self.ui.checkBoxEnforceNumbers.isChecked():
            numbers = Usage.ENFORCE
        elif self.ui.checkBoxAllowNumbers.isChecked():
            numbers = Usage.ALLOW
        specials_to_use = "".join(set(self.ui.lineEditSpecialSymbols.text()))
        if not specials_to_use:
            specials_to_use = config.default_special_characters
        if self.ui.checkBoxEnforceSpecialSymbols.isChecked():
            special_symbols = Usage.ENFORCE
        elif self.ui.checkBoxAllowSpecialSymbols.isChecked():
            special_symbols = Usage.ALLOW
        self.ui.lineEditName.setText('')
        alphabet = Alphabet(lowercase, uppercase, numbers, special_symbols, specials_to_use)
        try:
            self.parent().manager.add_service(
                name, length, alphabet
            )
        except Exception as e:
            message = QtWidgets.QMessageBox(self)
            message.setText(str(e))
            message.show()
            self.reject()
            return

        self.parent().init_data()
        self.hide()

    def reject(self) -> None:
        self.hide()


class AddServiceDialogAdd(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = add.Ui_Dialog()
        self.ui.setupUi(self)
        self.setWindowTitle("Add a service")

    def accept(self) -> None:
        self.parent().manager.add_service(self.ui.lineEditName.text(), password=self.ui.lineEditPassword.text())
        self.ui.lineEditName.setText('')
        self.ui.lineEditPassword.setText('')
        self.parent().init_data()
        self.hide()

    def reject(self) -> None:
        self.ui.lineEditName.setText('')
        self.ui.lineEditPassword.setText('')
        self.hide()


def main():
    app = QtWidgets.QApplication([])
    app.setFont(QFont("Helvetica", 10))
    rw = MainWindow()
    app.exec_()
