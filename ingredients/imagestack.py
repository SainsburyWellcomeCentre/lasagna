"""
This class defines the basic imagestack and instructs lasagna as to how to handle image stacks.
TODO: once this is working, pull out the general purpose stuff and set up an ingredient class that this inherits
"""

from __future__ import division
import numpy as np
import os
from PyQt4 import QtGui
import pyqtgraph as pg
from  lasagna_ingredient import lasagna_ingredient 

class imagestack(lasagna_ingredient):
    def __init__(self, data=None, fnameAbsPath='', enable=True, objectName='', minMax=None, lut='gray'):
        super(imagestack,self).__init__(data, fnameAbsPath, enable, objectName,
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

        cmap = cmap.lower()
        pos = np.array([0.0, 1.0])

        nVal = 255
        if cmap == 'gray' or cmap == 'grey':
            color = np.array([[ 0 , 0 , 0 ,nVal], [nVal,nVal,nVal,nVal]], dtype=np.ubyte)
        elif cmap == 'red':
            color = np.array([[ 0 , 0 , 0 ,nVal], [nVal, 0 ,0 ,nVal]], dtype=np.ubyte)
        elif cmap == 'green':
            color = np.array([[ 0 , 0 , 0 ,nVal], [ 0 ,nVal, 0 ,nVal]], dtype=np.ubyte)
        elif cmap == 'blue':
            color = np.array([[ 0 , 0 , 0 ,nVal], [ 0 , 0 ,nVal,nVal]], dtype=np.ubyte)
        elif cmap == 'magenta':
            color = np.array([[ 0 , 0 , 0 ,nVal], [nVal, 0 ,nVal,nVal]], dtype=np.ubyte)
        elif cmap == 'cyan':
            color = np.array([[ 0 , 0 , 0 ,nVal], [ 0 ,nVal,nVal,nVal]], dtype=np.ubyte)
        elif cmap == 'yellow':
            color = np.array([[ 0 , 0 , 0 ,nVal], [nVal,nVal, 0 ,nVal]], dtype=np.ubyte)
        else:
            print "no pre-defined colormap %s. reverting to gray " % cmap
            color = np.array([[ 0 , 0 , 0 ,nVal], [nVal,nVal,nVal,nVal]], dtype=np.ubyte)

        map = pg.ColorMap(pos, color)
        lut = map.getLookupTable(0.0, 1.0, nVal+1)

        return lut



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
                        lut=self.setColorMap(self.lut)
                        )



    def defaultHistRange(self,logY=False):
        """
        Returns a reasonable values for the maximum plotted value.
        logY if True we log the Y values
        """

        (y,x) = np.histogram(self.data(),bins=100)

        if logY==True:
            y=np.log10(y+0.1)

        
        #I'm sure this isn't the most robust approach but it works for now
        thresh=0.925 #find values greater than this proportion

        y=np.append(y,0)

        m = x*y
        vals = np.cumsum(m)/np.sum(m)
        vals = vals>thresh

        return x[vals.tolist().index(True)]


    def changeData(self,imageData,imageAbsPath,recalculateDefaultHistRange=False):
        """
        Replace the current image stack with imageData. 
        Must also supply imageAbsPath.
        """
        self.__data = imageData
        self.fnameAbsPath = imageAbsPath 

        if recalculateDefaultHistRange:
            self.defaultHistRange()


    def flipDataAlongAxis(self,axisToFlip):
        """
        Flip the data along axisToFlip. 
        """
        if isinstance(axisToFlip,int)==False:
            print "imagestack.flipDataAlongAxis - axisToFlip must be an integer"
            return


        if axisToFlip==0:
            self.__data = self.__data[::-1,:,:]
        elif axisToFlip==1:
            self.__data = self.__data[:,::-1,:]
        elif axisToFlip==2:
            self.__data = self.__data[:,:,::-1]            
        else:
            print "Can not flip axis %d" % axisToFlip

            