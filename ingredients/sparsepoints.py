"""
This class overlays points on top of the image stacks. 
"""

from __future__ import division
import numpy as np
import os
import pyqtgraph as pg
from  lasagna_ingredient import lasagna_ingredient 
from PyQt4 import QtGui, QtCore
import lasagna_helperFunctions as lasHelp
from matplotlib import cm
from numpy import linspace



class sparsepoints(lasagna_ingredient):
    def __init__(self, parent=None, data=None, fnameAbsPath='', enable=True, objectName=''):
        super(sparsepoints,self).__init__(parent, data, fnameAbsPath, enable, objectName,
                                        pgObject='ScatterPlotItem'
                                        )


        #Choose symbols from preferences file. TODO: in future could increment through so successive ingredients have different symbols and colors
        self.symbol = lasHelp.readPreference('symbolOrder')[0]
        self.symbolSize =  int(self.parent.markerSize_spinBox.value())
        self.alpha = int(self.parent.markerAlpha_spinBox.value())
        self.lineWidth = None #Not used right now

        #Add to the imageStackLayers_model which is associated with the points QTreeView
        name = QtGui.QStandardItem(objectName)
        name.setEditable(False)

        #Add checkbox
        thing = QtGui.QStandardItem()
        thing.setFlags(QtCore.Qt.ItemIsEnabled  | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsUserCheckable)
        thing.setCheckState(QtCore.Qt.Checked)

        #self.modelItems=(name,thing) #Remove this for now because I have NO CLUE how to get the checkbox state bacl
        self.modelItems=name
        self.model = self.parent.points_Model

        self.addToList()

        #Set the colour of the object based on how many items are already present
        thisNumber = self.parent.points_Model.rowCount()-1
        number_of_colors = 6
        cm_subsection = linspace(0, 1, number_of_colors) 
        colors = [ cm.jet(x) for x in cm_subsection ]
        color = colors[thisNumber]
        self.color = [color[0]*255, color[1]*255, color[2]*255]


    def data(self,axisToPlot=0):
        """
        Sparse point data are an n by 3 array where each row defines the location
        of a single point in x, y, and z
        """
        if len(self._data)==0:
            return False

        data = np.delete(self._data,axisToPlot,1)
        if axisToPlot==2:
            data = np.fliplr(data)

        return data


    def plotIngredient(self,pyqtObject,axisToPlot=0,sliceToPlot=0):
        """
        Plots the ingredient onto pyqtObject along axisAxisToPlot,
        onto the object with which it is associated
        """ 
        if pyqtObject==False:
            return

        # check if there is data. Use `is False` because np.array == False returns an array
        if self.data() is False or len(self.data()) == 0:
            pyqtObject.setData([],[]) # make sure there is no left data on plot
            return

        z = np.round(self._data[:,axisToPlot])

        data = self.data(axisToPlot)

        #Find points within this z-plane +/- a certain region
        zRange = self.parent.viewZ_spinBoxes[axisToPlot].value()-1
        fromLayer = sliceToPlot-zRange
        toLayer = sliceToPlot+zRange
        data = data[(z>=fromLayer) * (z<=toLayer),:]
        z = z[(z>=fromLayer) * (z<=toLayer)]

        #Add points, making points further from the current
        #layer less prominent 
        #TODO: make this settable by the user via the YAML or UI elements
        dataToAdd = []
        for ii in range(len(data)):

            #Get size for out-of layer points
            size = (self.symbolSize - abs(z[ii]-sliceToPlot)*2)
            if size<1:
                size=1
            #Get opacity for out-of layer points
            alpha = (self.alpha - abs(z[ii]-sliceToPlot)*20)
            if alpha<10:
                alpha=10


            dataToAdd.append(
                    {
                     'pos': (data[ii,0],data[ii,1]),
                     'symbol': self.symbol,
                     'brush': self.symbolBrush(alpha=alpha),
                     'size': size
                     }
                    )

        pyqtObject.setData(dataToAdd)
     

    def addToList(self):
        """
        Add to list and then set UI elements
        """
        super(sparsepoints,self).addToList()
        self.parent.markerSize_spinBox.setValue(self.symbolSize)
        self.parent.markerAlpha_spinBox.setValue(self.alpha)
            

    def symbolBrush(self,alpha=False):
        """
        Returns an RGB + opacity tuple 
        """
        if alpha==False:
            alpha=self.alpha

        if isinstance(self.color,list):
            return tuple(self.color + [alpha])
        else:
            print "sparsepoints.color can not cope with type " + str(type(self.color))


    #---------------------------------------------------------------
    #Getters and setters

    def get_symbolSize(self):
        return self._symbolSize
    def set_symbolSize(self,symbolSize):
        self._symbolSize = symbolSize
    symbolSize = property(get_symbolSize,set_symbolSize)


    def get_symbol(self):
        return self._symbol
    def set_symbol(self,symbol):
        self._symbol = symbol
    symbol = property(get_symbol,set_symbol)


    def get_color(self):
        return self._color
    def set_color(self,color):
        self._color = color
        self.setRowColor()
    color = property(get_color,set_color)


    def get_alpha(self):
        return self._alpha
    def set_alpha(self,alpha):
        self._alpha = alpha        
    alpha = property(get_alpha,set_alpha)


   