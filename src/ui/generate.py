# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'src/ui/generate.ui'
#
# Created by: PyQt5 UI code generator 5.15.6
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.setEnabled(True)
        Dialog.resize(317, 258)
        self.verticalLayout = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.label_7 = QtWidgets.QLabel(Dialog)
        self.label_7.setObjectName("label_7")
        self.gridLayout.addWidget(self.label_7, 0, 0, 1, 1)
        self.label_6 = QtWidgets.QLabel(Dialog)
        self.label_6.setObjectName("label_6")
        self.gridLayout.addWidget(self.label_6, 1, 0, 1, 1)
        self.lineEditLength = QtWidgets.QLineEdit(Dialog)
        self.lineEditLength.setObjectName("lineEditLength")
        self.gridLayout.addWidget(self.lineEditLength, 1, 1, 1, 1)
        self.lineEditName = QtWidgets.QLineEdit(Dialog)
        self.lineEditName.setObjectName("lineEditName")
        self.gridLayout.addWidget(self.lineEditName, 0, 1, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)
        self.gridLayout_2 = QtWidgets.QGridLayout()
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.checkBoxEnforceLowercase = QtWidgets.QCheckBox(Dialog)
        self.checkBoxEnforceLowercase.setChecked(True)
        self.checkBoxEnforceLowercase.setObjectName("checkBoxEnforceLowercase")
        self.gridLayout_2.addWidget(self.checkBoxEnforceLowercase, 2, 2, 1, 1)
        self.checkBoxAllowLowercase = QtWidgets.QCheckBox(Dialog)
        self.checkBoxAllowLowercase.setChecked(True)
        self.checkBoxAllowLowercase.setObjectName("checkBoxAllowLowercase")
        self.gridLayout_2.addWidget(self.checkBoxAllowLowercase, 2, 1, 1, 1)
        self.checkBoxEnforceNumbers = QtWidgets.QCheckBox(Dialog)
        self.checkBoxEnforceNumbers.setEnabled(True)
        self.checkBoxEnforceNumbers.setChecked(True)
        self.checkBoxEnforceNumbers.setObjectName("checkBoxEnforceNumbers")
        self.gridLayout_2.addWidget(self.checkBoxEnforceNumbers, 4, 2, 1, 1)
        self.checkBoxEnforceUppercase = QtWidgets.QCheckBox(Dialog)
        self.checkBoxEnforceUppercase.setChecked(True)
        self.checkBoxEnforceUppercase.setObjectName("checkBoxEnforceUppercase")
        self.gridLayout_2.addWidget(self.checkBoxEnforceUppercase, 3, 2, 1, 1)
        self.label_3 = QtWidgets.QLabel(Dialog)
        self.label_3.setObjectName("label_3")
        self.gridLayout_2.addWidget(self.label_3, 4, 0, 1, 1)
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setObjectName("label")
        self.gridLayout_2.addWidget(self.label, 2, 0, 1, 1)
        self.checkBoxAllowUppercase = QtWidgets.QCheckBox(Dialog)
        self.checkBoxAllowUppercase.setChecked(True)
        self.checkBoxAllowUppercase.setObjectName("checkBoxAllowUppercase")
        self.gridLayout_2.addWidget(self.checkBoxAllowUppercase, 3, 1, 1, 1)
        self.checkBoxEnforceSpecialSymbols = QtWidgets.QCheckBox(Dialog)
        self.checkBoxEnforceSpecialSymbols.setChecked(True)
        self.checkBoxEnforceSpecialSymbols.setObjectName("checkBoxEnforceSpecialSymbols")
        self.gridLayout_2.addWidget(self.checkBoxEnforceSpecialSymbols, 5, 2, 1, 1)
        self.checkBoxAllowSpecialSymbols = QtWidgets.QCheckBox(Dialog)
        self.checkBoxAllowSpecialSymbols.setChecked(True)
        self.checkBoxAllowSpecialSymbols.setObjectName("checkBoxAllowSpecialSymbols")
        self.gridLayout_2.addWidget(self.checkBoxAllowSpecialSymbols, 5, 1, 1, 1)
        self.checkBoxAllowNumbers = QtWidgets.QCheckBox(Dialog)
        self.checkBoxAllowNumbers.setChecked(True)
        self.checkBoxAllowNumbers.setObjectName("checkBoxAllowNumbers")
        self.gridLayout_2.addWidget(self.checkBoxAllowNumbers, 4, 1, 1, 1)
        self.label_4 = QtWidgets.QLabel(Dialog)
        self.label_4.setObjectName("label_4")
        self.gridLayout_2.addWidget(self.label_4, 5, 0, 1, 1)
        self.label_2 = QtWidgets.QLabel(Dialog)
        self.label_2.setObjectName("label_2")
        self.gridLayout_2.addWidget(self.label_2, 3, 0, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout_2)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label_5 = QtWidgets.QLabel(Dialog)
        self.label_5.setObjectName("label_5")
        self.horizontalLayout.addWidget(self.label_5)
        self.lineEditSpecialSymbols = QtWidgets.QLineEdit(Dialog)
        self.lineEditSpecialSymbols.setObjectName("lineEditSpecialSymbols")
        self.horizontalLayout.addWidget(self.lineEditSpecialSymbols)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.buttonBox = QtWidgets.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept)  # type: ignore
        self.buttonBox.rejected.connect(Dialog.reject)  # type: ignore
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.label_7.setText(_translate("Dialog", "Service name:"))
        self.label_6.setText(_translate("Dialog", "Length:"))
        self.lineEditLength.setPlaceholderText(_translate("Dialog", "16"))
        self.checkBoxEnforceLowercase.setText(_translate("Dialog", "Enforce"))
        self.checkBoxAllowLowercase.setText(_translate("Dialog", "Allow"))
        self.checkBoxEnforceNumbers.setText(_translate("Dialog", "Enforce"))
        self.checkBoxEnforceUppercase.setText(_translate("Dialog", "Enforce"))
        self.label_3.setText(_translate("Dialog", "Numbers"))
        self.label.setText(_translate("Dialog", "Lowercase"))
        self.checkBoxAllowUppercase.setText(_translate("Dialog", "Allow"))
        self.checkBoxEnforceSpecialSymbols.setText(_translate("Dialog", "Enforce"))
        self.checkBoxAllowSpecialSymbols.setText(_translate("Dialog", "Allow"))
        self.checkBoxAllowNumbers.setText(_translate("Dialog", "Allow"))
        self.label_4.setText(_translate("Dialog", "Special symbols"))
        self.label_2.setText(_translate("Dialog", "Uppercase"))
        self.label_5.setText(_translate("Dialog", "Which symbols?"))
        self.lineEditSpecialSymbols.setPlaceholderText(_translate("Dialog", "!\\\"#$%&\'()*+,-./:;<=>?@[]^_`{|}~"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())
