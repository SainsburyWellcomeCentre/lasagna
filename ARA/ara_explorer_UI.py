# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ara_explorer.ui'
#
# Created: Wed Aug 19 16:25:45 2015
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
        ara_explorer.resize(443, 574)
        ara_explorer.setMinimumSize(QtCore.QSize(443, 500))
        self.verticalLayout = QtGui.QVBoxLayout(ara_explorer)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.load_frame = QtGui.QFrame(ara_explorer)
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
        self.araName_comboBox.setGeometry(QtCore.QRect(10, 20, 271, 24))
        self.araName_comboBox.setObjectName(_fromUtf8("araName_comboBox"))
        self.load_pushButton = QtGui.QPushButton(self.load_frame)
        self.load_pushButton.setGeometry(QtCore.QRect(300, 20, 95, 24))
        self.load_pushButton.setObjectName(_fromUtf8("load_pushButton"))
        self.verticalLayout.addWidget(self.load_frame)
        self.frame = QtGui.QFrame(ara_explorer)
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
        self.overlayTemplate_checkBox.setGeometry(QtCore.QRect(10, 50, 241, 21))
        self.overlayTemplate_checkBox.setChecked(False)
        self.overlayTemplate_checkBox.setObjectName(_fromUtf8("overlayTemplate_checkBox"))
        self.verticalLayout.addWidget(self.frame)
        self.brainArea_treeView = QtGui.QTreeView(ara_explorer)
        self.brainArea_treeView.setObjectName(_fromUtf8("brainArea_treeView"))
        self.verticalLayout.addWidget(self.brainArea_treeView)

        self.retranslateUi(ara_explorer)
        QtCore.QMetaObject.connectSlotsByName(ara_explorer)

    def retranslateUi(self, ara_explorer):
        ara_explorer.setWindowTitle(_translate("ara_explorer", "Form", None))
        self.load_pushButton.setText(_translate("ara_explorer", "Load", None))
        self.statusBarName_checkBox.setText(_translate("ara_explorer", "show name in status bar", None))
        self.highlightArea_checkBox.setText(_translate("ara_explorer", "highlight area", None))
        self.overlayTemplate_checkBox.setText(_translate("ara_explorer", "overlay template", None))

