"""
this file describes a class that handles the axis behavior for the lasagna viewer
"""

from lasagna_viewBox import lasagna_viewBox
import lasagna_helperFunctions as lasHelp
import handleIngredients
import pyqtgraph as pg


class projection2D():

    def __init__(self, thisPlotWidget, ingredients=[], minMax=(0,1500), axisRatio=1, axisToPlot=0):
        """
        thisPlotWidget - the PlotWidget to which we will add the axes
        minMax - the minimum and maximum values of the plotted image. 
        axisRatio - the voxel size ratio along the x and y axes. 1 means square voxels.
        axisToPlot - the dimension along which we are slicing the data.
        """

        #Create properties
        self.axisToPlot = axisToPlot #the axis in 3D space that this view correponds to

        #We can link this projection to two others
        self.linkedXprojection=None
        self.linkedYprojection=None


        print "Creating axis at " + str(thisPlotWidget.objectName())
        self.view = thisPlotWidget #This should target the axes to a particular plot widget
        self.view.hideButtons()
        self.view.setAspectLocked(True,axisRatio)

        #Loop through the ingredients list and add them to the ViewBox
        self.items=[] #a list of added plot items TODO: check if we really need this
        self.addIngredientsToPlotWidget(ingredients)



    def addIngredientToPlotWidget(self,ingredient):
        """
        Adds an ingredient to the PlotWidget using information in the ingredient properties 
        to determine how to add it.
        """
        #TODO: AXIS find a way to feed in the constructor arguments in a dynamic way
        _thisItem = ( getattr(pg,ingredient.pgObject)(border='k',levels=ingredient.minMax) )
        #self.img = pg.ImageItem(border='k',levels=self.minMax) #TODO: AXIS this can't be added here
        _thisItem.objectName = ingredient.objectName


        self.view.addItem(_thisItem)
        self.items.append(_thisItem)


    def removeIngredientFromPlotWidget(self,ingredient):
        """
        Removes an ingredient from the PlotWidget and also from the list of items.
        This function is used for when want to delete or wipe an item from the list
        because it is no longer needed. Use hideIngredient if you want to temporarily
        make something invisible
        """
        pass


    def addIngredientsToPlotWidget(self,ingredients=[]):
        """
        Add all ingredients in list to the PlotWidget
        """
        if len(ingredients)==0:
            return
        [self.addIngredientToPlotWidget(thisIngredient) for thisIngredient in ingredients]


    def removeAllIngredientsFromPlotWidget(self,ingredients):
        """
        Remove all ingredients (i.e. delete them) from the PlotWidget
        """
        if len(ingredients)==0:
            return
        [self.removeIngredientFromPlotWidget(thisIngredient) for thisIngredient in ingredients]


    def hideIngredient(self,ingredient):
        """
        Hides an ingredient from the PlotWidget. If you want to delete an ingredient
        outright then use removeIngredientFromPlotWidget.
        """
        pass


    def updatePlotItems_2D(self, ingredients, sliceToPlot=None):
        """
        Update all plot items on axis, redrawing so everything associated with a specified 
        slice (sliceToPlot) is shown.
        """

        # Get base-image in correct orientation.
        baseImage = handleIngredients.returnIngredientByName('baseImage',ingredients)

        #Use base-image shape to set sliceToPlot correctly so it stays within bounds
        #  get the number of slices in the base image stack along this axes' z (depth) dimension
        numSlices = baseImage.data(self.axisToPlot).shape[0]

        #  choose the mid-point if no slice was specified. 
        if sliceToPlot==None:
            sliceToPlot=numSlices/2 #The mid-point of the stack
            
        #  remain within bounds (don't return a non-existant slice)
        if sliceToPlot>numSlices:
            sliceToPlot=numSlices-1;
        elif sliceToPlot<0:
            sliceToPlot=0;

        # loop through all plot items searching for imagestack items (these need to be plotted first)
        #TODO: CHECK HOW ORDER IS DECIDED
        #     the plot order may already have been decided at the time the objects were added so having these 
        #     two loops may be of no use
        for thisIngredient in ingredients:
            if thisIngredient.__module__.endswith('imagestack'):
                # * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
                #TODO: AXIS need some way of linking the ingredient to the plot item but keeping in mind 
                #      that this same object needs to be plotted in different axes, each of which has its own
                #      plot items. So I can't assign a single plot item to the ingredient. Options?
                #      a list of items and axes in the ingredient? I don't link that.
                thisIngredient.plotIngredient(
                                            pyqtObject=lasHelp.findPyQtGraphObjectNameInPlotWidget(self.view,thisIngredient.objectName), 
                                            axisToPlot=self.axisToPlot, 
                                            sliceToPlot=sliceToPlot
                                            )
                # * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *

        # the image is now displayed

        # loop through all plot items searching for non-image items (these need to be overlaid onto the image)
        for thisIngredient in ingredients:
            if not thisIngredient.__module__.endswith('imagestack'):
                pass
                #thisIngredient.plotIngredient(pyqtObject=self.img, axisToPlot=self.axisToPlot, sliceToPlot=sliceToPlot)


    def updateDisplayedSlices_2D(self, ingredients, slicesToPlot):
        """
        Update the image planes shown in each of the axes
        ingredients - lasagna.ingredients
        slicesToPlot - a tuple of length 2 that defines which slices to plot for the Y and X linked axes
        """
        # TODO: AXIS will need to be updated to cope with a more flexible axis paradigm
        self.updatePlotItems_2D(ingredients)  #TODO: Not have this here. This should be set when the mouse enters the axis and then not changed.
                                     #      Also this doesn't work if we are to change the displayed slice in the current axis by using the mouse wheel.
        #print "updateDisplayedSlices is plotting slices: x:%d and y:%d" % slicesToPlot
        self.linkedYprojection.updatePlotItems_2D(ingredients,slicesToPlot[0])
        self.linkedXprojection.updatePlotItems_2D(ingredients,slicesToPlot[1])


    def getMousePositionInCurrentView(self, pos):
        #TODO: figure out what pos is and where best to put it. Then can integrate this call into updateDisplayedSlices
        #TODO: Consider not returning X or Y values that fall outside of the image space.
        mousePoint = self.view.getPlotItem().vb.mapSceneToView(pos)
        X = int(mousePoint.x())       
        Y = int(mousePoint.y())
        return (X,Y)


    def resetAxes(self):
        """
        Set the X and Y limits of the axis to nicely frame the data 
        """
        self.view.autoRange()
