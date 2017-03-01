# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'infoBox.ui'
#
# Created by: PyQt5 UI code generator 5.5.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_infoBox(object):
    def setupUi(self, infoBox):
        infoBox.setObjectName("infoBox")
        infoBox.resize(400, 150)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(infoBox.sizePolicy().hasHeightForWidth())
        infoBox.setSizePolicy(sizePolicy)
        infoBox.setMinimumSize(QtCore.QSize(400, 150))
        infoBox.setMaximumSize(QtCore.QSize(400, 150))
        self.closeButton = QtWidgets.QPushButton(infoBox)
        self.closeButton.setGeometry(QtCore.QRect(160, 110, 95, 24))
        self.closeButton.setObjectName("closeButton")
        self.frame = QtWidgets.QFrame(infoBox)
        self.frame.setGeometry(QtCore.QRect(40, 20, 321, 71))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame.sizePolicy().hasHeightForWidth())
        self.frame.setSizePolicy(sizePolicy)
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.label = QtWidgets.QLabel(self.frame)
        self.label.setGeometry(QtCore.QRect(10, 10, 301, 51))
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
        self.label.setObjectName("label")

        self.retranslateUi(infoBox)
        QtCore.QMetaObject.connectSlotsByName(infoBox)

    def retranslateUi(self, infoBox):
        _translate = QtCore.QCoreApplication.translate
        infoBox.setWindowTitle(_translate("infoBox", "Info Box"))
        self.closeButton.setText(_translate("infoBox", "&Close"))

