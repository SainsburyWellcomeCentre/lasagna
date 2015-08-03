"""
this file describes a class that handles the axis behavior for the lasagna viewer
"""

from lasagna_viewBox import lasagna_viewBox
import lasagna_helperFunctions as lasHelp
import pyqtgraph as pg


class projection2D():

    def __init__(self, thisPlotWidget, lasagna, axisName='', minMax=(0,1500), axisRatio=1, axisToPlot=0):
        """
        thisPlotWidget - the PlotWidget to which we will add the axes
        minMax - the minimum and maximum values of the plotted image. 
        axisRatio - the voxel size ratio along the x and y axes. 1 means square voxels.
        axisToPlot - the dimension along which we are slicing the data.
        """

        #Create properties
        self.axisToPlot = axisToPlot #the axis in 3D space that this view correponds to
        self.axisName = axisName
        #We can link this projection to two others
        self.linkedXprojection=None
        self.linkedYprojection=None


        print "Creating axis at " + str(thisPlotWidget.objectName())
        self.view = thisPlotWidget #This should target the axes to a particular plot widget
        self.view.hideButtons()
        self.view.setAspectLocked(True,axisRatio)

        #Loop through the ingredients list and add them to the ViewBox
        self.lasagna = lasagna
        self.items=[] #a list of added plot items TODO: check if we really need this
        self.addItemsToPlotWidget(self.lasagna.ingredientList)



    def addItemToPlotWidget(self,ingredient):
        """
        Adds an ingredient to the PlotWidget as an item (i.e. the ingredient manages the process of 
        producing an item using information in the ingredient properties.
        """
        _thisItem = ( getattr(pg,ingredient.pgObject)(**ingredient.pgObjectConstructionArgs) )
        _thisItem.objectName = ingredient.objectName


        self.view.addItem(_thisItem)
        self.items.append(_thisItem)


    def removeItemFromPlotWidget(self,item):
        """
        Removes an item from the PlotWidget and also from the list of items.
        This function is used for when want to delete or wipe an item from the list
        because it is no longer needed. Use hideIngredient if you want to temporarily
        make something invisible

        "item" is either a string defining an objectName or the object itself
        """

        items=self.view.items()
        nItemsBefore = len(items) #to determine if an item was removed
        if isinstance(item,str):
            for thisItem in items:
                if hasattr(thisItem,'objectName') and thisItem.objectName==item:
                        self.view.removeItem(thisItem)
        else: #it should be an image item
            self.view.removeItem(item)

        #Optionally return True of False depending on whether the removal was successful
        nItemsAfter = len(self.view.items())
        if nItemsAfter<nItemsBefore:
            return True
        elif nItemsAfter==nItemsBefore:
            return False
        else:
            print '** removeItemFromPlotWidget: %d items before removal and %d after removal **' % (nItemsBefore,nItemsAfter)
            return False



        print "%d items after remove call" % len(self.view.items())


    def addItemsToPlotWidget(self,ingredients=[]):
        """
        Add all ingredients in list to the PlotWidget as items
        """
        if len(ingredients)==0:
            return
        [self.addItemToPlotWidget(thisIngredient) for thisIngredient in ingredients]


    def removeAllItemsFromPlotWidget(self,items):
        """
        Remove all items (i.e. delete them) from the PlotWidget
        items is a list of strings or plot items
        """
        if len(items)==0:
            return
        [self.removeItemFromPlotWidget(thisItem) for thisItem in items]


    def listNamedItemsInPlotWidget(self):
        """
        Print a list of all named items actually *added* in the PlotWidget
        """
        n=1
        for thisItem in self.view.items():
            if hasattr(thisItem,'objectName') and isinstance(thisItem.objectName,str):
                print "object %s: %s" % (n,thisItem.objectName)
            n=n+1

    def getPlotItemByName(self,objName):
        """
        returns the first plot item in the list bearing the objectName 'objName'
        because of the way we generally add objects, there *should* never be 
        multiple objects with the same name
        """
        for thisItem in self.view.items():
            if hasattr(thisItem,'objectName') and isinstance(thisItem.objectName,str):
                if thisItem.objectName == objName:
                    return thisItem



    def hideItem(self,item):
        """
        Hides an item from the PlotWidget. If you want to delete an item
        outright then use removeItemFromPlotWidget.
        """
        print "NEED TO WRITE lasagna.axis.hideItem()"
        return


    def updatePlotItems_2D(self, ingredients, sliceToPlot=None):
        """
        Update all plot items on axis, redrawing so everything associated with a specified 
        slice (sliceToPlot) is shown. This is done based upon a list of ingredients
        """

        # Get base-image in correct orientation.
        baseImage = self.lasagna.returnIngredientByName('baseImage')

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
        #NOTE: the following two loops will be changed soon
        #TODO: CHECK HOW ORDER IS DECIDED
        #TODO: have just one loop
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
            if not thisIngredient.__module__.endswith('imagestack'): #TODO: too specific 
                thisIngredient.plotIngredient(pyqtObject=lasHelp.findPyQtGraphObjectNameInPlotWidget(self.view,thisIngredient.objectName), 
                                              axisToPlot=self.axisToPlot, 
                                              sliceToPlot=sliceToPlot)


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
