"""
this file describes a class that handles the axis behavior for the lasagna viewer
"""

from lasagna_viewBox import lasagna_viewBox
import pyqtgraph as pg


class projection2D():

    def __init__(self, thisPlotWidget, minMax=(0,1500), axisRatio=1, axisToPlot=0):
        """
        thisPlotWidget - the PlotWidget to which we will add the axes
        minMax - the minimum and maximum values of the plotted image. 
        axisRatio - the voxel size ratio along the x and y axes. 1 means square voxels.
        axisToPlot - the dimension along which we are slicing the data.
        """

        #Create properties
        self.axisToPlot = axisToPlot #the axis in 3D space that this view correponds to
        self.minMax=minMax

        #We can link this projection to two others
        self.linkedXprojection=None
        self.linkedYprojection=None


        print "Creating axis at " + str(thisPlotWidget.objectName())
        self.img = pg.ImageItem(border='k',levels=self.minMax)
        self.img.objectName = 'img_' + str(thisPlotWidget.objectName())
        self.view = thisPlotWidget #This should target the axes to a particular plot widget
        self.view.hideButtons()
        self.view.setAspectLocked(True,axisRatio)
        self.view.addItem(self.img)


    def showImage(self, imageStack, sliceToPlot=None):
        # imageStack - the 3-D image stack (can be RGB)
        # sliceToPlot - the slice in that axis to plot. if False we plot the middle slice
        if self.axisToPlot>0:
            imageStack=imageStack.swapaxes(0,self.axisToPlot)
    
        #The mid-point of the stack
        if sliceToPlot==None:
            sliceToPlot=imageStack.shape[0]/2
            
        #Remain within bounds (don't return a non-existant slice)
        if sliceToPlot>imageStack.shape[0]:
            sliceToPlot=imageStack.shape[0]-1;
        if sliceToPlot<0:
            sliceToPlot=0;

        self.img.setImage(imageStack[sliceToPlot], levels=self.minMax)


    def updateDisplayedSlices(self, imageStack, slicesToPlot):
        self.showImage(imageStack)  #TODO: Not have this here. This should be set when the mouse enters the axis and then not changed.
                                    #      Also this doesn't work if we are to change the displayed slice in the current axis by using the mouse wheel.
        #print "updateDisplayedSlices is plotting slices: x:%d and y:%d" % slicesToPlot
        self.linkedYprojection.showImage(imageStack,slicesToPlot[0])
        self.linkedXprojection.showImage(imageStack,slicesToPlot[1])


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
