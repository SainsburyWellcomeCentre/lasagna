
"""
Overlays brain area onto a registered sample brain without overlaying the atlas.
"""

import lasagna_helperFunctions as lasHelp 
from lasagna_plugin import lasagna_plugin
import numpy as np
import pyqtgraph as pg
import os.path
from alert import alert
import imageStackLoader

#For the UI
from PyQt4 import QtGui, QtCore
import area_namer_UI

#For handling the labels files
import ara_json, tree

#For contour drawing
from skimage import measure

from ARA_plotter import ARA_plotter


class plugin(ARA_plotter, lasagna_plugin, QtGui.QWidget, area_namer_UI.Ui_area_namer): 
    def __init__(self,lasagna):
        super(plugin,self).__init__(lasagna)
        self.lasagna=lasagna

        self.pluginShortName="area namer"
        self.pluginLongName="brain area namer"
        self.pluginAuthor="Rob Campbell"


        #Read file locations from preferences file (creating a default file if none exists)
        self.pref_file = lasHelp.getLasagna_prefDir() + 'ARA_plugin_prefs.yml'
        self.prefs = lasHelp.loadAllPreferences(prefFName=self.pref_file,defaultPref=self.defaultPrefs())

        #The last value the mouse hovered over. When this changes, we re-calcualte the contour 
        self.lastValue=-1


        #default names of the three files that we need:
        self.atlasFileName = 'atlas'
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
        

        #Link signals to slots
        self.araName_comboBox.activated.connect(self.araName_comboBox_slot)
        self.loadOrig_pushButton.released.connect(self.loadOrig_pushButton_slot)
        self.loadOther_pushButton.released.connect(self.loadOther_pushButton_slot)

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

            pths = dict(atlas='', labels='')
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

        #If the user has asked for this, load the first ARA entry automatically
        self.data = dict(currentlyLoadedAtlasName='', currentlyLoadedOverlay='', atlas=np.ndarray([])) 

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
        imageStack = self.data['atlas'] 
        value = self.writeAreaNameInStatusBar(imageStack,self.statusBarName_checkBox.isChecked()) #Inherited from ARA_plotter

        #Highlight the brain area we are mousing over by drawing a boundary around it
        if self.lastValue != value  and self.highlightArea_checkBox.isChecked():
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
            self.loadOrig_pushButton.setEnabled(True) 
            return

        if self.data['currentlyLoadedAtlasName'] != str(self.araName_comboBox.itemText(self.araName_comboBox.currentIndex())):
            self.loadOrig_pushButton.setEnabled(True) 
        elif self.data['currentlyLoadedAtlasName'] == str(self.araName_comboBox.itemText(self.araName_comboBox.currentIndex())):
            self.loadOrig_pushButton.setEnabled(False) 


    def loadOrig_pushButton_slot(self):
        """
        Loads the atlas file but does not display it. Coordinate loading of the ARA items defined in the dictionary paths. 
        araName is a value from the self.paths dictionary. The values will be 
        combobox item texts and will load a dictionary from self.paths. The keys
        of this dictionary have these keys: 
        'atlas' (full path to atlas volume file)
        'labels' (full path to atlas labels file - csv or json)
        """
        selectedName = str(self.araName_comboBox.itemText(self.araName_comboBox.currentIndex()))

        paths = self.paths[selectedName]

        #Load the labels (this associates brain area index values with brain area names)
        self.data['labels'] = self.loadLabels(paths['labels'])

        #Load the raw image data but do not display it.
        self.data['atlas'] = imageStackLoader.loadStack(paths['atlas'])

        self.data['currentlyLoadedAtlasName'] =  paths['atlas'].split(os.path.sep)[-1]


    def loadOther_pushButton_slot(self,fnameToLoad=False):
        """
        Load a user-selected atlas file but use the labels from the ARA in the drop-down box.
        Can optionally load a specific file name (used for de-bugging)
        """
        if fnameToLoad==False:       
            fileFilter="Images (*.mhd *.mha *.tiff *.tif *.nrrd)"
            fnameToLoad = QtGui.QFileDialog.getOpenFileName(self, 'Open file', lasHelp.readPreference('lastLoadDir'), fileFilter)
            fnameToLoad = str(fnameToLoad)

        #re-load labels        
        selectedName = str(self.araName_comboBox.itemText(self.araName_comboBox.currentIndex()))
        paths = self.paths[selectedName]
        self.data['labels'] = self.loadLabels(paths['labels'])

        #load the selected atlas (without displaying it)
        self.data['atlas'] = imageStackLoader.loadStack(fnameToLoad)

        self.data['currentlyLoadedAtlasName'] =  fnameToLoad.split(os.path.sep)[-1]


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
