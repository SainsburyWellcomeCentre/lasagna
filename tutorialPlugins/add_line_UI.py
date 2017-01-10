# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'add_line.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_addLine(object):
    def setupUi(self, addLine):
        addLine.setObjectName(_fromUtf8("addLine"))
        addLine.resize(456, 378)
        self.verticalLayout_2 = QtGui.QVBoxLayout(addLine)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.splitter = QtGui.QSplitter(addLine)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName(_fromUtf8("splitter"))
        self.tableWidget = QtGui.QTableWidget(self.splitter)
        self.tableWidget.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.tableWidget.setObjectName(_fromUtf8("tableWidget"))
        self.tableWidget.setColumnCount(4)
        self.tableWidget.setRowCount(0)
        item = QtGui.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(0, item)
        item = QtGui.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(1, item)
        item = QtGui.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(2, item)
        item = QtGui.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(3, item)
        self.tableWidget.horizontalHeader().setDefaultSectionSize(60)
        self.widget = QtGui.QWidget(self.splitter)
        self.widget.setObjectName(_fromUtf8("widget"))
        self.verticalLayout = QtGui.QVBoxLayout(self.widget)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.label_3 = QtGui.QLabel(self.widget)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.verticalLayout.addWidget(self.label_3)
        self.name_lineEdit = QtGui.QLineEdit(self.widget)
        self.name_lineEdit.setObjectName(_fromUtf8("name_lineEdit"))
        self.verticalLayout.addWidget(self.name_lineEdit)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.deg_spinBox = QtGui.QSpinBox(self.widget)
        self.deg_spinBox.setMinimum(1)
        self.deg_spinBox.setObjectName(_fromUtf8("deg_spinBox"))
        self.horizontalLayout.addWidget(self.deg_spinBox)
        self.label = QtGui.QLabel(self.widget)
        self.label.setObjectName(_fromUtf8("label"))
        self.horizontalLayout.addWidget(self.label)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.interactive_checkBox = QtGui.QCheckBox(self.widget)
        self.interactive_checkBox.setObjectName(_fromUtf8("interactive_checkBox"))
        self.verticalLayout.addWidget(self.interactive_checkBox)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.label_2 = QtGui.QLabel(self.widget)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.verticalLayout.addWidget(self.label_2)
        self.spinBox = QtGui.QSpinBox(self.widget)
        self.spinBox.setReadOnly(True)
        self.spinBox.setObjectName(_fromUtf8("spinBox"))
        self.verticalLayout.addWidget(self.spinBox)
        self.line = QtGui.QFrame(self.widget)
        self.line.setFrameShape(QtGui.QFrame.HLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName(_fromUtf8("line"))
        self.verticalLayout.addWidget(self.line)
        self.fit_pushButton = QtGui.QPushButton(self.widget)
        self.fit_pushButton.setObjectName(_fromUtf8("fit_pushButton"))
        self.verticalLayout.addWidget(self.fit_pushButton)
        self.add_pushButton = QtGui.QPushButton(self.widget)
        self.add_pushButton.setObjectName(_fromUtf8("add_pushButton"))
        self.verticalLayout.addWidget(self.add_pushButton)
        self.verticalLayout_2.addWidget(self.splitter)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.closeButton = QtGui.QPushButton(addLine)
        self.closeButton.setObjectName(_fromUtf8("closeButton"))
        self.horizontalLayout_2.addWidget(self.closeButton)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem1)
        self.clear_pushButton = QtGui.QPushButton(addLine)
        self.clear_pushButton.setObjectName(_fromUtf8("clear_pushButton"))
        self.horizontalLayout_2.addWidget(self.clear_pushButton)
        self.verticalLayout_2.addLayout(self.horizontalLayout_2)
        self.label_3.setBuddy(self.name_lineEdit)
        self.label.setBuddy(self.deg_spinBox)
        self.label_2.setBuddy(self.spinBox)

        self.retranslateUi(addLine)
        QtCore.QMetaObject.connectSlotsByName(addLine)

    def retranslateUi(self, addLine):
        addLine.setWindowTitle(_translate("addLine", "add_lines", None))
        item = self.tableWidget.horizontalHeaderItem(0)
        item.setText(_translate("addLine", "ID", None))
        item = self.tableWidget.horizontalHeaderItem(1)
        item.setText(_translate("addLine", "Z", None))
        item = self.tableWidget.horizontalHeaderItem(2)
        item.setText(_translate("addLine", "X", None))
        item = self.tableWidget.horizontalHeaderItem(3)
        item.setText(_translate("addLine", "Y", None))
        self.label_3.setText(_translate("addLine", "&Name:", None))
        self.label.setText(_translate("addLine", "&deg", None))
        self.interactive_checkBox.setText(_translate("addLine", "&interactive", None))
        self.label_2.setText(_translate("addLine", "n pts:", None))
        self.fit_pushButton.setText(_translate("addLine", "&fit", None))
        self.add_pushButton.setText(_translate("addLine", "&Add it!", None))
        self.closeButton.setText(_translate("addLine", "&Close", None))
        self.clear_pushButton.setText(_translate("addLine", "clear", None))

