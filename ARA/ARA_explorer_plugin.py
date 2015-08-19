
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

#For handling the labels files
import ara_json, tree

class plugin(lasagna_plugin, QtGui.QWidget, ara_explorer_UI.Ui_ara_explorer): #must inherit lasagna_plugin first
    def __init__(self,lasagna):
        super(plugin,self).__init__(lasagna)
        self.lasagna=lasagna

        self.pluginShortName="ARA explorer"
        self.pluginLongName="Allen Reference Atlas explorer"
        self.pluginAuthor="Rob Campbell"


        #Read file locations from preferences file (creating a default file if none exists)
        self.pref_file = lasHelp.getLasagna_prefDir() + 'ARA_plugin_prefs.yml'
        self.prefs = lasHelp.loadAllPreferences(prefFName=self.pref_file,defaultPref=self.defaultPrefs())

        #Warn and quit if there are no paths
        if len(self.prefs['ara_paths'])==0:
           self.warnAndQuit('Please fill in preferences file at<br>%s' % self.pref_file)
           return

        #Set up the UI
        self.setupUi(self)
        self.show()
        self.statusBarName_checkBox.setChecked(self.prefs['enableNameInStatusBar'])
        self.highlightArea_checkBox.setChecked(self.prefs['enableOverlay'])


        #Loop through all paths and add to combobox.
        self.paths = dict()
        for ara in self.prefs['ara_paths']:
            pths = self.prefs['ara_paths'][ara] #paths

            #Skip if we can't find valid files
            if len(pths['atlas'])==0 | len(pths['labels'])==0 :
                print 'Skipping empty empty paths entry'
                continue

            skip = False
            for fileType in ['atlas','labels']:
                if not os.path.exists(pths[fileType]):
                    print 'Can not find %s. Skipping.' % pths[fileType]
                    skip = True
            if skip:
                continue

            #If we're here, this entry should at least have a valid atlas file and a valid labels file

            #We will index the self.paths dictionary by the name of the atlas file as this is also 
            #what will be put into the combobox. 
            atlasFileName = pths['atlas'].split(os.path.sep)[-1]

            #skip if a file with this name already exists
            if self.paths.has_key(atlasFileName):
                print "Skipping as a file called %s is already in the list" % atlasFileName
                continue


            #Add this ARA to the paths dictionary and to the combobox
            self.paths[atlasFileName] = pths            
            self.araName_comboBox.addItem(atlasFileName)



        #If we have no paths to ARAs by the end of this, issue an error alertbox and quit
        if len(self.paths)==0:
           self.warnAndQuit('Found no valid paths is preferences file at<br>%s' % self.pref_file)
           return


        self.data = dict() #Loaded data will be in this dictionary

        self.initPlugin()



    def initPlugin(self):
        self.lasagna.removeIngredientByType('imagestack') #remove all image stacks

        #If the user has asked for this, load the first ARA entry automatically
        if self.prefs['loadFirstAtlasOnStartup']:
            self.loadARA(self.paths[self.paths.keys()[0]])


        #Make up a disjointed colormap
        pos = np.array([0.0, 0.001, 0.25, 0.35, 0.45, 0.65, 0.9])
        color = np.array([[0,0,0,255],[255,0,0,255], [0,2,230,255], [7,255,112,255], [255,240,7,255], [7,153,255,255], [255,7,235,255]], dtype=np.ubyte)
        map = pg.ColorMap(pos, color)
        lut = map.getLookupTable(0.0, 1.0, 256)

        #Assign the colormap to the imagestack object
        self.ARAlayerName = self.lasagna.imageStackLayers_Model.index(0,0).data().toString() #TODO: a bit horrible
        firstLayer = self.lasagna.returnIngredientByName(self.ARAlayerName)
        firstLayer.lut=lut
        #Specify what colors the histogram should be so it doesn't end up megenta and 
        #vomit-yellow, or who knows what, due to the weird color map we use here.
        firstLayer.histPenCustomColor = [180,180,180,255]
        firstLayer.histBrushCustomColor = [150,150,150,150]

        self.lasagna.initialiseAxes(resetAxes=True)
        self.lasagna.plottedIntensityRegionObj.setRegion((0,2E3))



    def closePlugin(self):
        """
        Runs when the user unchecks the plugin in the menu box and also (in this case)
        when the user loads a new base stack
        """
        #self.lasagna.removeIngredientByName(self.ARAlayerName) #TODO: remove stuff
        self.lasagna.intensityHistogram.clear()
        self.detachHooks()


    #--------------------------------------
    # plugin hooks
    #all methods starting with hook_ are automatically registered as hooks with lasagna 
    #when the plugin is started this happens in the lasagna_plugin constructor 
    def hook_updateStatusBar_End(self):
        """
        hooks into the status bar update function to show the brain area name in the status bar 
        as the user mouses over the images
        """

        if self.lasagna.pixelValue in self.data['labels'].nodes:
            thisArea=self.data['labels'][self.lasagna.pixelValue].data['name']
        else:
            thisArea='UKNOWN'

        self.lasagna.statusBarText = self.lasagna.statusBarText + ", area: " + thisArea



    #The following hooks are for graceful shut down
    def hook_showBaseStackLoadDialog_Start(self):
        """
        Hooks into base image file dialog method to shut down the ARA Explorer if the
        user attempts to load a base stack
        """
        self.lasagna.removeIngredientByType('imagestack')

        self.lasagna.stopPlugin(self.__module__) #This will call self.closePlugin
        self.lasagna.pluginActions[self.__module__].setChecked(False) #Uncheck the menu item associated with this plugin's name

        self.closePlugin()


    def hook_loadRecentFileSlot_Start(self):
        """
        Hooks into the recent file loading method to shut down the ARA Explorer if the
        user attempts to load a base stack
        """
        self.lasagna.removeIngredientByType('imagestack')

        self.lasagna.stopPlugin(self.__module__) #This will call self.closePlugin
        self.lasagna.pluginActions[self.__module__].setChecked(False) #Uncheck the menu item associated with this plugin's name

        self.closePlugin()


    #--------------------------------------
    # core methods: these do the meat of the work
    #
    def loadARA(self,paths):
        """
        Coordinates loading of the ARA items defined in the dictionary paths. 
        Paths has these keys: 
        'atlas' (full path to atlas volume file)
        'labels' (full path to atlas labels file - csv or json)
        'template' (full path to average template file - optional)
        """
        self.data['labels'] = self.loadLabels(paths['labels'])
        self.data['atlas'] = self.loadVolume(paths['atlas'])        
        #self.data['template'] = self.loadVolume(paths['template'])   #TODO: set up code for this. 


    def loadLabels(self,fname):
        """
        Load the labels file, which may be in JSON or CSV format\
        
        The csv file should have the following format
        index,parent_index,data1,data1,dataN\n
        The first line should be a header line. Suggested separators: | or ,

        Header must include at least the name of the area. So we can get, e.g. 
        'name': 'Entorhinal area, lateral part, layer 2'

        The JSON should be the raw JSON from the ARA website

        Returns the labels as a tree structure that can be indexed by ID
        """

        if fname.lower().endswith('.csv'):
            colSep = self.guessFileSep(fname)
            return tree.importData(fname,colSep=colSep, headerLine=True)

        if fname.lower().endswith('.json'):
            (flattened,colNames) = ara_json.importData(fname)
            return tree.importData(flattened.split('\n'), colSep='|', headerLine=colNames)


    def loadVolume(self,fname):
        """
        Load the volume file, which may be in any format that the main viewer accepts through the
        load stack dialog
        """
        return self.lasagna.loadImageStack(fname)



    def guessFileSep(self,fname):
        """
        Guess the file separator in file fname.
        """
        fid=open(fname,'r')
        contents=fid.read()
        fid.close()
        nLines = contents.count('\n')
        possibleSeparators = ['|','\t',','] #don't include space because for these data that would be crazy
        for thisSep in possibleSeparators:
            if contents.count(thisSep)>=nLines:
                return thisSep

        #Just return comma if nothing was found. At least we tried!
        return ','





    #----------------------------
    #the following are housekeeping methods
    def defaultPrefs(self):
        """
        Return default preferences in the YAML file in this directory
        """

        emptyPathPref = {1: 
                        {'atlas': '',    #full path to atlas file (segmented brain area volume)
                         'labels': '',   #full path to labels JSON or CSV
                         'template': ''} #full path to average template (optional)
                    }

        return {
            'ara_paths' : emptyPathPref ,
            'loadFirstAtlasOnStartup' : True,
            'enableNameInStatusBar' : True ,
            'enableOverlay' : True ,
            }


    def warnAndQuit(self,msg):
        """
        Display alert and quit the plugin
        """
        #TODO: is not shutting down properly
        self.lasagna.alert = alert(self.lasagna,alertText=msg)
        self.lasagna.pluginActions[self.__module__].setChecked(False) #Uncheck the menu item associated with this plugin's name
        self.lasagna.stopPlugin(self.__module__) #This will call self.closePlugin as well as making it possible to restart the plugin
        self.closePlugin()