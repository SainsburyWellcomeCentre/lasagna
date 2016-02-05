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
    	self.model.appendRow(self.modelItems)
    	self.model.parent().setCurrentIndex(self.modelItems.index()) #Parent is, for example, a QTreeView


    def removeFromList(self):
        """
        Remove ingredient from the UI list with which it is associated  
        """
    	items = self.model.findItems(self.objectName)
    	self.model.removeRow(items[0].row())


    def colorName2value(self,colorName,nVal=255,alpha=255):
    	"""
    	Input is a color name, output is an RGBalpha vector.
    	nVal is the maximum intensity value
    	"""
    	colorName = colorName.lower()

    	colorDict = {
    				'gray'	: 	[nVal,nVal,nVal,alpha],
    				'red'	: 	[nVal, 0 , 0 ,alpha],
        			'green'	:	[ 0 ,nVal, 0 ,alpha],
					'blue'	:	[ 0 , 0 ,nVal,alpha],
        			'magenta':	[nVal, 0 ,nVal,alpha],
			        'cyan'	:	[ 0 ,nVal,nVal,alpha], 
        			'yellow':	[nVal,nVal, 0 ,alpha]
        			}

        if colorDict.has_key(colorName):
        	return colorDict[colorName]
        else:
            print "no pre-defined colormap %s. reverting to gray " % colorName 
            return colorDict['gray']

