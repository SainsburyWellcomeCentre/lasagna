"""
This class defines the basic imagestack and instructs lasagna as to how to handle image stacks.
"""


import numpy as np
import pyqtgraph as pg
from PyQt5 import QtGui, QtCore

from lasagna.ingredients.lasagna_ingredient import lasagna_ingredient
from lasagna.io_libs.image_stack_loader import save_stack


class imagestack(lasagna_ingredient):
    def __init__(
        self,
        parent=None,
        data=None,
        fnameAbsPath="",
        enable=True,
        objectName="",
        minMax=None,
        lut="gray",
    ):
        super(imagestack, self).__init__(
            parent,
            data,
            fnameAbsPath,
            enable,
            objectName,
            pgObject="ImageItem",
            pgObjectConstructionArgs=dict(border="k", levels=minMax),
        )

        self.compositionMode = QtGui.QPainter.CompositionMode_Plus

        # Set reasonable default for plotting the images unless different values were specified
        if minMax is None:
            self.minMax = [0, self.defaultHistRange()]
        else:
            self.minMax = minMax

        self.lut = lut  # The look-up table
        self.maxColMapValue = 255
        self._alpha = (
            100
        )  # image transparency stored here. see getters and setter at end of file

        # Add to the imageStackLayers_model which is associated with the imagestack QTreeView
        name = QtGui.QStandardItem(objectName)
        name.setEditable(False)

        # Add checkbox
        thing = QtGui.QStandardItem()
        thing.setFlags(
            QtCore.Qt.ItemIsEnabled
            | QtCore.Qt.ItemIsEditable
            | QtCore.Qt.ItemIsUserCheckable
        )
        thing.setCheckState(QtCore.Qt.Checked)

        # Append to list
        # self.modelItems=(name,thing) #Remove this for now because I have NO CLUE how to get the checkbox state bacl
        self.modelItems = name
        self.model = self.parent.imageStackLayers_Model
        self.addToList()

        # Allow for the option of custom colours in the luminance histogram
        # These should either be False or an RGBalph vector. e.g. [255,0,0,180]
        self.histPenCustomColor = False
        self.histBrushCustomColor = False

        self.histogram = self.calcHistogram()

    def setColorMap(self, cmap=""):
        """
        Sets the lookup table (colormap) property self.lut to the string defined by cmap.
        Next time the plot is updated, this colormap is used
        """

        if isinstance(
            cmap, np.ndarray
        ):  # In order to allow the user to set an arbitrary color map array to lut
            return cmap

        valid_cmaps = ("gray", "red", "green", "blue")
        if not cmap:
            print("valid color maps are {}".format(valid_cmaps))
            return

        pos = np.array([0.0, 1.0])
        n_val = self.maxColMapValue
        final_color = self.colorName2value(cmap, nVal=n_val, alpha=self.alpha)
        color = np.array([[0, 0, 0, n_val], final_color], dtype=np.ubyte)
        color_map = pg.ColorMap(pos, color)
        lut = color_map.getLookupTable(0.0, 1.0, n_val + 1)

        return lut

    def colorName2value(self, colorName, nVal=255, alpha=255):
        """
        Converts a colour map name to an RGBa vector
        colorName is a color name, output is an RGBalpha vector.
        nVal is the maximum intensity value
        """
        colorName = colorName.lower()

        color_dict = {
            "gray": [nVal, nVal, nVal, alpha],
            "red": [nVal, 0, 0, alpha],
            "green": [0, nVal, 0, alpha],
            "blue": [0, 0, nVal, alpha],
            "magenta": [nVal, 0, nVal, alpha],
            "cyan": [0, nVal, nVal, alpha],
            "yellow": [nVal, nVal, 0, alpha],
        }

        if colorName in color_dict:
            return color_dict[colorName]
        else:
            print(("no pre-defined colormap %s. reverting to gray " % colorName))
            return color_dict["gray"]

    def calcHistogram(self):
        """
        Calculate the histogram and return results
        """
        y, x = np.histogram(self._data, bins=256)
        x = x[0:-1]  # chop off last value

        return {"x": x, "y": y}

    def histBrushColor(self):
        """
        The brush color of the histogram
        """
        if self.histBrushCustomColor:
            return self.histBrushCustomColor

        c_map = self.setColorMap(self.lut)
        return c_map[int(round(len(c_map) / 2)), :]

    def histPenColor(self):
        """
        The pen color of the histogram
        """
        if self.histPenCustomColor:
            return self.histPenCustomColor

        c_map = self.setColorMap(self.lut)
        return c_map[-1, :]

    def data(self, axisToPlot=0):
        """
        Returns data formated in the correct way for plotting in the single axes that requested it.
        axisToPlot defines the data dimension along which we are plotting the data.
        specifically, axisToPlot is the dimension that is treated as the z-axis
        """
        return self._data.swapaxes(0, axisToPlot)

    def plotIngredient(self, pyqtObject, axisToPlot=0, sliceToPlot=0):
        """
        Plots the ingredient onto pyqtObject along axisAxisToPlot,
        onto the object with which it is associated
        """

        data = self.data(axisToPlot)

        if data.shape[0] - 1 < sliceToPlot:
            pyqtObject.setVisible(False)
            sliceToPlot = data.shape[0] - 1
        elif sliceToPlot < 0:
            pyqtObject.setVisible(False)
            sliceToPlot = 0
        else:
            pyqtObject.setVisible(True)

        pyqtObject.setImage(
            data[sliceToPlot],
            levels=self.minMax,
            compositionMode=self.compositionMode,
            lut=self.setColorMap(self.lut),
        )

    def defaultHistRange(self, logY=False):
        """
        Returns a reasonable values for the maximum plotted value.
        logY if True we log the Y values
        """

        y, x = np.histogram(self.data(), bins=100)
        y = np.append(y, 0)

        # Remove negative numbers from the calculation. Sometimes these happen with registered images
        y = y[x > 0]
        x = x[x > 0]

        if logY:
            y = np.log10(y + 0.1)

        # I'm sure this isn't the most robust approach but it works for now
        thresh = 0.925  # find values greater than this proportion

        m = x * y
        vals = np.cumsum(m) / np.sum(m)

        vals = vals > thresh

        return x[vals.tolist().index(True)]

    def changeData(self, imageData, imageAbsPath, recalculateDefaultHistRange=False):
        """
        Replace the current image stack with imageData. 
        Must also supply imageAbsPath.
        """

        if not isinstance(imageData, np.ndarray):
            return False

        self._data = imageData
        self.fnameAbsPath = imageAbsPath

        if recalculateDefaultHistRange:
            self.defaultHistRange()

        return True

    def flipAlongAxis(self, axisToFlip):  # FIXME: use numpy flip
        """
        Flip the data along axisToFlip. 
        """
        if not isinstance(axisToFlip, int):
            print("imagestack.flipDataAlongAxis - axisToFlip must be an integer")
            return

        if axisToFlip == 0:
            self._data = self._data[::-1, :, :]
        elif axisToFlip == 1:
            self._data = self._data[:, ::-1, :]
        elif axisToFlip == 2:
            self._data = self._data[:, :, ::-1]
        else:
            print(("Can not flip axis %d" % axisToFlip))

    def rotateAlongDimension(self, axisToRotate):
        """
        Rotate the image stack 90 degrees counter-clockwise along the axis "axisToRotate"
        """
        if axisToRotate > 2 or axisToRotate < 0:
            print(
                (
                    "imagestack.rotateAlongDimension can not rotate along axis %d"
                    % axisToRotate
                )
            )
            return

        self._data = np.swapaxes(self._data, 2, axisToRotate)
        self._data = np.rot90(self._data)
        self._data = np.swapaxes(self._data, 2, axisToRotate)

    def swapAxes(self, ax1, ax2):
        """
        Swap axes ax1 and ax2
        """
        if ax1 not in range(3) or ax2 not in range(3):
            print("Axes to swap out of range. ")
            return

        self._data = np.swapaxes(self._data, ax1, ax2)

    def removeFromList(self):
        super(imagestack, self).removeFromList()
        if len(self.parent.ingredientList) == 1:
            self.parent.ingredientList[0].lut = "gray"
            self.parent.initialiseAxes()

    def save(self, path=None):
        if path is None:
            path = QtGui.QFileDialog.getSaveFileName(
                self.parent, "File to save {}".format(self.objectName)
            )
        if not path:
            return
        save_stack(path, self.raw_data())
        print(("%s saved as %s" % (self.objectName, path)))

    # ---------------------------------------------------------------
    # Getters and setters
    # Alpha is set from a 0-100 range and is returned as a usually (0-255)
    def get_alpha(self):
        return int(self.maxColMapValue * (self._alpha / 100.0))

    def set_alpha(self, value):
        self._alpha = value

    alpha = property(get_alpha, set_alpha)
