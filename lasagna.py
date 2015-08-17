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



from PyQt4 import QtCore, QtGui
import pyqtgraph as pg
import numpy as np
import sys
import signal
import os.path


#lasagna modules
import ingredients                       # A set of classes for handling loaded data 
import imageStackLoader                  # To load TIFF and MHD files
import lasagna_axis                      # The class that runs the axes
import imageProcessing                   # A potentially temporary module that houses general-purpose image processing code
import pluginHandler                     # Deals with finding plugins in the path, etc
import lasagna_mainWindow                 # Derived from designer .ui files built by pyuic
import lasagna_helperFunctions as lasHelp # Module the provides a variety of import functions (e.g. preference file handling)
from alert import alert                  # Class used to bring up a warning box

#The following imports are made here in order to ensure Lasagna builds as a standlone
#application on the Mac with py2app
import csv
import lasagna_plugin #Needed here to build a standalone version 
#import tifffile #used currently for the LSM reading
import ARA #TODO: find out what calls this and try to weed it out. 



#Parse command-line input arguments
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("-D", help="Load demo images", action="store_true")
parser.add_argument("-im", nargs='+', help="file name(s) of image stacks to load")
parser.add_argument("-P", help="start plugin of this name. use string from plugins menu as the argument")
args = parser.parse_args()



fnames=[None,None]
pluginToStart = args.P
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
    
