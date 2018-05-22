"""
This class overlays lines on top of the image stacks. 
This class loads csv files with columns in the format:
line series, z, x, y

line series is a scalar. All points within the same line series
are joined by lines. Different line series are not joined but all
line series from the same CSV file are part of the same ingredient
(and the same plot item) and are rendered with the same colours, etc. 

Instances of lines are created by line_reader_plugin. It is 
line_reader_plugin that creates the menu entry in the file menu, 
loads the data from the csv file, and calles lines.py 
"""

import warnings  # to disable some annoying NaN-related warnings

import numpy as np
from matplotlib import cm
from numpy import linspace

from PyQt5 import QtGui, QtCore
import pyqtgraph as pg

from lasagna import lasagna_helperFunctions as las_help
from lasagna.lasagna_ingredient import lasagna_ingredient


class lines(lasagna_ingredient):
    def __init__(self, parent=None, data=None, fnameAbsPath='', enable=True, objectName=''):
        super(lines, self).__init__(parent, data, fnameAbsPath, enable, objectName,
                                    pgObject='PlotCurveItem'
                                    )

        # Choose symbols from preferences file.
        # TODO: read symbols from GUI
        self.symbol = las_help.readPreference('symbolOrder')[0]
        self.symbolSize = int(self.parent.markerSize_spinBox.value())
        self.alpha = int(self.parent.markerAlpha_spinBox.value())
        self.lineWidth = int(self.parent.lineWidth_spinBox.value())

        # Add to the imageStackLayers_model which is associated with the points QTreeView
        name = QtGui.QStandardItem(objectName)
        name.setEditable(False)

        # Add checkbox
        thing = QtGui.QStandardItem()
        thing.setFlags(QtCore.Qt.ItemIsEnabled  | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsUserCheckable)
        thing.setCheckState(QtCore.Qt.Checked)

        # self.modelItems=(name,thing) #Remove this for now because I have NO CLUE how to get access to the checkbox state
        self.modelItems=name
        self.model = self.parent.points_Model

        self.addToList()

        # Set the colour of the object based on how many items are already present
        number_of_colors = 6
        this_number = (self.parent.points_Model.rowCount() - 1) % number_of_colors  # FIXME: rename
        cm_subsection = linspace(0, 1, number_of_colors)
        colors = [cm.jet(x) for x in cm_subsection]
        color = colors[this_number]
        self.color = [color[0]*255, color[1]*255, color[2]*255]

    def data(self, axisToPlot=0):
        """
        lines data are an n by 3 array where each row defines the location
        of a single point in x, y, and z
        """
        if not self._data.size:
            return False

        data = np.delete(self._data, axisToPlot, 1)
        if axisToPlot == 2:
            data = np.fliplr(data)

        return data

    def plotIngredient(self, pyqtObject, axisToPlot=0, sliceToPlot=0):
        """
        Plots the ingredient onto pyqtObject along axisAxisToPlot,
        onto the object with which it is associated
        """
        if not pyqtObject:
            print("lines.py not proceeding because pyqtObject is false")             
            return

        # check if there are data on the plot. Use `is False` because np.array == False returns an array
        if self.data() is False or len(self.data()) == 0:
            pyqtObject.setData([], [])  # make sure there are no data left on the plot
            return

        # Ensure our z dimension is a whole number
        z = np.round(self._data[:, axisToPlot])

        data = self.data(axisToPlot)

        # Find points within this z-plane +/- a certain region
        z_range = self.parent.viewZ_spinBoxes[axisToPlot].value()-1
        from_layer = sliceToPlot-z_range
        to_layer = sliceToPlot+z_range

        # Now filter the data list by this Z range. Points that will not be plotted are replaced with nan
        warnings.simplefilter(action="ignore", category=RuntimeWarning)  # To block weird run-time warnings that aren't of interest produced by the following two lines  # FIXME: use context manager
        data[z < from_layer, :] = np.nan
        data[z > to_layer, :] = np.nan

        # If we have only NaNs we should not plot.
        if not np.all(np.isnan(data)):
            pyqtObject.setData(x=data[:, 0], y=data[:, 1],
                               pen=pg.mkPen(color=self.symbolBrush(), width=self.lineWidth),
                               antialias=True,
                               connect="finite")
            pyqtObject.setVisible(True)
        else:
            pyqtObject.setVisible(False)

    def addToList(self):
        """
        Add to list and then set UI elements
        """
        super(lines, self).addToList()
        self.parent.markerSize_spinBox.setValue(self.symbolSize)
        self.parent.markerAlpha_spinBox.setValue(self.alpha)

    def symbolBrush(self):
        if isinstance(self.color, list):
            return tuple(self.color + [self.alpha])
        else:
            print(("lines.color can not cope with type " + str(type(self.color))))

    # ---------------------------------------------------------------
    # Getters and setters
    def get_symbolSize(self):
        return self._symbolSize

    def set_symbolSize(self, symbolSize):
        self._symbolSize = symbolSize
    symbolSize = property(get_symbolSize, set_symbolSize)

    def get_symbol(self):
        return self._symbol

    def set_symbol(self, symbol):
        self._symbol = symbol
    symbol = property(get_symbol, set_symbol)

    def get_color(self):
        return self._color

    def set_color(self, color):
        self._color = color
        self.setRowColor()
    color = property(get_color, set_color)

    def get_alpha(self):
        return self._alpha

    def set_alpha(self, alpha):
        self._alpha = alpha        
    alpha = property(get_alpha, set_alpha)
