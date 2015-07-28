# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'infoBox.ui'
#
# Created: Tue Jul 21 12:33:59 2015
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

class Ui_infoBox(object):
    def setupUi(self, infoBox):
        infoBox.setObjectName(_fromUtf8("infoBox"))
        infoBox.resize(400, 150)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(infoBox.sizePolicy().hasHeightForWidth())
        infoBox.setSizePolicy(sizePolicy)
        infoBox.setMinimumSize(QtCore.QSize(400, 150))
        infoBox.setMaximumSize(QtCore.QSize(400, 150))
        self.closeButton = QtGui.QPushButton(infoBox)
        self.closeButton.setGeometry(QtCore.QRect(160, 110, 95, 24))
        self.closeButton.setObjectName(_fromUtf8("closeButton"))
        self.frame = QtGui.QFrame(infoBox)
        self.frame.setGeometry(QtCore.QRect(40, 20, 321, 71))
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame.sizePolicy().hasHeightForWidth())
        self.frame.setSizePolicy(sizePolicy)
        self.frame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtGui.QFrame.Raised)
        self.frame.setObjectName(_fromUtf8("frame"))
        self.label = QtGui.QLabel(self.frame)
        self.label.setGeometry(QtCore.QRect(10, 10, 301, 51))
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setFrameShape(QtGui.QFrame.NoFrame)
        self.label.setFrameShadow(QtGui.QFrame.Plain)
        self.label.setText(_fromUtf8(""))
        self.label.setScaledContents(False)
        self.label.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.label.setObjectName(_fromUtf8("label"))

        self.retranslateUi(infoBox)
        QtCore.QMetaObject.connectSlotsByName(infoBox)

    def retranslateUi(self, infoBox):
        infoBox.setWindowTitle(_translate("infoBox", "Info Box", None))
        self.closeButton.setText(_translate("infoBox", "&Close", None))

