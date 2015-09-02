# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'area_namer.ui'
#
# Created: Wed Sep  2 16:05:04 2015
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

class Ui_area_namer(object):
    def setupUi(self, area_namer):
        area_namer.setObjectName(_fromUtf8("area_namer"))
        area_namer.resize(443, 200)
        area_namer.setMinimumSize(QtCore.QSize(443, 200))
        self.load_frame = QtGui.QFrame(area_namer)
        self.load_frame.setGeometry(QtCore.QRect(0, 10, 435, 101))
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.load_frame.sizePolicy().hasHeightForWidth())
        self.load_frame.setSizePolicy(sizePolicy)
        self.load_frame.setMinimumSize(QtCore.QSize(0, 61))
        self.load_frame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.load_frame.setFrameShadow(QtGui.QFrame.Raised)
        self.load_frame.setObjectName(_fromUtf8("load_frame"))
        self.araName_comboBox = QtGui.QComboBox(self.load_frame)
        self.araName_comboBox.setGeometry(QtCore.QRect(10, 20, 411, 24))
        self.araName_comboBox.setObjectName(_fromUtf8("araName_comboBox"))
        self.loadOrig_pushButton = QtGui.QPushButton(self.load_frame)
        self.loadOrig_pushButton.setGeometry(QtCore.QRect(10, 50, 191, 24))
        self.loadOrig_pushButton.setObjectName(_fromUtf8("loadOrig_pushButton"))
        self.loadOther_pushButton = QtGui.QPushButton(self.load_frame)
        self.loadOther_pushButton.setGeometry(QtCore.QRect(230, 50, 191, 24))
        self.loadOther_pushButton.setObjectName(_fromUtf8("loadOther_pushButton"))
        self.frame = QtGui.QFrame(area_namer)
        self.frame.setGeometry(QtCore.QRect(0, 110, 435, 80))
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame.sizePolicy().hasHeightForWidth())
        self.frame.setSizePolicy(sizePolicy)
        self.frame.setMinimumSize(QtCore.QSize(0, 80))
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
        self.overlayTemplate_checkBox = QtGui.QCheckBox(self.frame)
        self.overlayTemplate_checkBox.setEnabled(False)
        self.overlayTemplate_checkBox.setGeometry(QtCore.QRect(220, 10, 181, 21))
        self.overlayTemplate_checkBox.setChecked(False)
        self.overlayTemplate_checkBox.setObjectName(_fromUtf8("overlayTemplate_checkBox"))

        self.retranslateUi(area_namer)
        QtCore.QMetaObject.connectSlotsByName(area_namer)

    def retranslateUi(self, area_namer):
        area_namer.setWindowTitle(_translate("area_namer", "Form", None))
        self.loadOrig_pushButton.setText(_translate("area_namer", "Attach original atlas", None))
        self.loadOther_pushButton.setText(_translate("area_namer", "Attach warped atlas", None))
        self.statusBarName_checkBox.setText(_translate("area_namer", "show name in status bar", None))
        self.highlightArea_checkBox.setText(_translate("area_namer", "highlight area", None))
        self.overlayTemplate_checkBox.setText(_translate("area_namer", "overlay template", None))

