# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'reorder_stack.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
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

class Ui_reorderStack(object):
    def setupUi(self, reorderStack):
        reorderStack.setObjectName(_fromUtf8("reorderStack"))
        reorderStack.resize(268, 300)
        self.verticalLayout_3 = QtGui.QVBoxLayout(reorderStack)
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.verticalLayout_2 = QtGui.QVBoxLayout()
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.label = QtGui.QLabel(reorderStack)
        self.label.setObjectName(_fromUtf8("label"))
        self.verticalLayout_2.addWidget(self.label)
        self.listWidget = QtGui.QListWidget(reorderStack)
        self.listWidget.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.listWidget.setObjectName(_fromUtf8("listWidget"))
        self.verticalLayout_2.addWidget(self.listWidget)
        self.horizontalLayout.addLayout(self.verticalLayout_2)
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.up_toolButton = QtGui.QToolButton(reorderStack)
        self.up_toolButton.setArrowType(QtCore.Qt.UpArrow)
        self.up_toolButton.setObjectName(_fromUtf8("up_toolButton"))
        self.verticalLayout.addWidget(self.up_toolButton)
        self.down_toolButton = QtGui.QToolButton(reorderStack)
        self.down_toolButton.setArrowType(QtCore.Qt.DownArrow)
        self.down_toolButton.setObjectName(_fromUtf8("down_toolButton"))
        self.verticalLayout.addWidget(self.down_toolButton)
        spacerItem1 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem1)
        self.update_checkBox = QtGui.QCheckBox(reorderStack)
        self.update_checkBox.setChecked(True)
        self.update_checkBox.setObjectName(_fromUtf8("update_checkBox"))
        self.verticalLayout.addWidget(self.update_checkBox)
        self.doit_pushButton = QtGui.QPushButton(reorderStack)
        self.doit_pushButton.setObjectName(_fromUtf8("doit_pushButton"))
        self.verticalLayout.addWidget(self.doit_pushButton)
        self.horizontalLayout.addLayout(self.verticalLayout)
        self.verticalLayout_3.addLayout(self.horizontalLayout)
        self.closeButton = QtGui.QPushButton(reorderStack)
        self.closeButton.setObjectName(_fromUtf8("closeButton"))
        self.verticalLayout_3.addWidget(self.closeButton)

        self.retranslateUi(reorderStack)
        QtCore.QMetaObject.connectSlotsByName(reorderStack)

    def retranslateUi(self, reorderStack):
        reorderStack.setWindowTitle(_translate("reorderStack", "reorder_stack", None))
        self.label.setText(_translate("reorderStack", "TextLabel", None))
        self.up_toolButton.setText(_translate("reorderStack", "...", None))
        self.down_toolButton.setText(_translate("reorderStack", "...", None))
        self.update_checkBox.setText(_translate("reorderStack", "update", None))
        self.doit_pushButton.setText(_translate("reorderStack", "do it!", None))
        self.closeButton.setText(_translate("reorderStack", "&Close", None))

