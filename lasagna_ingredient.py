"""
Ingredients inherit from this class
"""

import os
import pyqtgraph as pg

class lasagna_ingredient(object):
    def __init__(self, data, fnameAbsPath='', enable=True, objectName='',pgObject='', pgObjectConstructionArgs=dict()):

        #Assign input arguments to properties of the class instance. 
        #The following properties are common to all ingredients
        self._data     = data              #The raw data for this ingredient go here.

        self.enable     = enable            #Item is plotted if enable is True. Hidden if enable is False
        self.objectName = objectName        #The name of the object TODO: decide exactly what this will be

        self.pgObject   = pgObject          #The PyQtGraph item type which will display the data [see lasagna_axis.addItemToPlotWidget()]
        self.pgObjectConstructionArgs = pgObjectConstructionArgs #The pyqtgrao item is created with these arguments

        self.fnameAbsPath = fnameAbsPath    #Absolute path to file name        




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