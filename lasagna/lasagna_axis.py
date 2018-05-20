"""
this file describes a class that handles the axis behavior for the lasagna viewer
"""

import pyqtgraph as pg

from lasagna import lasagna_helperFunctions as lasHelp
from lasagna.ingredients.imagestack import imagestack as lasagna_imagestack


class projection2D():

    def __init__(self, thisPlotWidget, lasagna, axisName='', minMax=(0,1500), axisRatio=1, axisToPlot=0):
        """
        thisPlotWidget - the PlotWidget to which we will add the axes
        minMax - the minimum and maximum values of the plotted image. 
        axisRatio - the voxel size ratio along the x and y axes. 1 means square voxels.
        axisToPlot - the dimension along which we are slicing the data.
        """

        # Create properties
        self.axisToPlot = axisToPlot  # the axis in 3D space that this view correponds to
        self.axisName = axisName
        # We can link this projection to two others
        self.linkedXprojection=None
        self.linkedYprojection=None

        print("Creating axis at " + str(thisPlotWidget.objectName()))
        self.view = thisPlotWidget  # This should target the axes to a particular plot widget

        if lasHelp.readPreference('hideZoomResetButtonOnImageAxes'):
            self.view.hideButtons()

        if lasHelp.readPreference('hideAxes'):
            self.view.hideAxis('left')
            self.view.hideAxis('bottom')               

        self.view.setAspectLocked(True,axisRatio)

        # Loop through the ingredients list and add them to the ViewBox
        self.lasagna = lasagna
        self.items = []  # a list of added plot items TODO: check if we really need this
        self.addItemsToPlotWidget(self.lasagna.ingredientList)

        # The currently plotted slice
        self.currentSlice = None

        # Link the progressLayer signal to a slot that will move through image layers as the wheel is turned
        self.view.getViewBox().progressLayer.connect(self.wheel_layer_slot)

    def addItemToPlotWidget(self, ingredient):
        """
        Adds an ingredient to the PlotWidget as an item (i.e. the ingredient manages the process of 
        producing an item using information in the ingredient properties.
        """
        verbose=False

        _thisItem = (getattr(pg, ingredient.pgObject)(**ingredient.pgObjectConstructionArgs))
        _thisItem.objectName = ingredient.objectName

        if verbose:
            print("\nlasagna_axis.addItemToPlotWidget adds item " + ingredient.objectName + " as: " + str(_thisItem))

        self.view.addItem(_thisItem)
        self.items.append(_thisItem)


    def removeItemFromPlotWidget(self, item):
        """
        Removes an item from the PlotWidget and also from the list of items.
        This function is used for when want to delete or wipe an item from the list
        because it is no longer needed. Use hideIngredient if you want to temporarily
        make something invisible

        "item" is either a string defining an objectName or the object itself
        """
        items = list(self.view.items())
        nItemsBefore = len(items)  # to determine if an item was removed
        if isinstance(item, str):
            removed = False
            for thisItem in items:
                if hasattr(thisItem, 'objectName') and thisItem.objectName == item:
                        self.view.removeItem(thisItem)
                        removed = True
            if not removed:
                print("lasagna_axis.removeItemFromPlotWidget failed to remove item defined by string " + item)
        else:  # it should be an image item
            self.view.removeItem(item)

        # Optionally return True of False depending on whether the removal was successful
        nItemsAfter = len(list(self.view.items()))

        if nItemsAfter < nItemsBefore:
            return True
        elif nItemsAfter == nItemsBefore:
            return False
        else:
            print('** removeItemFromPlotWidget: %d items before removal and %d after removal **' % (nItemsBefore, nItemsAfter))
            return False

        print("%d items after remove call" % len(list(self.view.items())))  # FIXME: unreachable code

    def addItemsToPlotWidget(self, ingredients):
        """
        Add all ingredients in list to the PlotWidget as items
        """
        if not ingredients:
            return
        [self.addItemToPlotWidget(thisIngredient) for thisIngredient in ingredients]

    def removeAllItemsFromPlotWidget(self, items):
        """
        Remove all items (i.e. delete them) from the PlotWidget
        items is a list of strings or plot items
        """
        if not items:
            return
        [self.removeItemFromPlotWidget(thisItem) for thisItem in items]

    def listNamedItemsInPlotWidget(self):
        """
        Print a list of all named items actually *added* in the PlotWidget
        """
        n = 1
        for thisItem in list(self.view.items()):
            if hasattr(thisItem, 'objectName') and isinstance(thisItem.objectName, str):
                print("object %s: %s" % (n, thisItem.objectName))
            n += 1


    def getPlotItemByName(self, objName):
        """
        returns the first plot item in the list bearing the objectName 'objName'
        because of the way we generally add objects, there *should* never be 
        multiple objects with the same name
        """
        for thisItem in list(self.view.items()):
            if hasattr(thisItem, 'objectName') and isinstance(thisItem.objectName, str):
                if thisItem.objectName == objName:
                    return thisItem

    def getPlotItemByType(self, itemType):
        """
        returns all plot items of the defined type. 
        itemType should be a string that defines a pyqtgraph item type. 
        Examples include: ImageItem, ViewBox, PlotItem, AxisItem and LabelItem
        """
        itemList = [] 
        for thisItem in list(self.view.items()):
            if thisItem.__module__.endswith(itemType):
                itemList.append(thisItem)

        return itemList

    def hideItem(self, item):
        """
        Hides an item from the PlotWidget. If you want to delete an item
        outright then use removeItemFromPlotWidget.
        """
        print("NEED TO WRITE lasagna.axis.hideItem()")
        return

    def updatePlotItems_2D(self, ingredientsList, sliceToPlot=None, resetToMiddleLayer=False):
        """
        Update all plot items on axis, redrawing so everything associated with a specified 
        slice (sliceToPlot) is shown. This is done based upon a list of ingredients
        """
        verbose = False

        # loop through all plot items searching for imagestack items (these need to be plotted first)
        for thisIngredient in ingredientsList:
            if isinstance(thisIngredient, lasagna_imagestack):
                # * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
                #TODO: AXIS need some way of linking the ingredient to the plot item but keeping in mind 
                #      that this same object needs to be plotted in different axes, each of which has its own
                #      plot items. So I can't assign a single plot item to the ingredient. Options?
                #      a list of items and axes in the ingredient? I don't like that.

                # Got to the middle of the stack
                if sliceToPlot is None or resetToMiddleLayer:
                    stacks = self.lasagna.returnIngredientByType('imagestack')
                    numSlices = [] 
                    [numSlices.append(thisStack.data(self.axisToPlot).shape[0]) for thisStack in stacks]
                    numSlices = max(numSlices)
                    sliceToPlot = numSlices//2

                self.currentSlice = sliceToPlot

                if verbose:
                    print("lasagna_axis.updatePlotItems_2D - plotting ingredient " + thisIngredient.objectName)

                thisIngredient.plotIngredient(
                                            pyqtObject=lasHelp.findPyQtGraphObjectNameInPlotWidget(self.view,
                                                                                                   thisIngredient.objectName,
                                                                                                   verbose=verbose),
                                            axisToPlot=self.axisToPlot,
                                            sliceToPlot=self.currentSlice
                                            )
                # * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *

        # the image is now displayed

        # loop through all plot items searching for non-image items (these need to be overlaid on top of the image)
        for thisIngredient in ingredientsList:
            if not isinstance(thisIngredient, lasagna_imagestack):
                if verbose:
                    print("lasagna_axis.updatePlotItems_2D - plotting ingredient " + thisIngredient.objectName)

                thisIngredient.plotIngredient(pyqtObject=lasHelp.findPyQtGraphObjectNameInPlotWidget(self.view,
                                                                                                     thisIngredient.objectName,
                                                                                                     verbose=verbose),
                                              axisToPlot=self.axisToPlot,
                                              sliceToPlot=self.currentSlice
                                              )

    def updateDisplayedSlices_2D(self, ingredients, slicesToPlot):
        """
        Update the image planes shown in each of the axes
        ingredients - lasagna.ingredients
        slicesToPlot - a tuple of length 2 that defines which slices to plot for the Y and X linked axes
        """
        # self.updatePlotItems_2D(ingredients)  # TODO: Not have this here. This should be set when the mouse enters the axis and then not changed.
                                               # Like this it doesn't work if we are to change the displayed slice in the current axis using the mouse wheel.
        self.linkedYprojection.updatePlotItems_2D(ingredients, slicesToPlot[0])
        self.linkedXprojection.updatePlotItems_2D(ingredients, slicesToPlot[1])

    def getMousePositionInCurrentView(self, pos):
        # TODO: figure out what pos is and where best to put it. Then can integrate this call into updateDisplayedSlices
        # TODO: Consider not returning X or Y values that fall outside of the image space.
        mousePoint = self.view.getPlotItem().vb.mapSceneToView(pos)
        X = int(mousePoint.x())       
        Y = int(mousePoint.y())
        return X, Y

    def resetAxes(self):
        """
        Set the X and Y limits of the axis to nicely frame the data 
        """
        self.view.autoRange()

    # ------------------------------------------------------
    # slots
    def wheel_layer_slot(self):
        """
        Handle the wheel action that allows the user to move through stack layers
        """
        self.updatePlotItems_2D(self.lasagna.ingredientList,
                                sliceToPlot=round(self.currentSlice + self.view.getViewBox().progressBy))  # round creates an int that supresses a warning in p3
