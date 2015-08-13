"""
Ingredients inherit from this class
"""

import os
import pyqtgraph as pg

class lasagna_ingredient(object):
    def __init__(self, parent, data, fnameAbsPath='', enable=True, objectName='',pgObject='', pgObjectConstructionArgs=dict()):

    	self.parent		= parent
        self._data     	= data              #The raw data for this ingredient go here.

        self.objectName = objectName        #The name of the object TODO: decide exactly what this will be

        self.fnameAbsPath = fnameAbsPath    #Absolute path to file name        

        self.enable     = enable            #Item is plotted if enable is True. Hidden if enable is False
        self.pgObject   = pgObject          #The PyQtGraph item type which will display the data [see lasagna_axis.addItemToPlotWidget()]
        self.pgObjectConstructionArgs = pgObjectConstructionArgs #The pyqtgrao item is created with these arguments


        

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


    def show(self):
    	"""
    	Show ingredient on plots by adding the plot item to all 2D axes so that it becomes available for plotting
    	"""
        [axis.addItemToPlotWidget(self) for axis in self.parent.axes2D]


    def removePlotItem(self):
    	"""
    	Remove ingredient from plots by removing the plot item from all 2D axes so that it becomes unavailable for plotting
    	"""
        [axis.removeItemFromPlotWidget(self.objectName) for axis in self.parent.axes2D]