# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'selectstack.ui'
#
# Created by: PyQt5 UI code generator 5.7.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_selectStack(object):
    def setupUi(self, selectStack):
        selectStack.setObjectName("selectStack")
        selectStack.resize(248, 300)
        self.verticalLayout = QtWidgets.QVBoxLayout(selectStack)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtWidgets.QLabel(selectStack)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.listWidget = QtWidgets.QListWidget(selectStack)
        self.listWidget.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.listWidget.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.listWidget.setObjectName("listWidget")
        self.verticalLayout.addWidget(self.listWidget)
        self.buttonBox = QtWidgets.QDialogButtonBox(selectStack)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(selectStack)
        self.buttonBox.accepted.connect(selectStack.accept)
        self.buttonBox.rejected.connect(selectStack.reject)
        QtCore.QMetaObject.connectSlotsByName(selectStack)

    def retranslateUi(self, selectStack):
        _translate = QtCore.QCoreApplication.translate
        selectStack.setWindowTitle(_translate("selectStack", "Select stack"))
        self.label.setText(_translate("selectStack", "Select stack to change"))

