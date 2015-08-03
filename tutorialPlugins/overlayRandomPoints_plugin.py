

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
        objName = 'tutePoints'
        self.lasagna.addIngredient(objectName=objName , 
                                   kind='sparsepoints' ,
                                   data=self.generateRandomData())

        #ing = self.lasagna.returnIngredientByName('tutePoints')
        
        #Add plot items to axes so that they become available for plotting
        [axis.addItemToPlotWidget(self.lasagna.returnIngredientByName(objName)) for axis in self.lasagna.axes2D]
        
        self.lasagna.axes2D[0].listNamedItemsInPlotWidget()
       

    """
    #self.lasagna.updateMainWindowOnMouseMove is run each time the axes are updated. 
    #So we can hook into it to plot points TODO: is this the best hook?
    def hook_updateMainWindowOnMouseMove_End(self):
        ingredient = handIng.returnIngredientByName('tutePoints',self.lasagna.ingredients)
        ingredient.__data = self.generateRandomData()
        
        print ingredient.__data[1:10,:]
        print ingredient.data()[1:10,:] #THIS DOESN'T CHANGE. WHY??
    """


    def generateRandomData(self):
        baseImage = self.lasagna.returnIngredientByName('baseImage')
        if baseImage == False:
            print "No base image loaded"
            return
        imShape = baseImage.data().shape

        n = 10E3 #number of random points to make
        numAxes = 3

        print "generated"

        r = np.random.rand(n*numAxes).reshape((n,numAxes)) #the random array

        #multiply values in each dimension of the array by the array size of the base image
        for ii in range(numAxes):
            r[:,ii] = np.floor(r[:,ii]*imShape[ii])

        return r



    #The following methods are involved in shutting down the plugin window
    """
    This method is called by lasagna when the user unchecks the plugin in the menu
    """

    def closePlugin(self):
        #Remove points from axes then remove the ingredient from the list. 
        [axis.removeItemFromPlotWidget('tutePoints') for axis in self.lasagna.axes2D]
        self.lasagna.removeIngredientByName('tutePoints')



