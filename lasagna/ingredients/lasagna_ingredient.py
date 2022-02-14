"""
lasagna.ingredients.lasagna_ingredient 

Each ingredient is a class which defines how lasagna displays and interacts with 
a particular sort of data. Things like images, data points, lines, polygons, 
areas, etc, etc. This superclass is inherited by ingredient files and helps 
define interactions between the data and Lasagna.
"""

import os
from PyQt5 import QtGui, QtCore


class lasagna_ingredient(object):
    def __init__(
        self,
        parent,
        data,
        fnameAbsPath="",
        enable=True,
        objectName="",
        pgObject="",
        pgObjectConstructionArgs=dict(),
    ):

        self.parent = parent
        self._data = data  # The raw data for this ingredient go here.

        self.objectName = (
            objectName
        )  # The name of the object TODO: decide exactly what this will be

        self.fnameAbsPath = fnameAbsPath  # Absolute path to file name

        # Item is plotted if enable is True. Hidden if enable is False
        self.enable = (enable)

        # The PyQtGraph item type which will display the data [see lasagna_axis.addItemToPlotWidget()]
        self.pgObject = (pgObject)
        self.pgObjectConstructionArgs = (
            pgObjectConstructionArgs
        )  # The pyqtgraph item is created with these arguments

        self.color = (
            None
        )  # The ingredient color (e.g. colour of the stack or lines or points)

    def fname(self):
        """ Strip the absolute path and return only the file name as as a string

            :return:
            file name without the absolute path
        """
        return self.fnameAbsPath.split(os.path.sep)[-1]

    def raw_data(self):
        """ return raw data

        """
        return self._data

    def addToPlots(self):
        """
        Show ingredient on plots by adding the plot item to all 2D axes so that it becomes available for plotting
        """
        [axis.addItemToPlotWidget(self) for axis in self.parent.axes2D]

    def removePlotItem(self):
        """
        Remove ingredient from plots by removing the plot item from all 2D axes so that it becomes unavailable for plotting
        """
        [axis.removeItemFromPlotWidget(self.objectName) for axis in self.parent.axes2D]

    def build_model_for_list(self, objectName):
        """
        Builds a QStandardItem and add it to self.modelItems so that it that 
        can be added to the list of ingredients.
        """

        # Add to the imageStackLayers_model which is associated with the points QTreeView
        itemName = QtGui.QStandardItem(objectName)

        # It's possible other code depends on the name staying the same so block the user from editing
        itemName.setEditable(False)

        # Add checkbox
        itemCheckBox = QtGui.QStandardItem()
        itemCheckBox.setFlags(
            QtCore.Qt.ItemIsEnabled
            | QtCore.Qt.ItemIsEditable
            | QtCore.Qt.ItemIsUserCheckable
        )
        itemCheckBox.setCheckState(QtCore.Qt.Checked)


        self.modelItems = itemName  # Run this instead
        #self.modelItems=(itemName,itemCheckBox) # FIXME: Remove this for now because I have NO CLUE how to get access to the checkbox state

    def addToList(self):
        """
        Add this ingredient's list items to the QStandardModel (model) associated with its QTreeView
        then highlight it when it's added.
        """
        self.setRowColor()
        self.model.appendRow(self.modelItems)
        self.model.parent().setCurrentIndex(
            self.modelItems.index()
        )  # Parent is, for example, a QTreeView

    def removeFromList(self):
        """
        Remove ingredient from the UI list with which it is associated  
        """
        items = self.model.findItems(self.objectName)
        self.model.removeRow(items[0].row())

    def setRowColor(self):
        """
        Set the color of this ingredient row based upon its stored color
        """

        if self.color is None or not hasattr(self, "modelItems"):
            return

        if not isinstance(self.color, list):
            print("** lasagna_ingredient -- can not set color")
            return

        # Set the text color
        basil = QtGui.QBrush()
        basil.setStyle(QtCore.Qt.BrushStyle(1))
        QC = QtGui.QColor(int(self.color[0]), int(self.color[1]), int(self.color[2]))
        basil.setColor(QC)

        # If the text is too light, we set the background to this color instead of the foreground
        HSL = QC.getHsl()

        if HSL[2] > 170:
            #Light background with dark text
            self.modelItems.setBackground(basil)
            basil = QtGui.QBrush()
            basil.setColor(QtGui.QColor(0,0,0))
            self.modelItems.setForeground(basil)
        else:
            # Colored text with white background
            self.modelItems.setForeground(basil)
            basil = QtGui.QBrush()
            basil.setColor(QtGui.QColor(255,255,255))
            self.modelItems.setBackground(basil)





