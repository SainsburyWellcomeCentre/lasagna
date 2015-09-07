"""
This class defines the basic imagestack and instructs lasagna as to how to handle image stacks.
"""

from __future__ import division
import numpy as np
import os
from PyQt4 import QtGui, QtCore
import pyqtgraph as pg
from  lasagna_ingredient import lasagna_ingredient 

class imagestack(lasagna_ingredient):
    def __init__(self, parent=None, data=None, fnameAbsPath='', enable=True, objectName='', minMax=None, lut='gray'):
        super(imagestack,self).__init__(parent, data, fnameAbsPath, enable, objectName,
                                        pgObject='ImageItem',
                                        pgObjectConstructionArgs = dict(border='k', levels=minMax)
                                        )


        self.compositionMode=QtGui.QPainter.CompositionMode_Plus

        #Set reasonable default for plotting the images unless different values were specified
        if minMax is None:
            self.minMax = [0, self.defaultHistRange()]
        else:
            self.minMax = minMax

        self.lut=lut #The look-up table
        self.maxColMapValue=255
        self._alpha=100 #image transparency stored here. see getters and setter at end of file


        #Add to the imageStackLayers_model which is associated with the imagestack QTreeView
        name = QtGui.QStandardItem(objectName)
        name.setEditable(False)

        #Add checkbox
        thing = QtGui.QStandardItem()
        thing.setFlags(QtCore.Qt.ItemIsEnabled  | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsUserCheckable)
        thing.setCheckState(QtCore.Qt.Checked)

        #Append to list
        #self.modelItems=(name,thing) #Remove this for now because I have NO CLUE how to get the checkbox state bacl
        self.modelItems=name
        self.model = self.parent.imageStackLayers_Model
        self.addToList()

        #Allow for the option of custom colours in the luminance histogram
        #These should either be False or an RGBalph vector. e.g. [255,0,0,180]
        self.histPenCustomColor = False
        self.histBrushCustomColor = False


    def setColorMap(self,cmap=''):
        """
        Sets the lookup table (colormap) property self.lut to the string defined by cmap.
        Next time the plot is updated, this colormap is used
        """

        if isinstance(cmap,np.ndarray): #In order to allow the user to set an arbitrary color map array to lut
            return cmap

        validCmaps = ['gray','red','green','blue']
        if len(cmap)==0:
            print "valid color maps are gray, red, and green"
            return


        pos = np.array([0.0, 1.0])
        nVal = self.maxColMapValue
        finalColor = self.colorName2value(cmap,nVal=nVal,alpha=self.alpha)
        color = np.array([[ 0 , 0 , 0 ,nVal], finalColor], dtype=np.ubyte)
        map = pg.ColorMap(pos, color)
        lut = map.getLookupTable(0.0, 1.0, nVal+1)

        return lut


    def histBrushColor(self):
        """
        The brush color of the histogram
        """
        if self.histBrushCustomColor != False:
            return self.histBrushCustomColor

        cMap = self.setColorMap(self.lut)
        return cMap[round(len(cMap)/2),:]


    def histPenColor(self):
        """
        The pen color of the histogram
        """
        if self.histPenCustomColor != False:
            return self.histPenCustomColor
            
        cMap = self.setColorMap(self.lut)
        return cMap[-1,:]


    def data(self,axisToPlot=0):
        """
        Returns data formated in the correct way for plotting in the single axes that requested it.
        axisToPlot defines the data dimension along which we are plotting the data.
        specifically, axisToPlot is the dimension that is treated as the z-axis
        """
        return self._data.swapaxes(0,axisToPlot)


    def plotIngredient(self,pyqtObject,axisToPlot=0,sliceToPlot=0):
        """
        Plots the ingredient onto pyqtObject along axisAxisToPlot,
        onto the object with which it is associated
        """
        data = self.data(axisToPlot)
        pyqtObject.setImage(
                        data[sliceToPlot], 
                        levels=self.minMax, 
                        compositionMode=self.compositionMode,
                        lut=self.setColorMap(self.lut),
                        )


    def defaultHistRange(self,logY=False):
        """
        Returns a reasonable values for the maximum plotted value.
        logY if True we log the Y values
        """

        (y,x) = np.histogram(self.data(),bins=100)
        y=np.append(y,0)

        #Remove negative numbers from the calculation. Sometimes these happen with registered images
        y = y[x>0]
        x = x[x>0]

        if logY==True:
            y=np.log10(y+0.1)

        #I'm sure this isn't the most robust approach but it works for now
        thresh=0.925 #find values greater than this proportion

        m = x*y
        vals = np.cumsum(m)/np.sum(m)

        vals = vals>thresh

        return x[vals.tolist().index(True)]


    def changeData(self,imageData,imageAbsPath,recalculateDefaultHistRange=False):
        """
        Replace the current image stack with imageData. 
        Must also supply imageAbsPath.
        """

        if not isinstance(imageData,np.ndarray):
            return False

        self._data = imageData
        self.fnameAbsPath = imageAbsPath 

        if recalculateDefaultHistRange:
            self.defaultHistRange()

        return True


    def flipAlongAxis(self,axisToFlip):
        """
        Flip the data along axisToFlip. 
        """
        if isinstance(axisToFlip,int)==False:
            print "imagestack.flipDataAlongAxis - axisToFlip must be an integer"
            return

        if axisToFlip==0:
            self._data = self._data[::-1,:,:]
        elif axisToFlip==1:
            self._data = self._data[:,::-1,:]
        elif axisToFlip==2:
            self._data = self._data[:,:,::-1]            
        else:
            print "Can not flip axis %d" % axisToFlip


    def rotateAlongDimension(self,axisToRotate):
        """
        Rotate the image stack 90 degrees counter-clockwise along the axis "axisToRotate"
        """
        if axisToRotate>2 or axisToRotate<0:
            print "imagestack.rotateAlongDimension can not rotate along axis %d" % axisToRotate            
            return

        self._data = np.swapaxes(self._data,2,axisToRotate)
        self._data = np.rot90(self._data)
        self._data = np.swapaxes(self._data,2,axisToRotate)


    def swapAxes(self,ax1,ax2):
        """
        Swap axes ax1 and ax2
        """
        if ax1>2 or ax1<0 or ax2>2 or ax2<0:
            print "Axes to swap out of range. "
            return

        self._data = np.swapaxes(self._data,ax1,ax2)


    def removeFromList(self):
        super(imagestack,self).removeFromList()
        if len(self.parent.ingredientList)==1:
                self.parent.ingredientList[0].lut='gray'
                self.parent.initialiseAxes()




    #---------------------------------------------------------------
    #Getters and setters

    #Alpha is set from a 0-100 range and is returned as a usually (0-255)
    def get_alpha(self):
        return int(self.maxColMapValue * (self._alpha/100.0))
    def set_alpha(self,value):
        self._alpha = value
    alpha = property(get_alpha,set_alpha)