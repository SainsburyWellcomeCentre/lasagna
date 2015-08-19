# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ara_explorer.ui'
#
# Created: Wed Aug 19 11:50:06 2015
#      by: PyQt4 UI code generator 4.11.2
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

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

class Ui_ara_explorer(object):
    def setupUi(self, ara_explorer):
        ara_explorer.setObjectName(_fromUtf8("ara_explorer"))
        ara_explorer.resize(499, 254)
        self.load_frame = QtGui.QFrame(ara_explorer)
        self.load_frame.setGeometry(QtCore.QRect(10, 10, 421, 61))
        self.load_frame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.load_frame.setFrameShadow(QtGui.QFrame.Raised)
        self.load_frame.setObjectName(_fromUtf8("load_frame"))
        self.araName_comboBox = QtGui.QComboBox(self.load_frame)
        self.araName_comboBox.setGeometry(QtCore.QRect(10, 20, 271, 24))
        self.araName_comboBox.setObjectName(_fromUtf8("araName_comboBox"))
        self.load_pushButton = QtGui.QPushButton(self.load_frame)
        self.load_pushButton.setGeometry(QtCore.QRect(300, 20, 95, 24))
        self.load_pushButton.setObjectName(_fromUtf8("load_pushButton"))
        self.frame = QtGui.QFrame(ara_explorer)
        self.frame.setGeometry(QtCore.QRect(10, 80, 421, 80))
        self.frame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtGui.QFrame.Raised)
        self.frame.setObjectName(_fromUtf8("frame"))
        self.statusBarName_checkBox = QtGui.QCheckBox(self.frame)
        self.statusBarName_checkBox.setGeometry(QtCore.QRect(10, 10, 241, 21))
        self.statusBarName_checkBox.setChecked(True)
        self.statusBarName_checkBox.setObjectName(_fromUtf8("statusBarName_checkBox"))
        self.highlightArea_checkBox = QtGui.QCheckBox(self.frame)
        self.highlightArea_checkBox.setGeometry(QtCore.QRect(10, 30, 241, 21))
        self.highlightArea_checkBox.setChecked(True)
        self.highlightArea_checkBox.setObjectName(_fromUtf8("highlightArea_checkBox"))

        self.retranslateUi(ara_explorer)
        QtCore.QMetaObject.connectSlotsByName(ara_explorer)

    def retranslateUi(self, ara_explorer):
        ara_explorer.setWindowTitle(_translate("ara_explorer", "Form", None))
        self.load_pushButton.setText(_translate("ara_explorer", "Load", None))
        self.statusBarName_checkBox.setText(_translate("ara_explorer", "show name in status bar", None))
        self.highlightArea_checkBox.setText(_translate("ara_explorer", "highlight area", None))

