
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

#For contour drawing
from skimage import measure

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

        #The last value the mouse hovered over. When this changes, we re-calcualte the contour 
        self.lastValue=-1


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
           self.warnAndQuit('Found no valid paths is preferences file at<br>%s.<br>SEE <a href="http://raacampbell13.github.io/lasagna/ara_explorer_plugin.html">http://raacampbell13.github.io/lasagna/ara_explorer_plugin.html</a>' % self.pref_file)
           return

        self.lasagna.removeIngredientByType('imagestack') #remove all image stacks

        #If the user has asked for this, load the first ARA entry automatically
        self.data = dict(currentlyLoadedAtlasName='', currentlyLoadedOverlay='') #Loaded data will be in this dictionary, but we need the "loaded" key for sure
        if self.prefs['loadFirstAtlasOnStartup']:
            print "Auto-Loading " + self.araName_comboBox.itemText(self.araName_comboBox.currentIndex())
            self.loadARA(self.paths.keys()[0])
            self.load_pushButton.setEnabled(False) #disable because the current selection has now been loaded




        #Make a lines ingredient that will house the contours for the currently selected area.
        self.contourName = 'aracontour'
        self.lasagna.addIngredient(objectName=self.contourName, 
                                kind='lines', 
                                data=[])
        self.lasagna.returnIngredientByName(self.contourName).addToPlots() #Add item to all three 2D plots




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
        
        if not self.statusBarName_checkBox.isChecked():
            return
            
        stackName = self.araName_comboBox.itemText(self.araName_comboBox.currentIndex())
        thisAxis = self.lasagna.axes2D[self.lasagna.inAxis]
        thisItem = thisAxis.getPlotItemByName(stackName)
        imShape = thisItem.image.shape

        X = self.lasagna.mouseX
        Y = self.lasagna.mouseY
        
        if X<0 or Y<0:
            thisArea='outside image area'
            value=-1
        elif X>=imShape[0] or Y>=imShape[1]:
            thisArea='outside image area'
            value=-1
        else:
            value = thisItem.image[X,Y]
            if value==0:
                thisArea='outside brain'
            elif value in self.data['labels'].nodes :
                thisArea=self.data['labels'][value].data['name']
            else:
                thisArea='UNKNOWN'

        self.lasagna.statusBarText = self.lasagna.statusBarText + ", area: " + thisArea


        #Highlight the brain area we are mousing over by drawing a boundary around it
        if self.lastValue != value  and  value>0  and  self.highlightArea_checkBox.isChecked():
            self.drawAreaHighlight(value)

           
    def getContoursFromAxis(self,axisNumber=-1,value=-1):
        """
        Return a contours array from the axis indexed by integer axisNumber
        i.e. one of the three axes
        """        
        if axisNumber == -1:
            return False

        stackName = self.araName_comboBox.itemText(self.araName_comboBox.currentIndex())
        thisItem = self.lasagna.axes2D[axisNumber].getPlotItemByName(stackName)
        #Make a copy of the image and set values lower than our value to a greater number
        #since the countour finder will draw around everything less than our value
        tmpImage = np.array(thisItem.image)
        tmpImage[tmpImage<value] = value+10
        return measure.find_contours(tmpImage, value)


    def drawAreaHighlight(self, value, highlightOnlyCurrentAxis=False):
        """
        if highlightOnlyCurrentAxis is True, we draw highlights only on the axis we are mousing over
        """
        nans = np.array([np.nan, np.nan, np.nan]).reshape(1,3)
        allContours = nans


        for axNum in range(len(self.lasagna.axes2D)):
            contours = self.getContoursFromAxis(axisNumber=axNum,value=value)


            if (highlightOnlyCurrentAxis == True  and  axNum != self.lasagna.inAxis) or len(contours)==0:
                tmpNan =  np.array([np.nan, np.nan, np.nan]).reshape(1,3)
                tmpNan[0][axNum]=self.lasagna.axes2D[axNum].currentSlice #ensure nothing is plotted in this layer
                allContours = np.append(allContours,tmpNan,axis=0)
                continue

            #print "Plotting area %d in plane %d" % (value,self.lasagna.axes2D[axNum].currentSlice)
            for thisContour in contours:
                tmp = np.ones(thisContour.shape[0]*3).reshape(thisContour.shape[0],3)*self.lasagna.axes2D[axNum].currentSlice

                if axNum==0:
                    tmp[:,1:] = thisContour

                elif axNum==1:
                    tmp[:,0] = thisContour[:,0]
                    tmp[:,2] = thisContour[:,1]

                elif axNum==2:
                    tmp[:,1] = thisContour[:,0]
                    tmp[:,0] = thisContour[:,1]

                tmp = np.append(tmp,nans,axis=0) #Terminate each contour with nans so that they are not  linked
                allContours = np.append(allContours,tmp,axis=0)

            if highlightOnlyCurrentAxis:
                self.lastValue = value 
        
            
        #Replace the data in the ingredient so they are plotted
        self.lasagna.returnIngredientByName(self.contourName)._data = allContours
        [axis.updatePlotItems_2D(self.lasagna.ingredientList) for axis in self.lasagna.axes2D]


            

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

        if self.data['currentlyLoadedAtlasName'] != self.araName_comboBox.itemText(self.araName_comboBox.currentIndex()):
            self.load_pushButton.setEnabled(True) 
        elif self.data['currentlyLoadedAtlasName'] == self.araName_comboBox.itemText(self.araName_comboBox.currentIndex()):
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
                self.loadVolume(fname)
                return

        if self.overlayTemplate_checkBox.isChecked()==False:
            overlayName = fname.split(os.path.sep)[-1]
            self.lasagna.removeIngredientByName(overlayName)

        self.lasagna.returnIngredientByName(self.data['currentlyLoadedAtlasName']).lut='gray'
        self.lasagna.initialiseAxes()

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
        print paths
        #remove the currently loaded ARA (if present)
        if len(self.data['currentlyLoadedAtlasName'])>0:
            self.lasagna.removeIngredientByName(self.data['currentlyLoadedAtlasName'])

        self.data['labels'] = self.loadLabels(paths['labels'])


        self.addAreaDataToTreeView(self.data['labels'],self.rootNode,self.brainArea_itemModel.invisibleRootItem())

        self.data['atlas'] = self.loadVolume(paths['atlas'])        
        self.data['currentlyLoadedAtlasName'] = self.araName_comboBox.itemText(self.araName_comboBox.currentIndex())
        self.data['template']=paths['template']

        if os.path.exists(paths['template']):
            self.overlayTemplate_checkBox.setEnabled(True)
            if self.overlayTemplate_checkBox.isChecked()==True:
                self.addOverlay(self.data['template'])
        else:
            self.overlayTemplate_checkBox.setEnabled(False)


        #self.setARAcolors()
        self.lasagna.initialiseAxes(resetAxes=True)
        self.lasagna.returnIngredientByName(self.data['currentlyLoadedAtlasName']).minMax = [0,1.2E3]
        self.lasagna.initialiseAxes(resetAxes=True)


    def addOverlay(self,fname):
        """
        Add an overlay
        """
        print "ADDING"
        self.loadVolume(fname)
        self.data['currentlyLoadedOverlay'] = fname.split(os.path.sep)[-1]
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
        if nodeID==None:
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
        getFromModel = False #It would be great to get the area ID from the model, but I can't figure out how to get the sub-model that houses the dat

        index = self.brainArea_treeView.selectedIndexes()[0]
        areaName = index.data().toString() 
        if getFromModel:
            #The following row and column indexes are also correct, but index.model() is the root model and this is wrong.
            treeIndex = index.model().item(index.row(),index.column()).data().toInt()[0] 
            print "treeIndex (%d,%d): %d" % (index.row(),index.column(),treeIndex)
        else: #so we do it the stupid way from the reee
            treeIndex = self.AreaName2NodeID(self.data['labels'],areaName)

        if treeIndex != None:
            print "highlighting %d" % treeIndex
            self.drawAreaHighlight(treeIndex,highlightOnlyCurrentAxis=False)


    def loadLabels(self,fname):
        """
        Load the labels file, which may be in JSON or CSV format
        
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


    def setARAcolors(self):
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
        #TODO: is not shutting down properly, although this same code does work in other contexts (e.g. when it was hooked into the load stack method)
        self.lasagna.alert = alert(self.lasagna,alertText=msg)

        self.lasagna.stopPlugin(self.__module__) #This will call self.closePlugin as well as making it possible to restart the plugin
        self.lasagna.pluginActions[self.__module__].setChecked(False) #Uncheck the menu item associated with this plugin's name
        
        self.closePlugin()
