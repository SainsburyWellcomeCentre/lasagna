

"""
This tutorial plugin demonstrates how to overlay dynamically generated 
point data onto the plot axes. The plugin does the following:

* Upon starting, the plugin generates 100 independent random points in 
  each view and overlays them onto the axes.
* Upon each re-painting of the axes a new set of 100 points are created 
  and overlaid.
* The points are all removed and their plot items are cleaned up when 
  the plugin is closed.

"""

from lasagna_plugin import lasagna_plugin
import numpy as np
import sys

class plugin(lasagna_plugin): 

    def __init__(self,lasagna,parent=None):
        super(plugin,self).__init__(lasagna)

        #re-define some default properties that were originally defined in lasagna_plugin
        self.pluginShortName='Overlay random points' 
        self.pluginLongName='displays dynamically generated random points onto the axes' 
        self.pluginAuthor='Rob Campbell'

        self.lasagna = lasagna

        #add a sparsepoints ingredient
        self.objName = 'tutePoints'
        self.lasagna.addIngredient(object_name=self.objName,
                                   kind='sparsepoints',
                                   data=self.generateRandomData())

        self.lasagna.returnIngredientByName(self.objName).addToPlots() #Add item to all three 2D plots
        self.lasagna.axes2D[0].listNamedItemsInPlotWidget()
        self.lasagna.initialiseAxes(resetAxes=True) #update the plots.


    def generateRandomData(self):
        """
        Generate random data spanning the extent of the first image stack
        """
        stackName = self.lasagna.imageStackLayers_Model.index(0,0).data()
        firstLayer = self.lasagna.returnIngredientByName(stackName)
        if firstLayer == False:
            print("No image layers loaded")
            return

        imShape = firstLayer.data().shape

        n = 10000 #number of random points to make
        numAxes = 3

        r = np.random.rand(n*numAxes).reshape((n, numAxes)) #the random array

        #multiply values in each dimension of the array by the array size of the first layer image
        for ii in range(numAxes):
            r[:,ii] = np.floor(r[:,ii]*imShape[ii])

        return r



    #The following methods are involved in shutting down the plugin window
    """
    This method is called by lasagna when the user unchecks the plugin in the menu
    """

    def closePlugin(self):
        #Remove points from axes then remove the ingredient from the list. 
        self.lasagna.removeIngredientByName(self.objName)



