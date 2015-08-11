"""
This class overlays points on top of the image stacks. 
TODO: once this is working, pull out the general purpose stuff and set up an ingredient class that this inherits
"""

from __future__ import division
import numpy as np
import os
from PyQt4 import QtGui
import pyqtgraph as pg

class sparsepoints(object):
    def __init__(self, data=None, fnameAbsPath='', enable=True, objectName='', minMax=[0,1E3]):

        #Assign input arguments to properties of the class instance. 
        #The following properties are common to all ingredients
        self.__data     = data              #The raw data for this ingredient go here.

        self.enable     = enable            #Item is plotted if enable is True. Hidden if enable is False
        self.objectName = objectName        #The name of the object TODO: decide exactly what this will be


        self.pgObject   = 'PlotDataItem'       #The PyQtGraph item type which will display the data [see lasagna_axis.addItemToPlotWidget()]
        self.pgObjectConstructionArgs = dict() #The item is created with these arguments

        #Set up class-specific properties, which classes other than image stack may not share
        #or may share but have different values assigned





    def data(self,axisToPlot=0):
        """
        Sparse point data are an n by 3 array where each row defines the location
        of a single point in x, y, and z
        """
        data = np.delete(self.__data,axisToPlot,1)
        if axisToPlot==2:
            data = np.fliplr(data)

        return data


    
    # TODO: farm out preceeding stuff to a general-purpose ingredient class 
    # Methods that follow are specific to the imagestack class. Methods that preceed this
    # are general-purpose and can be part of an "ingredient" class

    def plotIngredient(self,pyqtObject,axisToPlot=0,sliceToPlot=0):
        """
        Plots the ingredient onto pyqtObject along axisAxisToPlot,
        onto the object with which it is associated
        """
        z = self.__data[:,axisToPlot]
        data = self.data(axisToPlot)
        data = data[z==sliceToPlot,:]


        pyqtObject.setData(x=data[:,0], y=data[:,1], symbol='t', pen=None, symbolSize=10, symbolBrush=(100, 100, 255, 150))
        