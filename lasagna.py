#!/usr/bin/python

"""
Show coronal, transverse and saggital plots in different panels

Example usage:
threeSubPlots.py myImage.tiff myImage2.tiff
threeSubPlots.py myImage.mhd myImage2.mhd
threeSubPlots.py myImage.tiff myImage2.mhd

Depends on:
vtk
pyqtgraph (0.9.10 and above 0.9.8 is known not to work)
numpy
tifffile
argparse
tempfile
urllib
"""

__author__ = "Rob Campbell"
__license__ = "GPL v3"
__maintainer__ = "Rob Campbell"



from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph as pg
import numpy as np
import sys
import signal
import os.path


#lasagna modules
import ingredients                       # A set of classes for handling loaded data 
import handleIngredients                 # methods for handling ingredients (searching for them, adding then, etc)
import imageStackLoader                  # To load TIFF and MHD files
from lasagna_axis import projection2D    # The class that runs the axes
import imageProcessing                   # A potentially temporary module that houses general-purpose image processing code
import pluginHandler                     # Deals with finding plugins in the path, etc
import lasagna_mainWindow                 # Derived from designer .ui files built by pyuic
import lasagna_helperFunctions as lasHelp # Module the provides a variety of import functions (e.g. preference file handling)



#Parse command-line input arguments
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("-D", help="Load demo images", action="store_true")
parser.add_argument("-red", help="file name for red channel (if only this is specified we get a gray image)")
parser.add_argument("-green", help="file name for green channel. Only processed if a red channel was provided")
args = parser.parse_args()



fnames=[None,None]
if args.D==True:
    import tempfile
    import urllib

    fnames = [tempfile.gettempdir()+os.path.sep+'reference.tiff',
              tempfile.gettempdir()+os.path.sep+'sample.tiff']

    loadUrl = 'http://mouse.vision/lasagna/'
    for fname in fnames:
        if not os.path.exists(fname):
            url = loadUrl + fname.split(os.path.sep)[-1]
            print 'Downloading %s to %s' % (url,fname)
            urllib.urlretrieve(url,fname)
    
else:
    if args.red != None:
        fnames[0] =args.red
    if args.green != None:
        fnames[1] =args.green
    





# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#Set up the figure window
class lasagna(QtGui.QMainWindow, lasagna_mainWindow.Ui_lasagna_mainWindow):

    def __init__(self, parent=None):
        """
        Create default values for properties then call initialiseUI to set up main window
        """
        super(lasagna, self).__init__(parent)

        #Create widgets defined in the designer file
        #self.win = QtGui.QMainWindow()
        self.setupUi(self)
        self.show()


        #Misc. window set up 
        self.setWindowTitle("Lasagna - 3D sectioning volume visualiser")
        self.recentLoadActions = [] 
        self.updateRecentlyOpenedFiles()
        
        #We will maintain a list of classes of loaded items that can be added to plots
        self.ingredients = [] 

        #set up axes 
        #TODO: could more tightly integrate these objects with the main window so no need to pass many of these args?
        #TODO: stop calling these three views by thei neuroanatomical names. These can be labels, but shouldn't be harcoded as the
        #      names of the object instances
        print ""
        self.axes2D = [
                projection2D(self.graphicsView_1, ingredients=self.ingredients, axisRatio=float(self.axisRatioLineEdit_1.text()), axisToPlot=0),
                projection2D(self.graphicsView_2, ingredients=self.ingredients, axisRatio=float(self.axisRatioLineEdit_2.text()), axisToPlot=1),
                projection2D(self.graphicsView_3, ingredients=self.ingredients, axisRatio=float(self.axisRatioLineEdit_3.text()), axisToPlot=2)
                ]
        print ""


        #Establish links between projections for panning and zooming using lasagna_viewBox.linkedAxis
        self.axes2D[0].view.getViewBox().linkedAxis = {
                    self.axes2D[1].view.getViewBox(): {'linkX':None, 'linkY':'y', 'linkZoom':True}  ,
                    self.axes2D[2].view.getViewBox(): {'linkX':'x', 'linkY':None, 'linkZoom':True} 
                 }

        self.axes2D[1].view.getViewBox().linkedAxis = {
                    self.axes2D[0].view.getViewBox(): {'linkX':None, 'linkY':'y', 'linkZoom':True}  ,
                    self.axes2D[2].view.getViewBox(): {'linkX':'y', 'linkY':None, 'linkZoom':True} 
                 }

        self.axes2D[2].view.getViewBox().linkedAxis = {
                    self.axes2D[0].view.getViewBox(): {'linkX':'x', 'linkY':None, 'linkZoom':True}  ,
                    self.axes2D[1].view.getViewBox(): {'linkX':None, 'linkY':'x', 'linkZoom':True} 
                 }


        #Establish links between projections for scrolling through slices [implemented by signals in main() after the GUI is instantiated]
        self.axes2D[0].linkedXprojection = self.axes2D[2]
        self.axes2D[0].linkedYprojection = self.axes2D[1]

        self.axes2D[2].linkedXprojection = self.axes2D[0]
        self.axes2D[2].linkedYprojection = self.axes2D[1]

        self.axes2D[1].linkedXprojection = self.axes2D[2]
        self.axes2D[1].linkedYprojection = self.axes2D[0]



        #UI elements updated during mouse moves over an axis
        self.crossHairVLine = None
        self.crossHairHLine = None
        self.showCrossHairs = lasHelp.readPreference('showCrossHairs')
        self.mouseX = None
        self.mouseY = None
        self.pixelValue = None
        self.statusBarText = None

        #Lists of functions that are used as hooks for plugins to modify the behavior of built-in methods.
        #Hooks are named using the following convention: <lasagnaMethodName_[Start|End]> 
        #So:
        # 1. It's obvious which method will call a given hook list. 
        # 2. _Start indicates the hook will run at the top of the method, potentially modifying all
        #    subsequent behavior of the method.
        # 3. _End indicates that the hook will run at the end of the method, appending its functionality
        #    to whatever the method normally does. 
        self.hooks = {
            'updateStatusBar_End'           :   [] ,
            'loadBaseImageStack_Start'      :   [] ,
            'loadBaseImageStack_End'        :   [] ,
            'showBaseStackLoadDialog_Start' :   [] ,
            'showBaseStackLoadDialog_End'   :   [] ,
            'removeCrossHairs_Start'        :   [] , 
            'showFileLoadDialog_Start'      :   [] ,
            'showFileLoadDialog_End'        :   [] ,
            'updateMainWindowOnMouseMove_Start' : [] ,
            'updateMainWindowOnMouseMove_End'   : []
                    }


        #Add load actions to the Load ingredients sub-menu
        self.loadActions = [] #actions must be attached to the lasagna object or they won't function
        from IO import loadOverlayImageStack
        self.loadActions.append(loadOverlayImageStack.loadOverlayImageStack(self))
 
        # Link other menu signals to slots
        self.actionOpen.triggered.connect(self.showBaseStackLoadDialog)
        self.actionQuit.triggered.connect(self.quitLasagna)


        # Link toolbar signals to slots
        self.actionResetAxes.triggered.connect(self.resetAxes)
        

        #Link tabbed view items to slots
        #TODO: set up as one slot that receives an argument telling it which axis ratio was changed
        self.axisRatioLineEdit_1.textChanged.connect(self.axisRatio1Slot)
        self.axisRatioLineEdit_2.textChanged.connect(self.axisRatio2Slot)
        self.axisRatioLineEdit_3.textChanged.connect(self.axisRatio3Slot)
        self.logYcheckBox.clicked.connect(self.plotImageStackHistogram)



        #Plugins menu and initialisation
        # 1. Get a list of all plugins in the plugins path and add their directories to the Python path
        pluginPaths = lasHelp.readPreference('pluginPaths')

        plugins, pluginPaths = pluginHandler.findPlugins(pluginPaths)
        print "Adding plugin paths to Python path"
        print pluginPaths
        [sys.path.append(p) for p in pluginPaths] #append

        # 2. Add each plugin to a dictionary where the keys are plugin name and values are instances of the plugin. 
        print ""
        self.plugins = {} #A dictionary where keys are plugin names and values are plugin classes or plugin instances
        self.pluginActions = {} #A dictionary where keys are plugin names and values are QActions associated with a plugin
        for thisPlugin in plugins:

            #Get the module name and class
            pluginClass, pluginName = pluginHandler.getPluginInstanceFromFileName(thisPlugin,None) 

            #create instance of the plugin object and add to the self.plugins dictionary
            print "Creating reference to class " + pluginName +  ".plugin"
            self.plugins[pluginName] = pluginClass.plugin

            #create an action associated with the plugin and add to the self.pluginActions dictionary
            print "Creating menu QAction for " + pluginName 
            self.pluginActions[pluginName] = QtGui.QAction(pluginName,self)
            self.pluginActions[pluginName].setObjectName(pluginName)
            self.pluginActions[pluginName].setCheckable(True) #so we have a checkbox next to the menu entry

            self.menuPlugins.addAction(self.pluginActions[pluginName]) #add action to the plugins menu
            self.pluginActions[pluginName].triggered.connect(self.startStopPlugin) #Connect this action's signal to the slot


        print ""


        self.statusBar.showMessage("Initialised")






    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # Plugin-related methods
    def startStopPlugin(self):
        pluginName = str(self.sender().objectName()) #Get the name of the action that sent this signal

        if self.pluginActions[pluginName].isChecked():
           self.startPlugin(pluginName)
        else:
            self.stopPlugin(pluginName)                    


    def startPlugin(self,pluginName):
        print "Starting " + pluginName
        self.plugins[pluginName] = self.plugins[pluginName](self) #Create an instance of the plugin object 


    def stopPlugin(self,pluginName):
        print "Stopping " + pluginName
        self.plugins[pluginName].closePlugin() #tidy up the plugin
        #delete the plugin instance and replace it in the dictionary with a reference (that what it is?) to the class
        #NOTE: plugins with a window do not run the following code when the window is closed. They should, however, 
        #detach hooks (unless the plugin author forgot to do this)
        del(self.plugins[pluginName])
        pluginClass, pluginName = pluginHandler.getPluginInstanceFromFileName(pluginName+".py",None) 
        self.plugins[pluginName] = pluginClass.plugin


    def runHook(self,hookArray):
        """
        loops through list of functions and runs them
        """
        if len(hookArray) == 0 :
            return

        for thisHook in hookArray:
            try:
                if thisHook == None:
                    print "Skipping empty hook in hook list"
                    continue
                else:
                     thisHook()
            except:
                print  "Error running plugin method " + str(thisHook) 
                raise

  
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # File menu and methods associated with loading the base image stack. 
  
    def loadBaseImageStack(self,fnameToLoad):
        """
        Loads the base image image stack. The base image stack is the one which will appear as gray
        if it is the only stack loaded. This function wipes and data that have already been loaded. Any overlays that 
        are present will be removed when this function runs. 
        """

        self.runHook(self.hooks['loadBaseImageStack_Start'])
        print "Loading " + fnameToLoad
        loadedImageStack = self.loadImageStack(fnameToLoad)

        # Set up default values in tabs
        axRatio = imageStackLoader.getVoxelSpacing(fnameToLoad)
        self.axisRatioLineEdit_1.setText( str(axRatio[0]) )
        self.axisRatioLineEdit_2.setText( str(axRatio[1]) )
        self.axisRatioLineEdit_3.setText( str(axRatio[2]) )


        #The paradigm is that other data are plotted over or otherwise added *to* a baseImage.
        #so we need to remove other crap. 
        # TODO: AXIS For now we just remove all image stacks in future there will be other classes
        #       and these are not handled currently. 
        imageStacks = handleIngredients.returnIngredientByType('imagestack',self.ingredients)
        if imageStacks != False:
            for thisStack in imageStacks: #remove imagestacks from plot axes
                [axis.removeItemFromPlotWidget(thisStack.objectName) for axis in self.axes2D]

        #remove imagestacks from ingredient list
        self.ingredients = handleIngredients.removeIngredientByType('imagestack',self.ingredients)

        #Add to the ingredients list
        objName='baseImage'
        self.ingredients = handleIngredients.addIngredient(self.ingredients, objectName=objName , 
                                                              kind='imagestack'       , 
                                                              data=loadedImageStack   , 
                                                              fname=fnameToLoad)

        #Add plot items to axes so that they become available for plotting
        [axis.addItemToPlotWidget(handleIngredients.returnIngredientByName(objName,self.ingredients)) for axis in self.axes2D]

        #remove any existing range highlighter on the histogram. We do this because different images
        #will likely have different default ranges
        if hasattr(self,'plottedIntensityRegionObj'):
            del self.plottedIntensityRegionObj

        self.runHook(self.hooks['loadBaseImageStack_End'])


    def showBaseStackLoadDialog(self):
        """
        This slot brings up the file load dialog and gets the file name.
        If the file name is valid, it loads the base stack using the loadBaseImageStack method.
        We split things up so that the base stack can be loaded from the command line, 
        or from a plugin without going via the load dialog. 
        """
        self.runHook(self.hooks['showBaseStackLoadDialog_Start'])

        fname = self.showFileLoadDialog()
        if fname == None:
            return

        if os.path.isfile(fname): 
            self.loadBaseImageStack(str(fname))
            self.initialiseAxes()
        else:
            self.statusBar.showMessage("Unable to find " + str(fname))

        self.runHook(self.hooks['showBaseStackLoadDialog_End'])


    # -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  
    #Code to handle generic file loading, dialogs, etc
    def loadImageStack(self,thisFname):
        """
        Loads a generic image stack (defined by the string thisFname) and returns it as an output argument
        """
        if not os.path.isfile(thisFname):
            msg = 'Unable to find ' + thisFname
            print msg
            self.statusBar.showMessage(msg)
            return

        #TODO: The axis swap likely shouldn't be hard-coded here
        return imageStackLoader.loadStack(thisFname).swapaxes(1,2) 
 

    def showFileLoadDialog(self):
        """
        Bring up the file load dialog. Return the file name. Update the last used path. 
        """
        self.runHook(self.hooks['showFileLoadDialog_Start'])

        fname = QtGui.QFileDialog.getOpenFileName(self, 'Open file', lasHelp.readPreference('lastLoadDir'),  "Images (*.mhd *.mha *.tiff *.tif)" )
        fname = str(fname)
        if len(fname) == 0:
            return None

        #Update last loaded directory 
        lasHelp.preferenceWriter('lastLoadDir', lasHelp.stripTrailingFileFromPath(fname))

        #Keep a track of the last loaded files
        recentlyLoaded = lasHelp.readPreference('recentlyLoadedFiles')
        n = lasHelp.readPreference('numRecentFiles')
        recentlyLoaded.append(fname)
        recentlyLoaded = list(set(recentlyLoaded)) #get remove repeats (i.e. keep only unique values)

        while len(recentlyLoaded)>n:
            recentlyLoaded.pop(-1)

        lasHelp.preferenceWriter('recentlyLoadedFiles',recentlyLoaded)
        self.updateRecentlyOpenedFiles()

        self.runHook(self.hooks['showFileLoadDialog_End'])

        return fname


    def updateRecentlyOpenedFiles(self):
        """
        Updates the list of recently opened files
        """
        recentlyLoadedFiles = lasHelp.readPreference('recentlyLoadedFiles')

        #Remove existing actions if present
        if len(self.recentLoadActions)>0 and len(recentlyLoadedFiles)>0:
            for thisAction in self.recentLoadActions:
                self.menuOpen_recent.removeAction(thisAction)
            self.recentLoadActions = []

        for thisFile in recentlyLoadedFiles:
            self.recentLoadActions.append(self.menuOpen_recent.addAction(thisFile)) #add action to list
            self.recentLoadActions[-1].triggered.connect(self.loadRecentFileSlot) #link it to a slot
            #NOTE: tried the lambda approach but it always assigns the last file name to the list to all signals
            #      http://stackoverflow.com/questions/940555/pyqt-sending-parameter-to-slot-when-connecting-to-a-signal

    def loadRecentFileSlot(self):
        """
        load a file from recently opened list
        """
        fname = str(self.sender().text())
        self.loadBaseImageStack(fname)
        self.initialiseAxes()


    def quitLasagna(self):
        """
        Neatly shut down the GUI
        """
        #Loop through and shut plugins. 
        for thisPlugin in self.pluginActions.keys():
            if self.pluginActions[thisPlugin].isChecked():
                if not self.plugins[thisPlugin].confirmOnClose: #TODO: handle cases where plugins want confirmation to close
                    self.stopPlugin(thisPlugin)

        QtGui.qApp.quit()

    def closeEvent(self, event):
        self.quitLasagna()
    # -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -           


    def clearAxes(self):
        """
        Wipes image stack and clears plot windows
        """
        #TODO: AXIS this function should remove ingredients from each axis 
        print "NEED TO WRITE lasagna.clearAxes!!"
        [axis.removeItemsFromPlotWidget() for axis in self.axes2D]


    def resetAxes(self):
        """
        Set X and Y limit of each axes to fit the data
        """
        if handleIngredients.returnIngredientByName('baseImage',self.ingredients)==False:
            return
        [axis.resetAxes() for axis in self.axes2D]


    def initialiseAxes(self):
        """
        Initial display of images in axes and also update other parts of the GUI. 
        """
        if handleIngredients.returnIngredientByName('baseImage',self.ingredients)==False:
            return

        #show default images
        print "updating axes with added ingredients"
        [axis.updatePlotItems_2D(self.ingredients) for axis in self.axes2D]

        #initialize cross hair
        if self.showCrossHairs:
            if self.crossHairVLine==None:
                self.crossHairVLine = pg.InfiniteLine(angle=90, movable=False)
                self.crossHairVLine.objectName = 'crossHairVLine'
            if self.crossHairHLine==None:
                self.crossHairHLine = pg.InfiniteLine(angle=0, movable=False)
                self.crossHairHLine.objectName = 'crossHairHLine'

        self.plotImageStackHistogram()

        #TODO: turn into list by making the axisRatioLineEdits a list
        self.axes2D[0].view.setAspectLocked(True, float(self.axisRatioLineEdit_1.text()))
        self.axes2D[1].view.setAspectLocked(True, float(self.axisRatioLineEdit_2.text()))
        self.axes2D[2].view.setAspectLocked(True, float(self.axisRatioLineEdit_3.text()))
        
        self.resetAxes()
        self.updateDisplayText()

    def updateDisplayText(self):
        """
        Loop through all ingredients and print out their type the file name
        """
        displayTxt=''
        for thisIngredient in self.ingredients:
            displayTxt = "%s<b>%s</b>: %s<br>" % (displayTxt, thisIngredient.objectName, thisIngredient.fname())

        self.infoTextPanel.setText(displayTxt)




    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # Slots for axis tab
    # TODO: incorporate these three slots into one
    def axisRatio1Slot(self):
        """
        Set axis ratio on plot 1
        """
        self.axes2D[0].view.setAspectLocked( True, float(self.axisRatioLineEdit_1.text()) )


    def axisRatio2Slot(self):
        """
        Set axis ratio on plot 2
        """
        self.axes2D[1].view.setAspectLocked( True, float(self.axisRatioLineEdit_2.text()) )


    def axisRatio3Slot(self):
        """
        Set axis ratio on plot 3
        """
        self.axes2D[2].view.setAspectLocked( True, float(self.axisRatioLineEdit_3.text()) )


    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # Methods that are run during navigation
    def removeCrossHairs(self):
        """
        Remove the cross hairs from all plots
        """
        # NOTE: I'm a little unhappy about this as I don't understand what's going on. 
        # I've noticed that removing the cross hairs from any one plot is sufficient to remove
        # them from the other two. However, if all three axes are not explicitly removed I've
        # seen peculiar behavior with plugins that query the PlotWidgets. RAAC 21/07/2015

        self.runHook(self.hooks['removeCrossHairs_Start']) #This will be run each time a plot is updated

        if not self.showCrossHairs:
            return

        [axis.removeItemFromPlotWidget(self.crossHairVLine) for axis in self.axes2D]
        [axis.removeItemFromPlotWidget(self.crossHairHLine) for axis in self.axes2D]


    def constrainMouseLocationToImage(self,thisImage):
        """
        Ensures that the values of self.mouseX and self.mouseY, which are the X and Y positions
        of the mouse pointer on the current image, do not exceed the dimensions of the image.
        This is used to avoid asking for image slices that do not exist.
        NOTE: constraints on plotting are also imposed in lasagna_axis.updatePlotItems_2D
        """
        #I think the following would be better placed in getMousePositionInCurrentView, but this could work also. 
        if self.mouseX<0:
            self.mouseX=0

        if self.mouseY<0:
            self.mouseY=0

        if self.mouseX>=thisImage.shape[0]:
            self.mouseX=thisImage.shape[0]-1

        if self.mouseY>=thisImage.shape[1]:
            self.mouseY=thisImage.shape[1]-1


    def updateCrossHairs(self):
        """
        Update the drawn cross hairs on the current image 
        """
        if not self.showCrossHairs:
            return
        self.crossHairVLine.setPos(self.mouseX+0.5) #Add 0.5 to add line to middle of pixel
        self.crossHairHLine.setPos(self.mouseY+0.5)


    def updateStatusBar(self,thisImage):
        """
        Update the text on the status bar based on the current mouse position 
        """
        X = self.mouseX
        Y = self.mouseY

        #get pixel value of red layer
        self.pixelValue = thisImage[X,Y] 
        if isinstance(self.pixelValue,np.ndarray): #so this works with both RGB and monochrome images
            self.pixelValue = int(self.pixelValue[0])

        self.statusBarText = "X=%d, Y=%d, val=%d" % (X,Y,self.pixelValue)
        self.runHook(self.hooks['updateStatusBar_End']) #Hook goes here to modify or append message
        self.statusBar.showMessage(self.statusBarText)


    def updateMainWindowOnMouseMove(self,axis):
        """
        Update UI elements on the screen (but not the plotted images) as the user moves the mouse across an axis
        """
        self.runHook(self.hooks['updateMainWindowOnMouseMove_Start']) #Runs each time the views are updated

        thisImage = lasHelp.findPyQtGraphObjectNameInPlotWidget(axis.view,'baseImage').image

        self.constrainMouseLocationToImage(thisImage)
        self.updateCrossHairs()
        self.updateStatusBar(thisImage)
        self.runHook(self.hooks['updateMainWindowOnMouseMove_End']) #Runs each time the views are updated



    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # Image Tab methods
    # These methods are involved with the tabs to the left of the three view axes

    def plotImageStackHistogram(self):
        """
        Plot the image stack histogram in a PlotWidget to the left of the three image views.
        This function is called when the plot is first set up and also when the log Y
        checkbox is checked or unchecked
        """

        #TODO: AXIS - eventually have different histograms for each color channel
        img = lasHelp.findPyQtGraphObjectNameInPlotWidget(self.axes2D[0].view,'baseImage')
        x,y = img.getHistogram()

        if self.logYcheckBox.isChecked():
            y=np.log10(y+0.1)

        #Determine max value on the un-logged y values. Do not run this again if the 
        #graph is merely updated. This will only run if a new imageStack was loaded
        if not hasattr(self,'plottedIntensityRegionObj'):
            baseImage=handleIngredients.returnIngredientByName('baseImage',self.ingredients)
            calcuMaxVal = baseImage.defaultHistRange() #return a reasonable value for the maximum

      
        self.intensityHistogram.clear()
        ## Using stepMode=True causes the plot to draw two lines for each sample but it needs X to be longer than Y by 1
        self.intensityHistogram.plot(x, y, stepMode=False, fillLevel=0, brush=(255,0,255,80))

        self.intensityHistogram.showGrid(x=True,y=True,alpha=0.33)
        self.intensityHistogram.setLimits(yMin=0, xMin=0)

        #The object that represents the plotted intensity range is only set up the first time the 
        #plot is made or following a new base image being loaded (any existing plottedIntensityRegionObj
        #is deleted at base image load time.)
        if not hasattr(self,'plottedIntensityRegionObj'):
            self.plottedIntensityRegionObj = pg.LinearRegionItem()
            self.plottedIntensityRegionObj.setZValue(10)
            self.setIntensityRange( (0,calcuMaxVal) )
            self.plottedIntensityRegionObj.sigRegionChanged.connect(self.updateAxisLevels) #link signal slot

        # Add to the ViewBox but exclude it from auto-range calculations.
        self.intensityHistogram.addItem(self.plottedIntensityRegionObj, ignoreBounds=True)


    def setIntensityRange(self,intRange=(0,2**12)):
        """
        Set the intensity range of the images and update the axis labels. 
        This is really just a convenience function with an easy to remember name.
        intRange is a tuple that is (minX,maxX)
        """
        self.plottedIntensityRegionObj.setRegion(intRange)
        self.updateAxisLevels()


    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # Slots relating to plotting
    def updateAxisLevels(self):
        #TODO: AXIS - decide what to do with minMax. 
        #Have the object set it? Doing it here by directly manipulating the item seems wrong
        minX, maxX = self.plottedIntensityRegionObj.getRegion()

        #Get all imagestacks
        allImageStacks = handleIngredients.returnIngredientByType('imagestack',self.ingredients)

        #Loop through all imagestacks and set their levels in each axis
        for thisImageStack in allImageStacks:
            objectName=thisImageStack.objectName

            for thisAxis in self.axes2D:
                img = lasHelp.findPyQtGraphObjectNameInPlotWidget(thisAxis.view,objectName)
                img.setLevels([minX,maxX]) #Sets levels immediately


            thisImageStack.minMax=[minX,maxX] #ensures levels stay set during all plot updates that follow

        


    def mouseMovedCoronal(self,evt):
        if handleIngredients.returnIngredientByName('baseImage',self.ingredients)==False:
            return


        pos = evt[0] #Using signal proxy turns original arguments into a tuple
        self.removeCrossHairs()

        if self.axes2D[0].view.sceneBoundingRect().contains(pos):
            #TODO: figure out how to integrate this into object, because when we have that, we could
            #      do everything but the axis linking in the object. 
            if self.showCrossHairs:
                self.axes2D[0].view.addItem(self.crossHairVLine, ignoreBounds=True)
                self.axes2D[0].view.addItem(self.crossHairHLine, ignoreBounds=True)

            (self.mouseX,self.mouseY)=self.axes2D[0].getMousePositionInCurrentView(pos)
            self.updateMainWindowOnMouseMove(self.axes2D[0]) #Update UI elements 
            self.axes2D[0].updateDisplayedSlices_2D(self.ingredients,(self.mouseX,self.mouseY)) #Update displayed slice


    def mouseMovedSaggital(self,evt):
        if handleIngredients.returnIngredientByName('baseImage',self.ingredients)==False:
            return

        pos = evt[0]
        self.removeCrossHairs()

        if self.axes2D[1].view.sceneBoundingRect().contains(pos):
            if self.showCrossHairs:
                self.axes2D[1].view.addItem(self.crossHairVLine, ignoreBounds=True)
                self.axes2D[1].view.addItem(self.crossHairHLine, ignoreBounds=True)

            (self.mouseX,self.mouseY)=self.axes2D[1].getMousePositionInCurrentView(pos)
            self.updateMainWindowOnMouseMove(self.axes2D[1])
            self.axes2D[1].updateDisplayedSlices_2D(self.ingredients,(self.mouseX,self.mouseY))

        
    def mouseMovedTransverse(self,evt):
        if handleIngredients.returnIngredientByName('baseImage',self.ingredients)==False:
            return

        pos = evt[0]  
        self.removeCrossHairs()

        if self.axes2D[2].view.sceneBoundingRect().contains(pos):
            if self.showCrossHairs:
                self.axes2D[2].view.addItem(self.crossHairVLine, ignoreBounds=True) 
                self.axes2D[2].view.addItem(self.crossHairHLine, ignoreBounds=True)

            (self.mouseX,self.mouseY)=self.axes2D[2].getMousePositionInCurrentView(pos)
            self.updateMainWindowOnMouseMove(self.axes2D[2])
            self.axes2D[2].updateDisplayedSlices_2D(self.ingredients,(self.mouseX,self.mouseY))






# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

def main(fnames=[None,None]):
    app = QtGui.QApplication([])

    tasty = lasagna()

    #Load stacks from command line input if any was provided
    if not fnames[0]==None:
        print "Loading " + fnames[0]
        tasty.loadBaseImageStack(fnames[0])
    
        if not fnames[1]==None:
            print "Loading " + fnames[1]
            tasty.loadActions[0].load(fnames[1]) #TODO: we need a nice way of finding load actions by name

        tasty.initialiseAxes()


    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # Link slots to signals
    #connect views to the mouseMoved slot. After connection this runs in the background. 
    #TODO: figure out why returning an argument is crucial even though we never use it
    #TODO: set up with just one slot that accepts arguments
    proxy1=pg.SignalProxy(tasty.axes2D[0].view.scene().sigMouseMoved, rateLimit=30, slot=tasty.mouseMovedCoronal)
    proxy2=pg.SignalProxy(tasty.axes2D[1].view.scene().sigMouseMoved, rateLimit=30, slot=tasty.mouseMovedSaggital)
    proxy3=pg.SignalProxy(tasty.axes2D[2].view.scene().sigMouseMoved, rateLimit=30, slot=tasty.mouseMovedTransverse)

    sys.exit(app.exec_())

## Start Qt event loop unless running in interactive mode.
if __name__ == '__main__':
    main(fnames=fnames)


    """
    original_sigint = signal.getsignal(signal.SIGINT)
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
    """