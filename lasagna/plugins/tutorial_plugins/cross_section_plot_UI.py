# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'cross_section_plot.ui'
#
# Created by: PyQt5 UI code generator 5.5.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_xSection(object):
    def setupUi(self, xSection):
        xSection.setObjectName("xSection")
        xSection.resize(400, 300)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(xSection.sizePolicy().hasHeightForWidth())
        xSection.setSizePolicy(sizePolicy)
        xSection.setMinimumSize(QtCore.QSize(400, 300))
        xSection.setMaximumSize(QtCore.QSize(400, 300))
        self.closeButton = QtWidgets.QPushButton(xSection)
        self.closeButton.setGeometry(QtCore.QRect(160, 270, 95, 24))
        self.closeButton.setObjectName("closeButton")
        self.graphicsView = PlotWidget(xSection)
        self.graphicsView.setGeometry(QtCore.QRect(15, 11, 371, 251))
        self.graphicsView.setObjectName("graphicsView")

        self.retranslateUi(xSection)
        QtCore.QMetaObject.connectSlotsByName(xSection)

    def retranslateUi(self, xSection):
        _translate = QtCore.QCoreApplication.translate
        xSection.setWindowTitle(_translate("xSection", "cross section"))
        self.closeButton.setText(_translate("xSection", "&Close"))

from pyqtgraph import PlotWidget
