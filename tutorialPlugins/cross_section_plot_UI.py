# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'cross_section_plot.ui'
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

class Ui_xSection(object):
    def setupUi(self, xSection):
        xSection.setObjectName(_fromUtf8("xSection"))
        xSection.resize(400, 300)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(xSection.sizePolicy().hasHeightForWidth())
        xSection.setSizePolicy(sizePolicy)
        xSection.setMinimumSize(QtCore.QSize(400, 300))
        xSection.setMaximumSize(QtCore.QSize(400, 300))
        self.closeButton = QtGui.QPushButton(xSection)
        self.closeButton.setGeometry(QtCore.QRect(160, 270, 95, 24))
        self.closeButton.setObjectName(_fromUtf8("closeButton"))
        self.graphicsView = PlotWidget(xSection)
        self.graphicsView.setGeometry(QtCore.QRect(15, 11, 371, 251))
        self.graphicsView.setObjectName(_fromUtf8("graphicsView"))

        self.retranslateUi(xSection)
        QtCore.QMetaObject.connectSlotsByName(xSection)

    def retranslateUi(self, xSection):
        xSection.setWindowTitle(_translate("xSection", "cross section", None))
        self.closeButton.setText(_translate("xSection", "&Close", None))

from pyqtgraph import PlotWidget
