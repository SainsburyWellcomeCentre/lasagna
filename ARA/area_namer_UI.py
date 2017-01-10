# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'area_namer.ui'
#
# Created by: PyQt5 UI code generator 5.5.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_area_namer(object):
    def setupUi(self, area_namer):
        area_namer.setObjectName("area_namer")
        area_namer.resize(443, 200)
        area_namer.setMinimumSize(QtCore.QSize(443, 200))
        self.load_frame = QtWidgets.QFrame(area_namer)
        self.load_frame.setGeometry(QtCore.QRect(0, 10, 435, 101))
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
        self.araName_comboBox.setGeometry(QtCore.QRect(10, 20, 411, 24))
        self.araName_comboBox.setObjectName("araName_comboBox")
        self.loadOrig_pushButton = QtWidgets.QPushButton(self.load_frame)
        self.loadOrig_pushButton.setGeometry(QtCore.QRect(10, 50, 191, 24))
        self.loadOrig_pushButton.setObjectName("loadOrig_pushButton")
        self.loadOther_pushButton = QtWidgets.QPushButton(self.load_frame)
        self.loadOther_pushButton.setGeometry(QtCore.QRect(230, 50, 191, 24))
        self.loadOther_pushButton.setObjectName("loadOther_pushButton")
        self.frame = QtWidgets.QFrame(area_namer)
        self.frame.setGeometry(QtCore.QRect(0, 110, 435, 80))
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

        self.retranslateUi(area_namer)
        QtCore.QMetaObject.connectSlotsByName(area_namer)

    def retranslateUi(self, area_namer):
        _translate = QtCore.QCoreApplication.translate
        area_namer.setWindowTitle(_translate("area_namer", "Form"))
        self.loadOrig_pushButton.setText(_translate("area_namer", "Attach original atlas"))
        self.loadOther_pushButton.setText(_translate("area_namer", "Attach warped atlas"))
        self.statusBarName_checkBox.setText(_translate("area_namer", "show name in status bar"))
        self.highlightArea_checkBox.setText(_translate("area_namer", "highlight area"))

