# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'transformix_plugin.ui'
#
# Created: Sat Sep  5 12:22:26 2015
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

class Ui_transformix_plugin(object):
    def setupUi(self, transformix_plugin):
        transformix_plugin.setObjectName(_fromUtf8("transformix_plugin"))
        transformix_plugin.resize(819, 269)
        transformix_plugin.setMinimumSize(QtCore.QSize(819, 269))
        transformix_plugin.setMaximumSize(QtCore.QSize(819, 269))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/icons/elastix_logo_48.gif")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        transformix_plugin.setWindowIcon(icon)
        self.frameCommand = QtGui.QFrame(transformix_plugin)
        self.frameCommand.setGeometry(QtCore.QRect(10, 120, 801, 101))
        self.frameCommand.setFrameShape(QtGui.QFrame.Box)
        self.frameCommand.setFrameShadow(QtGui.QFrame.Raised)
        self.frameCommand.setObjectName(_fromUtf8("frameCommand"))
        self.commandText_label = QtGui.QLabel(self.frameCommand)
        self.commandText_label.setGeometry(QtCore.QRect(10, 20, 781, 71))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Courier"))
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.commandText_label.setFont(font)
        self.commandText_label.setText(_fromUtf8(""))
        self.commandText_label.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.commandText_label.setWordWrap(True)
        self.commandText_label.setObjectName(_fromUtf8("commandText_label"))
        self.labelCommand = QtGui.QLabel(self.frameCommand)
        self.labelCommand.setGeometry(QtCore.QRect(10, 0, 80, 20))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.labelCommand.setFont(font)
        self.labelCommand.setObjectName(_fromUtf8("labelCommand"))
        self.layoutWidget = QtGui.QWidget(transformix_plugin)
        self.layoutWidget.setGeometry(QtCore.QRect(10, 20, 801, 26))
        self.layoutWidget.setObjectName(_fromUtf8("layoutWidget"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.layoutWidget)
        self.horizontalLayout.setMargin(0)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.loadStack_pushButton = QtGui.QPushButton(self.layoutWidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.loadStack_pushButton.sizePolicy().hasHeightForWidth())
        self.loadStack_pushButton.setSizePolicy(sizePolicy)
        self.loadStack_pushButton.setMinimumSize(QtCore.QSize(180, 0))
        self.loadStack_pushButton.setObjectName(_fromUtf8("loadStack_pushButton"))
        self.horizontalLayout.addWidget(self.loadStack_pushButton)
        self.stackName_label = QtGui.QLabel(self.layoutWidget)
        self.stackName_label.setMinimumSize(QtCore.QSize(250, 0))
        self.stackName_label.setText(_fromUtf8(""))
        self.stackName_label.setObjectName(_fromUtf8("stackName_label"))
        self.horizontalLayout.addWidget(self.stackName_label)
        spacerItem = QtGui.QSpacerItem(318, 17, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.layoutWidget_2 = QtGui.QWidget(transformix_plugin)
        self.layoutWidget_2.setGeometry(QtCore.QRect(10, 50, 801, 26))
        self.layoutWidget_2.setObjectName(_fromUtf8("layoutWidget_2"))
        self.horizontalLayout_2 = QtGui.QHBoxLayout(self.layoutWidget_2)
        self.horizontalLayout_2.setMargin(0)
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.loadTransform_pushButton = QtGui.QPushButton(self.layoutWidget_2)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.loadTransform_pushButton.sizePolicy().hasHeightForWidth())
        self.loadTransform_pushButton.setSizePolicy(sizePolicy)
        self.loadTransform_pushButton.setMinimumSize(QtCore.QSize(180, 0))
        self.loadTransform_pushButton.setObjectName(_fromUtf8("loadTransform_pushButton"))
        self.horizontalLayout_2.addWidget(self.loadTransform_pushButton)
        self.transformName_label = QtGui.QLabel(self.layoutWidget_2)
        self.transformName_label.setMinimumSize(QtCore.QSize(250, 0))
        self.transformName_label.setText(_fromUtf8(""))
        self.transformName_label.setObjectName(_fromUtf8("transformName_label"))
        self.horizontalLayout_2.addWidget(self.transformName_label)
        spacerItem1 = QtGui.QSpacerItem(318, 17, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem1)
        self.frame_2 = QtGui.QFrame(transformix_plugin)
        self.frame_2.setGeometry(QtCore.QRect(70, 80, 741, 31))
        self.frame_2.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QtGui.QFrame.Raised)
        self.frame_2.setObjectName(_fromUtf8("frame_2"))
        self.outputDir_label = QtGui.QLabel(self.frame_2)
        self.outputDir_label.setGeometry(QtCore.QRect(10, 4, 721, 21))
        self.outputDir_label.setText(_fromUtf8(""))
        self.outputDir_label.setObjectName(_fromUtf8("outputDir_label"))
        self.outputDirSelect_button = QtGui.QPushButton(transformix_plugin)
        self.outputDirSelect_button.setGeometry(QtCore.QRect(10, 80, 61, 31))
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.outputDirSelect_button.sizePolicy().hasHeightForWidth())
        self.outputDirSelect_button.setSizePolicy(sizePolicy)
        self.outputDirSelect_button.setMinimumSize(QtCore.QSize(0, 0))
        self.outputDirSelect_button.setObjectName(_fromUtf8("outputDirSelect_button"))
        self.run_pushButton = QtGui.QPushButton(transformix_plugin)
        self.run_pushButton.setGeometry(QtCore.QRect(10, 230, 180, 24))
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.run_pushButton.sizePolicy().hasHeightForWidth())
        self.run_pushButton.setSizePolicy(sizePolicy)
        self.run_pushButton.setMinimumSize(QtCore.QSize(180, 0))
        self.run_pushButton.setObjectName(_fromUtf8("run_pushButton"))
        self.loadResult_pushButton = QtGui.QPushButton(transformix_plugin)
        self.loadResult_pushButton.setGeometry(QtCore.QRect(220, 230, 180, 24))
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.loadResult_pushButton.sizePolicy().hasHeightForWidth())
        self.loadResult_pushButton.setSizePolicy(sizePolicy)
        self.loadResult_pushButton.setMinimumSize(QtCore.QSize(180, 0))
        self.loadResult_pushButton.setObjectName(_fromUtf8("loadResult_pushButton"))

        self.retranslateUi(transformix_plugin)
        QtCore.QMetaObject.connectSlotsByName(transformix_plugin)

    def retranslateUi(self, transformix_plugin):
        transformix_plugin.setWindowTitle(_translate("transformix_plugin", "Form", None))
        self.labelCommand.setText(_translate("transformix_plugin", "Command", None))
        self.loadStack_pushButton.setText(_translate("transformix_plugin", "Load Stack", None))
        self.loadTransform_pushButton.setText(_translate("transformix_plugin", "Load Transform", None))
        self.outputDirSelect_button.setText(_translate("transformix_plugin", "Dir", None))
        self.run_pushButton.setText(_translate("transformix_plugin", "Run", None))
        self.loadResult_pushButton.setText(_translate("transformix_plugin", "Load result stack", None))

import elastix_plugin_rc
