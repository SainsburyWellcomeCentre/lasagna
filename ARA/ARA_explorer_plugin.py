
"""
lasagna plugin for exploring the Allen Brain Atlas:
1. Display of average template brain.
2. Reporting of brain area name
more stuff... 
plugin under construction

"""

import lasagna_helperFunctions as lasHelp 
from lasagna_plugin import lasagna_plugin
import numpy as np
import pyqtgraph as pg
import os.path
from alert import alert

#For the UI
from PyQt4 import QtGui, QtCore
import ara_explorer_UI

#For contour drawing
from skimage import measure

from ARA_plotter import ARA_plotter


class plugin(ARA_plotter, lasagna_plugin, QtGui.QWidget, ara_explorer_UI.Ui_ara_explorer): 
    def __init__(self,lasagna):
        super(plugin,self).__init__(lasagna)
        self.lasagna=lasagna

        self.pluginShortName="ARA explorer"
        self.pluginLongName="Allen Reference Atlas explorer"
        self.pluginAuthor="Rob Campbell"


        #Read file locations from preferences file (creating a default file if none exists)
        self.pref_file = lasHelp.getLasagna_prefDir() + 'ARA_plugin_prefs.yml'
        self.prefs = lasHelp.loadAllPreferences(prefFName=self.pref_file,defaultPref=self.defaultPrefs())

        #The last value the mouse hovered over. When this changes, we re-calculate the contour 
        self.lastValue=-1


        #default names of the three files that we need:
        self.atlasFileName = 'atlas'
        self.templateFileName = 'template'
        self.labelsFileName = 'labels'

        #The root node index of the ARA
        self.rootNode=8  

        #Warn and quit if there are no paths
        if len(self.prefs['ara_paths'])==0:
           self.warnAndQuit('Please fill in preferences file at<br>%s<br><a href="http://raacampbell13.github.io/lasagna/ara_explorer_plugin.html">http://raacampbell13.github.io/lasagna/ara_explorer_plugin.html</a>' % self.pref_file)
           return

        #Set up the UI
        self.setupUi(self)
        self.show()
        self.statusBarName_checkBox.setChecked(self.prefs['enableNameInStatusBar'])
        self.highlightArea_checkBox.setChecked(self.prefs['enableOverlay'])
        
        self.brainArea_itemModel = QtGui.QStandardItemModel(self.brainArea_treeView)
        self.brainArea_treeView.setModel(self.brainArea_itemModel)

        #Link the selections in the tree view to a slot in order to allow highlighting of the selected area
        QtCore.QObject.connect(self.brainArea_treeView.selectionModel(), QtCore.SIGNAL("selectionChanged(QItemSelection, QItemSelection)"), self.highlightSelectedAreaFromList) 


        #Link signals to slots
        self.araName_comboBox.activated.connect(self.araName_comboBox_slot)
        self.load_pushButton.released.connect(self.load_pushButton_slot)
        self.overlayTemplate_checkBox.stateChanged.connect(self.overlayTemplate_checkBox_slot)

        self.statusBarName_checkBox.stateChanged.connect(self.statusBarName_checkBox_slot)
        self.highlightArea_checkBox.stateChanged.connect(self.highlightArea_checkBox_slot)

        #Loop through all paths and add to combobox.
        self.paths = dict()
        n=1
        for path in self.prefs['ara_paths']:

            if not os.path.exists(path):
                print "%s does not exist. skipping" % path 
                continue

            filesInPath = os.listdir(path) 
            if len(filesInPath)==0:
                print "No files in %s . skipping" % path 
                continue

            pths = dict(atlas='', labels='', template='')
            print "\n %d. Looking for files in directory %s" % (n,path)
            n += 1

            files = os.listdir(path)

            #get the file names
            for thisFile in files:
                if thisFile.startswith(self.atlasFileName):
                    if thisFile.endswith('raw'):
                        continue
                    pths['atlas'] = os.path.join(path,thisFile)
                    print "Adding atlas file %s" % thisFile
                    break 

            for thisFile in files:
                if thisFile.startswith(self.labelsFileName):
                    pths['labels'] = os.path.join(path,thisFile)
                    print "Adding labels file %s" % thisFile
                    break 

            for thisFile in files:
                if thisFile.startswith(self.templateFileName):
                    if thisFile.endswith('raw'):
                        continue
                    pths['template'] = os.path.join(path,thisFile)
                    print "Adding template file %s" % thisFile
                    break 


            if len(pths['atlas'])==0 | len(pths['labels'])==0 :
                print 'Skipping empty empty paths entry'
                continue


            #If we're here, this entry should at least have a valid atlas file and a valid labels file

            #We will index the self.paths dictionary by the name of the atlas file as this is also 
            #what will be put into the combobox. 
            atlasDirName = path.split(os.path.sep)[-1]

            #skip if a file with this name already exists
            if self.paths.has_key(atlasDirName):
                print "Skipping as a directory called %s is already in the list" % atlasDirName
                continue


            #Add this ARA to the paths dictionary and to the combobox
            self.paths[atlasDirName] = pths
            self.araName_comboBox.addItem(atlasDirName)


        #blank line
        print ""

        #If we have no paths to ARAs by the end of this, issue an error alertbox and quit
        if len(self.paths)==0:
           self.warnAndQuit('Found no valid paths is preferences file at<br>%s.<br>SEE <a href="http://raacampbell13.github.io/lasagna/ara_explorer_plugin.html">http://raacampbell13.github.io/lasagna/ara_explorer_plugin.html</a>' % self.pref_file)
           return

        self.lasagna.removeIngredientByType('imagestack') #remove all image stacks

        #If the user has asked for this, load the first ARA entry automatically
        self.data = dict(currentlyLoadedAtlasName='', currentlyLoadedOverlay='') 

        currentlySelectedARA = str(self.araName_comboBox.itemText(self.araName_comboBox.currentIndex()))
        if self.prefs['loadFirstAtlasOnStartup']:
            print "Auto-Loading " +  currentlySelectedARA
            self.loadARA(currentlySelectedARA)
            self.load_pushButton.setEnabled(False) #disable because the current selection has now been loaded

        #Make a lines ingredient that will house the contours for the currently selected area.
        self.contourName = 'aracontour'
        self.lasagna.addIngredient(objectName=self.contourName, 
                                kind='lines', 
                                data=[])
        self.lasagna.returnIngredientByName(self.contourName).addToPlots() #Add item to all three 2D plots
        # End of constructor


    #--------------------------------------
    # plugin hooks
    #all methods starting with hook_ are automatically registered as hooks with lasagna 
    #when the plugin is started this happens in the lasagna_plugin constructor 
    def hook_updateStatusBar_End(self):
        """
        hooks into the status bar update function to show the brain area name in the status bar 
        as the user mouses over the images
        """

        #Get the atlas volume and find in which voxel the mouse cursor is located        
        araName = str(self.araName_comboBox.itemText(self.araName_comboBox.currentIndex()))
        atlasLayerName = self.paths[araName]['atlas'].split(os.path.sep)[-1]
        ingredient = self.lasagna.returnIngredientByName(atlasLayerName)

        if ingredient == False:
            print "ARA_explorer_plugin.hook_updateStatusBar_End Failed to find imageStack named %s" % atlasLayerName
            return

        imageStack = self.lasagna.returnIngredientByName(atlasLayerName).raw_data()

        value = self.writeAreaNameInStatusBar(imageStack,self.statusBarName_checkBox.isChecked()) #Inherited from ARA_plotter

        #Highlight the brain area we are mousing over by drawing a boundary around it
        if self.lastValue != value  and  self.highlightArea_checkBox.isChecked():
            self.drawAreaHighlight(imageStack,value) #Inherited from ARA_plotter


    def hook_deleteLayerStack_Slot_End(self):
        """
        Runs when a stack is removed. Watches for the removal of the current atlas and 
        triggers closing of the plugin if it is removed.
        """
        #is the current loaded atlas present
        atlasName= self.data['currentlyLoadedAtlasName']
        if self.lasagna.returnIngredientByName(atlasName)==False:
            print "The current atlas has been removed by the user. Closing the ARA explorer plugin"
            self.closePlugin()

   

    #--------------------------------------
    # UI slots
    #all methods starting with hook_ are automatically registered as hooks with lasagna 
    #when the plugin is started this happens in the lasagna_plugin constructor 
    def araName_comboBox_slot(self):
        """
        Enables the load button only if the currently selected item is not loaded
        """
        #If nothing has been loaded then for sure we need the load button enabled
        if len(self.data['currentlyLoadedAtlasName'])==0:
            self.load_pushButton.setEnabled(True) 
            return

        if self.data['currentlyLoadedAtlasName'] != str(self.araName_comboBox.itemText(self.araName_comboBox.currentIndex())):
            self.load_pushButton.setEnabled(True) 
        elif self.data['currentlyLoadedAtlasName'] == str(self.araName_comboBox.itemText(self.araName_comboBox.currentIndex())):
            self.load_pushButton.setEnabled(False) 


    def load_pushButton_slot(self):
        """
        Load the currently selected ARA version
        """
        selectedName = str(self.araName_comboBox.itemText(self.araName_comboBox.currentIndex()))
        self.loadARA(selectedName)


    def overlayTemplate_checkBox_slot(self):
        """
        Load or unload the template overlay
        """
        fname = self.data['template']
        if len(fname)==0:
            return

        if self.overlayTemplate_checkBox.isChecked()==True:
            if os.path.exists(fname):
                self.addOverlay(fname)
                return

        if self.overlayTemplate_checkBox.isChecked()==False:
            overlayName = fname.split(os.path.sep)[-1]
            self.lasagna.removeIngredientByName(overlayName)

        self.lasagna.returnIngredientByName(self.data['currentlyLoadedAtlasName']).lut='gray'
        self.lasagna.initialiseAxes()


    def statusBarName_checkBox_slot(self):
        """
        Remove the area name or add it as soon as the check box is unchecked
        """
        araName = str(self.araName_comboBox.itemText(self.araName_comboBox.currentIndex()))
        atlasLayerName = self.paths[araName]['atlas'].split(os.path.sep)[-1]
        imageStack = self.lasagna.returnIngredientByName(atlasLayerName).raw_data()
        
        if not self.statusBarName_checkBox.isChecked():
            self.writeAreaNameInStatusBar(imageStack,False)
        elif self.statusBarName_checkBox.isChecked():
            self.writeAreaNameInStatusBar(imageStack,True)
            
        self.lasagna.updateStatusBar()


    def highlightArea_checkBox_slot(self):
        """
        Remove the contour or add it as soon as the check box is unchecked
        """
        if not self.highlightArea_checkBox.isChecked():
            self.removeAreaContour()
        elif self.highlightArea_checkBox.isChecked():
            self.addAreaContour()
            
            
    #--------------------------------------
    # core methods: these do the meat of the work
    #
    def loadARA(self,araName):
        """
        Coordinate loading of the ARA items defined in the dictionary paths. 
        araName is a value from the self.paths dictionary. The values will be 
        combobox item texts and will load a dictionary from self.paths. The keys
        of this dictionary have these keys: 
        'atlas' (full path to atlas volume file)
        'labels' (full path to atlas labels file - csv or json)
        'template' (full path to average template file - optional)
        """
        
        paths = self.paths[araName]

        #remove the currently loaded ARA (if present)
        if len(self.data['currentlyLoadedAtlasName'])>0:
            self.lasagna.removeIngredientByName(self.data['currentlyLoadedAtlasName'])

        self.data['labels'] = self.loadLabels(paths['labels']) #see ARA_plotter.py


        self.addAreaDataToTreeView(self.data['labels'],self.rootNode,self.brainArea_itemModel.invisibleRootItem())

        self.lasagna.loadImageStack(paths['atlas'])
        
        self.data['currentlyLoadedAtlasName'] =  paths['atlas'].split(os.path.sep)[-1]

        self.data['template']=paths['template']
        if os.path.exists(paths['template']):
            self.overlayTemplate_checkBox.setEnabled(True)
            if self.overlayTemplate_checkBox.isChecked()==True:
                self.addOverlay(self.data['template'])
        else:
            self.overlayTemplate_checkBox.setEnabled(False)


        #self.setARAcolors()
        #self.lasagna.initialiseAxes(resetAxes=True)
        self.lasagna.returnIngredientByName(self.data['currentlyLoadedAtlasName']).minMax = [0,1.2E3]
        self.lasagna.initialiseAxes(resetAxes=True)


    def addOverlay(self,fname):
        """
        Add an overlay
        """
        self.lasagna.loadImageStack(fname)
        self.data['currentlyLoadedOverlay'] = str(fname.split(os.path.sep)[-1])
        self.lasagna.returnIngredientByName(self.data['currentlyLoadedAtlasName']).lut='gray'
        self.lasagna.returnIngredientByName(self.data['currentlyLoadedOverlay']).lut='cyan'
        self.lasagna.returnIngredientByName(self.data['currentlyLoadedOverlay']).minMax = [0,1.5E3]
        self.lasagna.initialiseAxes(resetAxes=True)


    #---------------
    #Methods to handle the tree 
    def addAreaDataToTreeView(self,thisTree,nodeID,parent):
        """
        Add a tree structure of area names to the QListView
        """

        children = thisTree[nodeID].children
        for child in sorted(children):
            child_item = QtGui.QStandardItem(thisTree[child].data['name'])
            child_item.setData(child) #Store index. Can be retrieved by: child_item.data().toInt()[0] NOT USING THIS RIGHT NOW
            parent.appendRow(child_item)
            #print child_item
            #Print the details associated with the QStandardItemObject
            #print "%d. %s is a %s and has index %s" % (child_item.data().toInt()[0], child_item.data().toString(),str(child_item), str(child_item.index()))

            self.addAreaDataToTreeView(thisTree, child, child_item)


    def AreaName2NodeID(self,thisTree,name,nodeID=None):
        """
        Searches the tree for a brain area called name and returns the node ID (atlas index value)
        Breaks out of the search loop if the area is found and propagates the value back through
        the recursive function calls
        """
        if nodeID is None:
            nodeID = self.rootNode
        
        children = thisTree[nodeID].children
        for child in sorted(children):
            if thisTree[child].data['name']==name:
                return child
            else:
                returnVal = self.AreaName2NodeID(thisTree=thisTree, name=name, nodeID=child)
                if returnVal != False:
                    return returnVal

        return False


    def highlightSelectedAreaFromList(self):
        """
        This slot is run when the user clicks on a brain area in the list
        """
        getFromModel = False #It would be great to get the area ID from the model, but I can't figure out how to get the sub-model that houses the data

        index = self.brainArea_treeView.selectedIndexes()[0]

        #Get the image stack, as we need to feed it to drawAreaHighlight
        araName = str(self.araName_comboBox.itemText(self.araName_comboBox.currentIndex()))
        atlasLayerName = self.paths[araName]['atlas'].split(os.path.sep)[-1]
        imageStack = self.lasagna.returnIngredientByName(atlasLayerName).raw_data()

        if getFromModel:
            #The following row and column indexes are also correct, but index.model() is the root model and this is wrong.
            treeIndex = index.model().item(index.row(),index.column()).data().toInt()[0] 
            print "treeIndex (%d,%d): %d" % (index.row(),index.column(),treeIndex)
        else: #so we do it the stupid way from the reee
            areaName = index.data().toString()
            treeIndex = self.AreaName2NodeID(self.data['labels'],areaName)

        if treeIndex != None:
            #print "highlighting %d" % treeIndex
            self.drawAreaHighlight(imageStack,treeIndex,highlightOnlyCurrentAxis=False)




    #----------------------------
    # Methods to handle close events and errors
    def closePlugin(self):
        """
        Runs when the user unchecks the plugin in the menu box and also (in this case)
        when the user loads a new base stack
        """        
        
        #remove the currently loaded ARA (if present)
        self.lasagna.removeIngredientByName('aracontour')

        if len(self.data['currentlyLoadedAtlasName'])>0:
            self.lasagna.removeIngredientByName(self.data['currentlyLoadedAtlasName'])

        if len(self.data['currentlyLoadedOverlay'])>0:
            self.lasagna.removeIngredientByName(self.data['currentlyLoadedOverlay'])


        #self.lasagna.intensityHistogram.clear()
        self.detachHooks()
        self.lasagna.statusBar.showMessage("ARA explorer closed")
        self.close()


    def closeEvent(self, event):
        """
        This event is execute when the user presses the close window (cross) button in the title bar
        """
        self.lasagna.stopPlugin(self.__module__) #This will call self.closePlugin
        self.lasagna.pluginActions[self.__module__].setChecked(False) #Uncheck the menu item associated with this plugin's name

        self.closePlugin()
        self.deleteLater()
        event.accept()


    def warnAndQuit(self,msg):
        """
        Display alert and (maybe) quit the plugin
        """
        self.lasagna.alert = alert(self.lasagna,alertText=msg)
        self.lasagna.stopPlugin(self.__module__) #This will call self.closePlugin
        self.lasagna.pluginActions[self.__module__].setChecked(False) #Uncheck the menu item associated with this plugin's name

        #TODO: If we close the plugin the warning vanishes right away
        #self.closePlugin()
