# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './designerFiles/alert.ui'
#
# Created by: PyQt5 UI code generator 5.12.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_alertBox(object):
    def setupUi(self, alertBox):
        alertBox.setObjectName("alertBox")
        alertBox.resize(400, 250)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(alertBox.sizePolicy().hasHeightForWidth())
        alertBox.setSizePolicy(sizePolicy)
        alertBox.setMinimumSize(QtCore.QSize(400, 250))
        alertBox.setMaximumSize(QtCore.QSize(400, 250))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/icons/icons/emblem-important.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        alertBox.setWindowIcon(icon)
        self.closeButton = QtWidgets.QPushButton(alertBox)
        self.closeButton.setGeometry(QtCore.QRect(150, 210, 95, 24))
        self.closeButton.setObjectName("closeButton")
        self.frame = QtWidgets.QFrame(alertBox)
        self.frame.setGeometry(QtCore.QRect(30, 20, 341, 171))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame.sizePolicy().hasHeightForWidth())
        self.frame.setSizePolicy(sizePolicy)
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.label = QtWidgets.QLabel(self.frame)
        self.label.setGeometry(QtCore.QRect(10, 10, 321, 151))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.label.setFrameShadow(QtWidgets.QFrame.Plain)
        self.label.setText("")
        self.label.setScaledContents(False)
        self.label.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.label.setWordWrap(True)
        self.label.setOpenExternalLinks(True)
        self.label.setObjectName("label")

        self.retranslateUi(alertBox)
        QtCore.QMetaObject.connectSlotsByName(alertBox)

    def retranslateUi(self, alertBox):
        _translate = QtCore.QCoreApplication.translate
        alertBox.setWindowTitle(_translate("alertBox", "Lasagna Alert"))
        self.closeButton.setText(_translate("alertBox", "&Close"))


import mainWindow_rc
