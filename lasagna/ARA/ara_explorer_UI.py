# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ara_explorer.ui'
#
# Created by: PyQt5 UI code generator 5.5.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_ara_explorer(object):
    def setupUi(self, ara_explorer):
        ara_explorer.setObjectName("ara_explorer")
        ara_explorer.resize(443, 574)
        ara_explorer.setMinimumSize(QtCore.QSize(443, 500))
        self.verticalLayout = QtWidgets.QVBoxLayout(ara_explorer)
        self.verticalLayout.setObjectName("verticalLayout")
        self.load_frame = QtWidgets.QFrame(ara_explorer)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.load_frame.sizePolicy().hasHeightForWidth())
        self.load_frame.setSizePolicy(sizePolicy)
        self.load_frame.setMinimumSize(QtCore.QSize(0, 61))
        self.load_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.load_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.load_frame.setObjectName("load_frame")
        self.araName_comboBox = QtWidgets.QComboBox(self.load_frame)
        self.araName_comboBox.setGeometry(QtCore.QRect(10, 20, 271, 24))
        self.araName_comboBox.setObjectName("araName_comboBox")
        self.load_pushButton = QtWidgets.QPushButton(self.load_frame)
        self.load_pushButton.setGeometry(QtCore.QRect(300, 20, 95, 24))
        self.load_pushButton.setObjectName("load_pushButton")
        self.verticalLayout.addWidget(self.load_frame)
        self.frame = QtWidgets.QFrame(ara_explorer)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame.sizePolicy().hasHeightForWidth())
        self.frame.setSizePolicy(sizePolicy)
        self.frame.setMinimumSize(QtCore.QSize(0, 80))
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.statusBarName_checkBox = QtWidgets.QCheckBox(self.frame)
        self.statusBarName_checkBox.setGeometry(QtCore.QRect(10, 10, 241, 21))
        self.statusBarName_checkBox.setChecked(True)
        self.statusBarName_checkBox.setObjectName("statusBarName_checkBox")
        self.highlightArea_checkBox = QtWidgets.QCheckBox(self.frame)
        self.highlightArea_checkBox.setGeometry(QtCore.QRect(10, 30, 241, 21))
        self.highlightArea_checkBox.setChecked(True)
        self.highlightArea_checkBox.setObjectName("highlightArea_checkBox")
        self.overlayTemplate_checkBox = QtWidgets.QCheckBox(self.frame)
        self.overlayTemplate_checkBox.setEnabled(False)
        self.overlayTemplate_checkBox.setGeometry(QtCore.QRect(10, 50, 241, 21))
        self.overlayTemplate_checkBox.setChecked(False)
        self.overlayTemplate_checkBox.setObjectName("overlayTemplate_checkBox")
        self.verticalLayout.addWidget(self.frame)
        self.brainArea_treeView = QtWidgets.QTreeView(ara_explorer)
        self.brainArea_treeView.setObjectName("brainArea_treeView")
        self.verticalLayout.addWidget(self.brainArea_treeView)

        self.retranslateUi(ara_explorer)
        QtCore.QMetaObject.connectSlotsByName(ara_explorer)

    def retranslateUi(self, ara_explorer):
        _translate = QtCore.QCoreApplication.translate
        ara_explorer.setWindowTitle(_translate("ara_explorer", "Form"))
        self.load_pushButton.setText(_translate("ara_explorer", "Load"))
        self.statusBarName_checkBox.setText(_translate("ara_explorer", "show name in status bar"))
        self.highlightArea_checkBox.setText(_translate("ara_explorer", "highlight area"))
        self.overlayTemplate_checkBox.setText(_translate("ara_explorer", "overlay template"))