elif args.im != None:
    fnames = args.im
  
    





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
        self.app=None #The QApplication handle kept here


        #Misc. window set up 
        self.setWindowTitle("Lasagna - 3D sectioning volume visualiser")
        self.recentLoadActions = [] 
        self.updateRecentlyOpenedFiles()
        
        #We will maintain a list of classes of loaded items that can be added to plots
        self.ingredientList = [] 


        #set up axes 
        #Turn axisRatioLineEdit_x elements into a list to allow functions to iterate across them
        self.axisRatioLineEdits = [self.axisRatioLineEdit_1,self.axisRatioLineEdit_2,self.axisRatioLineEdit_3]

        self.graphicsViews = [self.graphicsView_1, self.graphicsView_2, self.graphicsView_3] #These are the graphics_views from the UI file
        self.axes2D=[]
        print ""
        for ii in range(len(self.graphicsViews)):
            self.axes2D.append(lasagna_axis.projection2D(self.graphicsViews[ii], self, axisRatio=float(self.axisRatioLineEdits[ii].text()), axisToPlot=ii))
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
            'loadImageStack_Start'          :   [] ,
            'loadImageStack_End'            :   [] ,
            'showStackLoadDialog_Start'     :   [] ,
            'showStackLoadDialog_End'       :   [] ,
            'removeCrossHairs_Start'        :   [] , 
            'showFileLoadDialog_Start'      :   [] ,
            'showFileLoadDialog_End'        :   [] ,
            'loadRecentFileSlot_Start'      :   [] ,
            'updateMainWindowOnMouseMove_Start' : [] ,
            'updateMainWindowOnMouseMove_End'   : []
                    }


        #Handle IO plugins. For instance these are the loaders that handle different data types
        #and different loading actions. 
        IO_Paths = lasHelp.readPreference('IO_modulePaths') #directories containing IO modules
        print "Adding IO module paths to Python path"
        IO_plugins, IO_pluginPaths = pluginHandler.findPlugins(IO_Paths)
        for p in IO_Paths:
            sys.path.append(p) #append to system path
            print p

        #Add *load actions* to the Load ingredients sub-menu and add loader modules here 
        #TODO: currently we only have code to handle load actions as no save actions are available
        self.loadActions = {} #actions must be attached to the lasagna object or they won't function
        for thisIOmodule in IO_plugins:
            print "Adding %s to load menu" % thisIOmodule
            IOclass,IOname=pluginHandler.getPluginInstanceFromFileName(thisIOmodule,attributeToImport='loaderClass')
            thisInstance = IOclass(self)
            self.loadActions[thisInstance.objectName] = thisInstance

        print ""

        # Link other menu signals to slots
        self.actionOpen.triggered.connect(self.showStackLoadDialog)
        self.actionQuit.triggered.connect(self.quitLasagna)
        self.actionAbout.triggered.connect(self.about_slot)

        # Link toolbar signals to slots
        self.actionResetAxes.triggered.connect(self.resetAxes)

        #Link tabbed view items to slots
        #TODO: set up as one slot that receives an argument telling it which axis ratio was changed
        self.axisRatioLineEdit_1.textChanged.connect(self.axisRatio1Slot)
        self.axisRatioLineEdit_2.textChanged.connect(self.axisRatio2Slot)
        self.axisRatioLineEdit_3.textChanged.connect(self.axisRatio3Slot)

        #Flip axis 
        self.pushButton_FlipView1.released.connect(lambda: self.flipAxis_Slot(0))
        self.pushButton_FlipView2.released.connect(lambda: self.flipAxis_Slot(1))
        self.pushButton_FlipView3.released.connect(lambda: self.flipAxis_Slot(2))


        #Image tab stuff
        self.logYcheckBox.clicked.connect(self.plotImageStackHistogram)
        self.imageStackLayers_Model = QtGui.QStandardItemModel(self.imageStackLayers_TreeView)
        labels = QtCore.QStringList("Name") 
        self.imageStackLayers_Model.setHorizontalHeaderLabels(labels)
        self.imageStackLayers_TreeView.setModel(self.imageStackLayers_Model)
        self.imageStackLayers_TreeView.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.imageStackLayers_TreeView.customContextMenuRequested.connect(self.layersMenuStacks)
        #self.imageStackLayers_TreeView.setColumnWidth(0,200)

        QtCore.QObject.connect(self.imageStackLayers_TreeView.selectionModel(), QtCore.SIGNAL("selectionChanged(QItemSelection, QItemSelection)"), self.plotImageStackHistogram) 


        #Points tab stuff
        self.points_Model = QtGui.QStandardItemModel(self.points_TreeView)
        labels = QtCore.QStringList("Name") 
        self.points_Model.setHorizontalHeaderLabels(labels)
        self.points_TreeView.setModel(self.points_Model)
        self.points_TreeView.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.points_TreeView.customContextMenuRequested.connect(self.layersMenuPoints)
        [self.markerSymbol_comboBox.addItem(pointType) for pointType in lasHelp.readPreference('symbolOrder')] #populate with markers
        self.markerSymbol_comboBox.activated.connect(self.markerSymbol_comboBox_slot)
        self.markerSize_spinBox.valueChanged.connect(self.markerSize_spinBox_slot)
        self.markerAlpha_spinBox.valueChanged.connect(self.markerAlpha_spinBox_slot)
        self.markerAlpha_spinBox.valueChanged.connect(self.markerAlpha_spinBox_slot)        
        self.markerColor_pushButton.released.connect(self.markerColor_pushButton_slot)
        self.addLines_checkBox.stateChanged.connect(self.addLines_checkBox_slot)
        #add the z-points spinboxes to a list to make them indexable
        self.viewZ_spinBoxes = [self.view1Z_spinBox, self.view2Z_spinBox, self.view3Z_spinBox]

        #Plugins menu and initialisation
        # 1. Get a list of all plugins in the plugins path and add their directories to the Python path
        pluginPaths = lasHelp.readPreference('pluginPaths')

        plugins, pluginPaths = pluginHandler.findPlugins(pluginPaths)
        print "Adding plugin paths to Python path:"
        self.pluginSubMenus = {}    
        for p in pluginPaths: #print plugin paths to screen, add to path, add as sub-dir names in Plugins menu
            print p
            sys.path.append(p)
            dirName = p.split(os.path.sep)[-1]
            self.pluginSubMenus[dirName] = QtGui.QMenu(self.menuPlugins)
            self.pluginSubMenus[dirName].setObjectName(dirName)
            self.pluginSubMenus[dirName].setTitle(dirName)
            self.menuPlugins.addAction(self.pluginSubMenus[dirName].menuAction())
            


        # 2. Add each plugin to a dictionary where the keys are plugin name and values are instances of the plugin. 
        print ""
        self.plugins = {} #A dictionary where keys are plugin names and values are plugin classes or plugin instances
        self.pluginActions = {} #A dictionary where keys are plugin names and values are QActions associated with a plugin
        for thisPlugin in plugins:

            #Get the module name and class
            pluginClass, pluginName = pluginHandler.getPluginInstanceFromFileName(thisPlugin,None) 

            #Get the name of the directory in which the plugin resides so we can add it to the right sub-menu
            dirName = os.path.dirname(pluginClass.__file__).split(os.path.sep)[-1]

            #create instance of the plugin object and add to the self.plugins dictionary
            print "Creating reference to class " + pluginName +  ".plugin"
            self.plugins[pluginName] = pluginClass.plugin

            #create an action associated with the plugin and add to the self.pluginActions dictionary
            print "Creating menu QAction for " + pluginName 
            self.pluginActions[pluginName] = QtGui.QAction(pluginName,self)
            self.pluginActions[pluginName].setObjectName(pluginName)
            self.pluginActions[pluginName].setCheckable(True) #so we have a checkbox next to the menu entry

            self.pluginSubMenus[dirName].addAction(self.pluginActions[pluginName]) #add action to the correct plugins sub-menu
            self.pluginActions[pluginName].triggered.connect(self.startStopPlugin) #Connect this action's signal to the slot


        print ""


        self.statusBar.showMessage("Initialised")



    # -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  - 
    def about_slot(self):
        """
        A simple about box
        """
        msg = "Lasagna - Rob Campbell<br>Basel - 2015"
        reply = QtGui.QMessageBox.question(self, 'Message', msg)


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
        try:
            self.plugins[pluginName].closePlugin() #tidy up the plugin
        except:
            print "failed to properly close plugin " + pluginName
        
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
  
    def loadImageStack(self,fnameToLoad):
        """
        Loads the base image image stack. The base image stack is the one which will appear as gray
        if it is the only stack loaded. This function wipes and data that have already been loaded. Any overlays that 
        are present will be removed when this function runs. 
        """

        self.runHook(self.hooks['loadImageStack_Start'])

        if not os.path.isfile(fnameToLoad):
            msg = 'Unable to find ' + fnameToLoad
            print msg
            self.statusBar.showMessage(msg)
            return False

        print "Loading image stack " + fnameToLoad
 
        #TODO: The axis swap likely shouldn't be hard-coded here
        loadedImageStack = imageStackLoader.loadStack(fnameToLoad).swapaxes(1,2) 
 
        if len(loadedImageStack)==0 and loadedImageStack==False:
            return

        # Set up default values in tabs
        # It's ok to load images of different sizes but their voxel sizes need to be the same
        axRatio = imageStackLoader.getVoxelSpacing(fnameToLoad)
        for ii in range(len(axRatio)):
            self.axisRatioLineEdits[ii].setText(str(axRatio[ii]))


        #Add to the ingredients list
        objName=fnameToLoad.split(os.path.sep)[-1]
        self.addIngredient(objectName=objName       , 
                           kind='imagestack'        , 
                           data=loadedImageStack    , 
                           fname=fnameToLoad)

        self.returnIngredientByName(objName).addToPlots() #Add item to all three 2D plots


        #If only one stack is present, we will display it as gray (see imagestack class)
        #if more than one stack has been added, we will colour successive stacks according
        #to the colorOrder preference in the parameter file
        stacks = self.stacksInTreeList()
        colorOrder = lasHelp.readPreference('colorOrder')

        if len(stacks)==2:
            self.returnIngredientByName(stacks[0]).lut=colorOrder[0]
            self.returnIngredientByName(stacks[1]).lut=colorOrder[1]
        elif len(stacks)>2:
            self.returnIngredientByName(stacks[len(stacks)-1]).lut=colorOrder[len(stacks)-1]

        #remove any existing range highlighter on the histogram. We do this because different images
        #will likely have different default ranges
        if hasattr(self,'plottedIntensityRegionObj'):
            del self.plottedIntensityRegionObj

        self.runHook(self.hooks['loadImageStack_End'])


    def showStackLoadDialog(self,triggered=None,fileFilter="Images (*.mhd *.mha *.tiff *.tif)"):
        """
        This slot brings up the file load dialog and gets the file name.
        If the file name is valid, it loads the base stack using the loadImageStack method.
        We split things up so that the base stack can be loaded from the command line, 
        or from a plugin without going via the load dialog. 
        
        triggered - just catches the input from the signal so we can set fileFilter
        """
        self.runHook(self.hooks['showStackLoadDialog_Start'])

        fname = self.showFileLoadDialog(fileFilter=fileFilter)
        if fname == None:
            return

        if os.path.isfile(fname): 
            self.loadImageStack(str(fname))
            self.initialiseAxes()
        else:
            self.statusBar.showMessage("Unable to find " + str(fname))

        self.runHook(self.hooks['showStackLoadDialog_End'])


    # -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  
    #Code to handle generic file loading, dialogs, etc

    def showFileLoadDialog(self, fileFilter="All files (*)" ):
        """
        Bring up the file load dialog. Return the file name. Update the last used path. 
        """
        self.runHook(self.hooks['showFileLoadDialog_Start'])
        print fileFilter
        fname = QtGui.QFileDialog.getOpenFileName(self, 'Open file', lasHelp.readPreference('lastLoadDir'), fileFilter)
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
        self.runHook(self.hooks['loadRecentFileSlot_Start'])
        fname = str(self.sender().text())
        self.loadImageStack(fname)
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
        sys.exit(0) #without this we get a big horrible error report on the Mac

    def closeEvent(self, event):
        self.quitLasagna()


    # -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  
    #Code to handle ingredients and modify GUI as they are added or removed
    """
    TODO: ingredients can only be handled if they are in the ingredients module
    ingredients defined in plugin directories, etc, can not be handled by this 
    module. This potentially makes plugin creation awkward as it couples it too
    strongly to the core code (new ingredients must be added to the ingredients
    module). This may turn out to not be a problem in practice, so we leave 
    things for now and play it by ear. 
    """
    #------------------------------------------------------------------------
    # PROTOTYPE CODE
    def layersMenuStacks(self,position): 
        menu = QtGui.QMenu()

        changeColorMenu = QtGui.QMenu("Change color",self)

        #action.triggered.connect(self.changeImageStackColorMap_Slot)

        for thisColor in lasHelp.readPreference('colorOrder'):
            action = QtGui.QAction(thisColor,self)
            #action.triggered.connect(lambda: self.changeImageStackColorMap_Slot(thisColor))
            action.triggered.connect(self.changeImageStackColorMap_Slot)
            changeColorMenu.addAction(action)

        menu.addAction(changeColorMenu.menuAction())

        action = QtGui.QAction("Delete",self)
        action.triggered.connect(self.deleteLayerStack_Slot)
        menu.addAction(action)
        menu.exec_(self.imageStackLayers_TreeView.viewport().mapToGlobal(position))


    def changeImageStackColorMap_Slot(self):
        color = str(self.sender().text())
        objName = self.selectedStackName()
        self.returnIngredientByName(objName).lut=color
        self.initialiseAxes()


    def deleteLayerStack_Slot(self):
        objName = self.selectedStackName()
        self.removeIngredientByName(objName)
        print "removed " + objName


    def stacksInTreeList(self):
        """
        Goes through the list of image stack layers in the QTreeView list 
        and pull out the names.
        """
        stacks=[]
        for ii in range(self.imageStackLayers_Model.rowCount()):
            stackName = self.imageStackLayers_Model.index(ii,0).data().toString()
            stacks.append(stackName)

        if len(stacks)>0:
            return stacks
        else:
            return False

    def selectedStackName(self):
        """
        Return the name of the selected image stack. If no stack selected, returns the first stack in the list
        """
        if self.imageStackLayers_Model.rowCount()==0:
            print "lasagna.selectedStackName finds no image stacks in list"
            return False

        #Highlight the first row if nothing is selected (which shouldn't ever happen)        
        if len(self.imageStackLayers_TreeView.selectedIndexes())==0:
            firstItem  = self.imageStackLayers_Model.index(0,0)
            self.imageStackLayers_TreeView.setCurrentIndex(firstItem)
            print "lasagna.selectedStackName forced highlighting of first image stack"


        return str( self.imageStackLayers_TreeView.selectedIndexes()[0].data().toString() )

    #------------------------------------------------------------------------

    def addIngredient(self, kind='', objectName='', data=None, fname=''):
        """
        Adds an ingredient to the list of ingredients.
        Scans the list of ingredients to see if an ingredient is already present. 
        If so, it removes it before adding a new one with the same name. 
        ingredients are classes that are defined in the ingredients package
        """

        print "Adding ingredient " + objectName

        if len(kind)==0:
            print "ERROR: no ingredient kind specified"
            return

        #Do not attempt to add an ingredient if its class is not defined
        if not hasattr(ingredients,kind):
            print "ERROR: ingredients module has no class '%s'" % kind
            return

        #If an ingredient with this object name is already present we delete it
        self.removeIngredientByName(objectName)

        #Get ingredient of this class from the ingredients package
        ingredientClassObj = getattr(getattr(ingredients,kind),kind) #make an ingredient of type "kind"
        self.ingredientList.append(ingredientClassObj(
                            parent=self,
                            fnameAbsPath=fname,
                            data=data,
                            objectName=objectName
                    )
                )




    def removeIngredient(self,ingredientInstance):
        """
        Removes the ingredient "ingredientInstance" from self.ingredientList
        This method is called by the two following methods that remove based on
        ingredient name or type         
        """
        ingredientInstance.removePlotItem() #remove from axes
        self.ingredientList.remove(ingredientInstance) 
        ingredientInstance.removeFromList() #remove ingredient from the list with which it is associated        

    def removeIngredientByName(self,objectName):
        """
        Finds ingredient by name and removes it from the list
        """

        verbose = False
        if len(self.ingredientList)==0:
            if verbose:
                print "lasagna.removeIngredientByType finds no ingredients in list!"
            return

        removedIngredient=False
        for thisIngredient in self.ingredientList[:]:
            if thisIngredient.objectName == objectName:
                if verbose:
                    print 'Removing ingredient ' + objectName
                self.removeIngredient(thisIngredient)
                removedIngredient=True

        if removedIngredient == False & verbose==True:
            print "** Failed to remove ingredient %s **" % objectName

    def removeIngredientByType(self,ingredientType):
        """
        Finds ingredient by type and removes it
        """
        verbose = False
        if len(self.ingredientList)==0:
            if verbose:
                print "removeIngredientByType finds no ingredients in list!"
            return

        for thisIngredient in self.ingredientList[:]:
            if thisIngredient.__module__.endswith(ingredientType): #TODO: fix this so we look for it by instance not name
                if verbose:
                    print 'Removing ingredient ' + thisIngredient.objectName

                self.removeIngredient(thisIngredient)


    def listIngredients(self):
        """
        Return a list of ingredient objectNames
        """
        ingredientNames = [] 
        for thisIngredient in ingredientList:
            ingredientNames.append(thisIngredient.objectName)

        return ingredientNames


    def returnIngredientByType(self,ingredientType):
        """
        Return a list of ingredients based upon their type. e.g. imagestack, sparsepoints, etc
        """
        verbose = False
        if len(self.ingredientList)==0:
            if verbose:
                print "returnIngredientByType finds no ingredients in list!"
            return False

        returnedIngredients=[]
        for thisIngredient in self.ingredientList:
            if thisIngredient.__module__.endswith(ingredientType):  #TODO: fix this so we look for it by instance not name
                returnedIngredients.append(thisIngredient)


        if verbose and len(returnedIngredients)==0:
            print "returnIngredientByType finds no ingredients with type " + ingredientType
            return False
        else:
            return returnedIngredients


    def returnIngredientByName(self,objectName):
        """
        Return a specific ingredient based upon its object name.
        Returns False if the ingredient was not found
        """
        verbose = False
        if len(self.ingredientList)==0:
            if verbose:
                print "returnIngredientByName finds no ingredients in list!"
            return False

        for thisIngredient in self.ingredientList:
            if thisIngredient.objectName == objectName:
                return thisIngredient

        if verbose:
            print "returnIngredientByName finds no ingredient called " + objectName
        return False


    # -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -           

    def resetAxes(self):
        """
        Set X and Y limit of each axes to fit the data
        """
        if self.stacksInTreeList()==False:
            return
        [axis.resetAxes() for axis in self.axes2D]



    def initialiseAxes(self,resetAxes=False):
        """
        Initial display of images in axes and also update other parts of the GUI. 
        """
        if self.stacksInTreeList()==False:
            return

        #show default images (snap to middle layer of each axis)
        [axis.updatePlotItems_2D(self.ingredientList) for axis in self.axes2D]

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
        for ii in range(len(self.axisRatioLineEdits)):
            self.axes2D[ii].view.setAspectLocked(True, float(self.axisRatioLineEdits[ii].text()))
        
        if resetAxes:
            self.resetAxes()


    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # Slots for points tab
    def markerSymbol_comboBox_slot(self,index):
        symbol = str(self.markerSymbol_comboBox.currentText())
        ingredient = self.returnIngredientByName(self.selectedPointsName())
        if ingredient==False:
            return
        ingredient.symbol = symbol
        self.initialiseAxes()

    def markerSize_spinBox_slot(self,spinBoxValue):
        ingredient = self.returnIngredientByName(self.selectedPointsName())
        if ingredient==False:
            return
        ingredient.symbolSize = spinBoxValue
        self.initialiseAxes()

    def markerAlpha_spinBox_slot(self,spinBoxValue):
        ingredient = self.returnIngredientByName(self.selectedPointsName())
        if ingredient==False:
            return
        ingredient.alpha = spinBoxValue
        self.initialiseAxes()

    def markerColor_pushButton_slot(self):
        ingredient = self.returnIngredientByName(self.selectedPointsName())
        if ingredient==False:
            return

        col = QtGui.QColorDialog.getColor()
        rgb = [col.toRgb().red(), col.toRgb().green(), col.toRgb().blue()]
        ingredient.color =rgb
        self.initialiseAxes()

    def addLines_checkBox_slot(self,state):
        ingredient = self.returnIngredientByName(self.selectedPointsName())
        if ingredient==False:
            return

        if state==0:
            ingredient.pen = None
        else:
            ingredient.pen = True

        self.initialiseAxes()


    def selectedPointsName(self):
        """
        Return the name of the selected points ingredient. If none are selected, returns the first in the list
        """
        if self.points_Model.rowCount()==0:
            print "lasagna.selectedPointsName finds no image stacks in list"
            return False

        #Highlight the first row if nothing is selected (which shouldn't ever happen)        
        if len(self.points_TreeView.selectedIndexes())==0:
            firstItem  = self.points_Model.index(0,0)
            self.points_TreeView.setCurrentIndex(firstItem)
            print "lasagna.selectedStackName forced highlighting of first image stack"


        return str( self.points_TreeView.selectedIndexes()[0].data().toString() )


    #The remaining methods for this tab are involved in building a context menu on right-click
    def layersMenuPoints(self,position): 
        menu = QtGui.QMenu()

        action = QtGui.QAction("Delete",self)
        action.triggered.connect(self.deleteLayerPoints_Slot)
        menu.addAction(action)
        menu.exec_(self.points_TreeView.viewport().mapToGlobal(position))


    def deleteLayerPoints_Slot(self):
        objName =  self.selectedPointsName()
        self.removeIngredientByName(objName)
        print "removed " + objName




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


    def flipAxis_Slot(self,axisToFlip):
        """
        Loops through all displayed image stacks and flips the axes
        """
        imageStacks = self.returnIngredientByType('imagestack')
        if imageStacks==False:
            return

        for thisStack in imageStacks:
            thisStack.flipDataAlongAxis(axisToFlip)

        self.initialiseAxes()



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


    def updateCrossHairs(self):
        """
        Update the drawn cross hairs on the current image 
        """
        if not self.showCrossHairs:
            return
        self.crossHairVLine.setPos(self.mouseX+0.5) #Add 0.5 to add line to middle of pixel
        self.crossHairHLine.setPos(self.mouseY+0.5)


    def updateStatusBar(self):
        """
        Update the text on the status bar based on the current mouse position 
        """

        X = self.mouseX
        Y = self.mouseY

        #get pixels under image
        imageItems = self.axes2D[0].getPlotItemByType('ImageItem')
        pixelValues=[]
        
        #Get the pixel intensity of all displayed image layers under the mouse
        #The following assumes that images have their origin at (0,0)
        for thisImageItem in imageItems:
            imShape = thisImageItem.image.shape

            if X<0 or Y<0:
                pixelValues.append(0)
            elif X>=imShape[0] or Y>=imShape[1]:
                pixelValues.append(0)
            else:
                pixelValues.append(thisImageItem.image[X,Y])

        #Build a text string to house these values
        valueStr = ''
        while len(pixelValues)>0:
            valueStr = valueStr + '%d,' % pixelValues.pop()

        valueStr = valueStr[:-1] #Chop off the last character

        self.statusBarText = "X=%d, Y=%d, val=[%s]" % (X,Y,valueStr)

        self.runHook(self.hooks['updateStatusBar_End']) #Hook goes here to modify or append message
        self.statusBar.showMessage(self.statusBarText)


    def updateMainWindowOnMouseMove(self,axis):
        """
        Update UI elements on the screen (but not the plotted images) as the user moves the mouse across an axis
        """
        self.runHook(self.hooks['updateMainWindowOnMouseMove_Start']) #Runs each time the views are updated

        self.updateCrossHairs()
        self.updateStatusBar()

        self.runHook(self.hooks['updateMainWindowOnMouseMove_End']) #Runs each time the views are updated



    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # Image Tab methods
    # These methods are involved with the tabs to the left of the three view axes


    #The following are part of the image tab
    def plotImageStackHistogram(self):
        """
        Plot the image stack histogram in a PlotWidget to the left of the three image views.
        This function is called when the plot is first set up and also when the log Y
        checkbox is checked or unchecked
        """
        img = lasHelp.findPyQtGraphObjectNameInPlotWidget(self.axes2D[0].view,self.selectedStackName())
        if img==False: #TODO: when the last image stack is deleted there is an error that is caught by this if statement a more elegant solution would be nice
            self.intensityHistogram.clear()
            return

        x,y = img.getHistogram()
      
        #Plot the histogram
        if self.logYcheckBox.isChecked():
            y=np.log10(y+0.1)
            y[y<0]=0

        self.intensityHistogram.clear()
        ingredient = self.returnIngredientByName(self.selectedStackName());#Get colour of the layer

        brushColor =  ingredient.histBrushColor()
        penColor = ingredient.histPenColor()

        ## Using stepMode=True causes the plot to draw two lines for each sample but it needs X to be longer than Y by 1
        self.intensityHistogram.plot(x, y, stepMode=False, fillLevel=0, pen=penColor, brush=brushColor,yMin=0, xMin=0)
        self.intensityHistogram.showGrid(x=True,y=True,alpha=0.33)

        #The object that represents the plotted intensity range is only set up the first time the 
        #plot is made or following a new base image being loaded (any existing plottedIntensityRegionObj
        #is deleted at base image load time.)
        if not hasattr(self,'plottedIntensityRegionObj'):
            self.plottedIntensityRegionObj = pg.LinearRegionItem()
            self.plottedIntensityRegionObj.setZValue(10)
            self.plottedIntensityRegionObj.sigRegionChanged.connect(self.updateAxisLevels) #link signal slot

        #Get the plotted range and apply to the region object
        minMax=self.returnIngredientByName(self.selectedStackName()).minMax
        self.setIntensityRange(minMax)

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
        #TODO: Decide what to do with minMax. Setting it here by directly manipulating the item seems wrong
        minX, maxX = self.plottedIntensityRegionObj.getRegion()

        #Get all imagestacks
        allImageStacks = self.returnIngredientByType('imagestack')
        if allImageStacks == False:
            return

        #Loop through all imagestacks and set their levels in each axis
        for thisImageStack in allImageStacks:
            objectName=thisImageStack.objectName

            if objectName != self.selectedStackName(): #TODO: LAYERS
                continue

            for thisAxis in self.axes2D:
                img = lasHelp.findPyQtGraphObjectNameInPlotWidget(thisAxis.view,objectName)
                img.setLevels([minX,maxX]) #Sets levels immediately
                thisImageStack.minMax=[minX,maxX] #ensures levels stay set during all plot updates that follow

            


    def mouseMovedCoronal(self,evt):
        if self.stacksInTreeList()==False:
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
            self.axes2D[0].updateDisplayedSlices_2D(self.ingredientList,(self.mouseX,self.mouseY)) #Update displayed slice
    

    def mouseMovedSaggital(self,evt):
        if self.stacksInTreeList()==False:
            return

        pos = evt[0]
        self.removeCrossHairs()

        if self.axes2D[1].view.sceneBoundingRect().contains(pos):
            if self.showCrossHairs:
                self.axes2D[1].view.addItem(self.crossHairVLine, ignoreBounds=True)
                self.axes2D[1].view.addItem(self.crossHairHLine, ignoreBounds=True)

            (self.mouseX,self.mouseY)=self.axes2D[1].getMousePositionInCurrentView(pos)
            self.updateMainWindowOnMouseMove(self.axes2D[1])
            self.axes2D[1].updateDisplayedSlices_2D(self.ingredientList,(self.mouseX,self.mouseY))

        
    def mouseMovedTransverse(self,evt):
        if self.stacksInTreeList()==False:
            return

        pos = evt[0]  
        self.removeCrossHairs()

        if self.axes2D[2].view.sceneBoundingRect().contains(pos):
            if self.showCrossHairs:
                self.axes2D[2].view.addItem(self.crossHairVLine, ignoreBounds=True) 
                self.axes2D[2].view.addItem(self.crossHairHLine, ignoreBounds=True)

            (self.mouseX,self.mouseY)=self.axes2D[2].getMousePositionInCurrentView(pos)
            self.updateMainWindowOnMouseMove(self.axes2D[2])
            self.axes2D[2].updateDisplayedSlices_2D(self.ingredientList,(self.mouseX,self.mouseY))



# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

def main(fnames, pluginToStart=None):
    app = QtGui.QApplication([])

    tasty = lasagna()
    tasty.app = app

    #Load stacks from command line input if any was provided
    if not fnames[0]==None:
        for thisFname in fnames:
            print "Loading " + thisFname
            tasty.loadImageStack(thisFname)

    tasty.initialiseAxes()

    if pluginToStart != None:
        if tasty.plugins.has_key(pluginToStart):
            tasty.startPlugin(pluginToStart) 
            tasty.pluginActions[pluginToStart].setChecked(True)
        else:
            print "No plugin '%s': not starting" % pluginToStart

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # Link slots to signals
    #connect views to the mouseMoved slot. After connection this runs in the background. 
    #TODO: set up with just one slot that accepts arguments
    proxy1=pg.SignalProxy(tasty.axes2D[0].view.scene().sigMouseMoved, rateLimit=30, slot=tasty.mouseMovedCoronal)
    proxy2=pg.SignalProxy(tasty.axes2D[1].view.scene().sigMouseMoved, rateLimit=30, slot=tasty.mouseMovedSaggital)
    proxy3=pg.SignalProxy(tasty.axes2D[2].view.scene().sigMouseMoved, rateLimit=30, slot=tasty.mouseMovedTransverse)

    sys.exit(app.exec_())

## Start Qt event loop unless running in interactive mode.
if __name__ == '__main__':
    main(fnames=fnames, pluginToStart=pluginToStart)


    """
    original_sigint = signal.getsignal(signal.SIGINT)
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
    """