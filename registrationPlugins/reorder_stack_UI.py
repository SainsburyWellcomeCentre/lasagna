# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'reorder_stack.ui'
#
# Created by: PyQt5 UI code generator 5.7.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_reorderStack(object):
    def setupUi(self, reorderStack):
        reorderStack.setObjectName("reorderStack")
        reorderStack.resize(268, 300)
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(reorderStack)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.label = QtWidgets.QLabel(reorderStack)
        self.label.setObjectName("label")
        self.verticalLayout_2.addWidget(self.label)
        self.listWidget = QtWidgets.QListWidget(reorderStack)
        self.listWidget.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.listWidget.setObjectName("listWidget")
        self.verticalLayout_2.addWidget(self.listWidget)
        self.horizontalLayout.addLayout(self.verticalLayout_2)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.up_toolButton = QtWidgets.QToolButton(reorderStack)
        self.up_toolButton.setArrowType(QtCore.Qt.UpArrow)
        self.up_toolButton.setObjectName("up_toolButton")
        self.verticalLayout.addWidget(self.up_toolButton)
        self.down_toolButton = QtWidgets.QToolButton(reorderStack)
        self.down_toolButton.setArrowType(QtCore.Qt.DownArrow)
        self.down_toolButton.setObjectName("down_toolButton")
        self.verticalLayout.addWidget(self.down_toolButton)
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem1)
        self.update_checkBox = QtWidgets.QCheckBox(reorderStack)
        self.update_checkBox.setChecked(True)
        self.update_checkBox.setObjectName("update_checkBox")
        self.verticalLayout.addWidget(self.update_checkBox)
        self.doit_pushButton = QtWidgets.QPushButton(reorderStack)
        self.doit_pushButton.setObjectName("doit_pushButton")
        self.verticalLayout.addWidget(self.doit_pushButton)
        self.horizontalLayout.addLayout(self.verticalLayout)
        self.verticalLayout_3.addLayout(self.horizontalLayout)
        self.closeButton = QtWidgets.QPushButton(reorderStack)
        self.closeButton.setObjectName("closeButton")
        self.verticalLayout_3.addWidget(self.closeButton)

        self.retranslateUi(reorderStack)
        QtCore.QMetaObject.connectSlotsByName(reorderStack)

    def retranslateUi(self, reorderStack):
        _translate = QtCore.QCoreApplication.translate
        reorderStack.setWindowTitle(_translate("reorderStack", "reorder_stack"))
        self.label.setText(_translate("reorderStack", "TextLabel"))
        self.up_toolButton.setText(_translate("reorderStack", "..."))
        self.down_toolButton.setText(_translate("reorderStack", "..."))
        self.update_checkBox.setText(_translate("reorderStack", "update"))
        self.doit_pushButton.setText(_translate("reorderStack", "do it!"))
        self.closeButton.setText(_translate("reorderStack", "&Close"))

