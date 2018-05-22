"""
Ingredients inherit this class
"""

import os
import pyqtgraph as pg
from PyQt5 import QtGui, QtCore


class lasagna_ingredient(object):
    def __init__(self, parent, data, fnameAbsPath='', enable=True, objectName='', pgObject='', pgObjectConstructionArgs=dict()):

        self.parent = parent
        self._data = data                   # The raw data for this ingredient go here.

        self.objectName = objectName        # The name of the object TODO: decide exactly what this will be

        self.fnameAbsPath = fnameAbsPath    # Absolute path to file name

        self.enable = enable                # Item is plotted if enable is True. Hidden if enable is False
        self.pgObject = pgObject            # The PyQtGraph item type which will display the data [see lasagna_axis.addItemToPlotWidget()]
        self.pgObjectConstructionArgs = pgObjectConstructionArgs  # The pyqtgraph item is created with these arguments

        self.color = None                   # The ingredient color (e.g. colour of the stack or lines or points)

    def fname(self):
        """
        Strip the absolute path and return only the file name as as a string
        """
        return self.fnameAbsPath.split(os.path.sep)[-1]

    def raw_data(self):
        """
        return raw data
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

    def addToList(self):
        """
        Add this ingredient's list items to the QStandardModel (model) associated with its QTreeView
        then highlight it when it's added.
        """
        self.setRowColor()
        self.model.appendRow(self.modelItems)
        self.model.parent().setCurrentIndex(self.modelItems.index())  # Parent is, for example, a QTreeView

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

        if self.color is None or not hasattr(self, 'modelItems'):
            return

        if not isinstance(self.color, list):
            print("** lasagna_ingredient -- can not set color")
            return

        basil = QtGui.QBrush()
        basil.setColor(QtGui.QColor(self.color[0], self.color[1], self.color[2]))
        basil.setStyle(QtCore.Qt.BrushStyle(1))

        self.modelItems.setBackground(basil)
