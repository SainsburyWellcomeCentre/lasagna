"""
This class overlays points on top of the image stacks. 
"""

import numpy as np
from PyQt5 import QtGui, QtCore
from matplotlib import cm
from numpy import linspace

from lasagna.ingredients.lasagna_ingredient import lasagna_ingredient
from lasagna.utils import preferences


class sparsepoints(lasagna_ingredient):
    def __init__(
        self, parent=None, data=None, fnameAbsPath="", enable=True, objectName=""
    ):
        super(sparsepoints, self).__init__(
            parent, data, fnameAbsPath, enable, objectName, pgObject="ScatterPlotItem"
        )

        # Choose symbols from preferences file. TODO: in future could increment through so successive ingredients have different symbols and colors
        self.symbol = preferences.readPreference("symbolOrder")[0]
        self.symbolSize = int(self.parent.markerSize_spinBox.value())
        self.alpha = int(self.parent.markerAlpha_spinBox.value())
        self.lineWidth = None  # Not used right now

        self.build_model_for_list(objectName)
        self.model = self.parent.points_Model
        self.addToList()

        # Set the colour of the object based on how many items are already present
        number_of_colors = 6
        this_number = (
            self.parent.points_Model.rowCount() - 1
        ) % number_of_colors  # FIXME: rename
        cm_subsection = linspace(0, 1, number_of_colors)
        colors = [cm.jet(x) for x in cm_subsection]
        color = colors[this_number]
        self.color = [color[0] * 255, color[1] * 255, color[2] * 255]

    def data(self, axisToPlot=0):
        """
        Sparse point data are an n by 3 array where each row defines the location
        of a single point in x, y, and z
        """

        if self._data is None or not len(self._data):
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
            return

        # check if there is data. Use `is False` because np.array == False returns an array
        if self.data() is False or len(self.data()) == 0:
            pyqtObject.setData([], [])  # make sure there is no left data on plot
            return

        z = np.round(self._data[:, axisToPlot])

        data = self.data(axisToPlot)

        # Find points within this z-plane +/- a certain region
        z_range = self.parent.viewZ_spinBoxes[axisToPlot].value() - 1
        from_layer = sliceToPlot - z_range
        to_layer = sliceToPlot + z_range
        data = data[(z >= from_layer) * (z <= to_layer), :]
        z = z[(z >= from_layer) * (z <= to_layer)]

        # Add points, making points further from the current
        # layer less prominent
        # TODO: make this settable by the user via the YAML or UI elements
        data_to_add = []
        for i in range(len(data)):
            # Get size for out-of layer points
            size = self.symbolSize - abs(z[i] - sliceToPlot) * 2
            if size < 1:
                size = 1
            # Get opacity for out-of layer points
            alpha = self.alpha - abs(z[i] - sliceToPlot) * 20
            if alpha < 10:
                alpha = 10

            data_to_add.append(
                {
                    "pos": (data[i, 0], data[i, 1]),
                    "symbol": self.symbol,
                    "brush": self.symbolBrush(alpha=alpha),
                    "size": size,
                }
            )

        pyqtObject.setData(data_to_add)

    def addToList(self):
        """
        Add to list and then set UI elements
        """
        super(sparsepoints, self).addToList()
        self.parent.markerSize_spinBox.setValue(self.symbolSize)
        self.parent.markerAlpha_spinBox.setValue(self.alpha)

    def symbolBrush(self, alpha=False):
        """
        Returns an RGB + opacity tuple 
        """
        if not alpha:
            alpha = self.alpha

        if isinstance(self.color, list):
            return tuple(self.color + [alpha])
        else:
            print(
                ("sparsepoints.color can not cope with type " + str(type(self.color)))
            )

    def save(self, path=None):
        """Save sparse point in "pts" format (basic coordinates, space separated)"""
        if path is None:
            path, _ = QtGui.QFileDialog.getSaveFileName(
                self.parent, "File to save %s" % self.objectName, self.objectName
            )
            # getSaveFileName also returns the selected filter "All file (*)" for instance.
            # Ignore the second output
        if not path:
            return
        with open(path, "w") as F:
            for c in self.raw_data():
                F.write(",".join(["%s" % i for i in c]) + "\n")
        print("%s saved as %s" % (self.objectName, path))

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
