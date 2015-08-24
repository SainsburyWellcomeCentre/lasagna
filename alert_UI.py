# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './designerFiles/alert.ui'
#
# Created: Mon Aug 24 17:42:15 2015
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

class Ui_alertBox(object):
    def setupUi(self, alertBox):
        alertBox.setObjectName(_fromUtf8("alertBox"))
        alertBox.resize(400, 250)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(alertBox.sizePolicy().hasHeightForWidth())
        alertBox.setSizePolicy(sizePolicy)
        alertBox.setMinimumSize(QtCore.QSize(400, 250))
        alertBox.setMaximumSize(QtCore.QSize(400, 250))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/icons/emblem-important.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        alertBox.setWindowIcon(icon)
        self.closeButton = QtGui.QPushButton(alertBox)
        self.closeButton.setGeometry(QtCore.QRect(150, 210, 95, 24))
        self.closeButton.setObjectName(_fromUtf8("closeButton"))
        self.frame = QtGui.QFrame(alertBox)
        self.frame.setGeometry(QtCore.QRect(30, 20, 341, 171))
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame.sizePolicy().hasHeightForWidth())
        self.frame.setSizePolicy(sizePolicy)
        self.frame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtGui.QFrame.Raised)
        self.frame.setObjectName(_fromUtf8("frame"))
        self.label = QtGui.QLabel(self.frame)
        self.label.setGeometry(QtCore.QRect(10, 10, 321, 151))
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
        self.label.setWordWrap(True)
        self.label.setOpenExternalLinks(True)
        self.label.setObjectName(_fromUtf8("label"))

        self.retranslateUi(alertBox)
        QtCore.QMetaObject.connectSlotsByName(alertBox)

    def retranslateUi(self, alertBox):
        alertBox.setWindowTitle(_translate("alertBox", "Lasagna Alert", None))
        self.closeButton.setText(_translate("alertBox", "&Close", None))

import mainWindow_rc
