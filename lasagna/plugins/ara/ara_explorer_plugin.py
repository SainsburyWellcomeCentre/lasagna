
"""
lasagna plugin for exploring the Allen Brain Atlas:
1. Display of average template brain.
2. Reporting of brain area name
more stuff... 
plugin under construction

"""

import os

from PyQt5 import QtGui, QtCore


from lasagna.alert import alert
# For the UI
from lasagna.plugins.ara import ara_explorer_UI
# For contour drawing
from lasagna.plugins.ara.ara_plotter import ARA_plotter
from lasagna.plugins.lasagna_plugin import LasagnaPlugin
from lasagna.utils.pref_utils import get_lasagna_pref_dir
from lasagna.utils import preferences


class plugin(ARA_plotter, LasagnaPlugin, QtGui.QWidget, ara_explorer_UI.Ui_ara_explorer):
    def __init__(self, lasagna_serving):
        super(plugin, self).__init__(lasagna_serving)
        self.lasagna = lasagna_serving

        self.pluginShortName = "ARA explorer"
        self.pluginLongName = "Allen Reference Atlas explorer"
        self.pluginAuthor = "Rob Campbell"

        # Read file locations from preferences file (creating a default file if none exists)
        self.pref_file = get_lasagna_pref_dir() + 'ARA_plugin_prefs.yml'
        self.prefs = preferences.loadAllPreferences(prefFName=self.pref_file, defaultPref=self.defaultPrefs())

        # The last value the mouse hovered over. When this changes, we re-calculate the contour
        self.lastValue = -1

        # Default names of the three files that we need:
        self.atlasFileName = 'atlas'
        self.templateFileName = 'template'
        self.labelsFileName = 'labels'

        # The root node index of the ARA
        self.rootNode = 8

        # Warn and quit if there are no paths
        if not self.prefs['ara_paths']:
            self.warnAndQuit('Please fill in preferences file at<br>%s<br><a href='
                             '"http://raacampbell.github.io/lasagna/ara_explorer_plugin.html">'
                             'http://raacampbell.github.io/lasagna/ara_explorer_plugin.html</a>' % self.pref_file)
            return

        # Set up the UI
        self.setupUi(self)
        self.show()
        self.statusBarName_checkBox.setChecked(self.prefs['enableNameInStatusBar'])
        self.highlightArea_checkBox.setChecked(self.prefs['enableOverlay'])
        
        self.brainArea_itemModel = QtGui.QStandardItemModel(self.brainArea_treeView)
        self.brainArea_treeView.setModel(self.brainArea_itemModel)

        # Link the selections in the tree view to a slot in order to allow highlighting of the selected area
        self.brainArea_treeView.selectionModel().selectionChanged[QtCore.QItemSelection, QtCore.QItemSelection].connect(self.highlightSelectedAreaFromList)

        # Link signals to slots
        self.araName_comboBox.activated.connect(self.araName_comboBox_slot)
        self.load_pushButton.released.connect(self.load_pushButton_slot)
        self.overlayTemplate_checkBox.stateChanged.connect(self.overlayTemplate_checkBox_slot)

        self.statusBarName_checkBox.stateChanged.connect(self.statusBarName_checkBox_slot)
        self.highlightArea_checkBox.stateChanged.connect(self.highlightArea_checkBox_slot)

        # Loop through all paths and add to combobox.
        self.paths = dict()
        n = 1
        for path in self.prefs['ara_paths']:
            if not os.path.exists(path):
                print("{} does not exist. skipping".format(path))
                continue

            if not os.listdir(path):
                print("No files in {}. skipping".format(path))
                continue

            pths = dict(atlas='', labels='')
            print("\n %d. Looking for files in directory %s" % (n, path))
            n += 1

            files = os.listdir(path)

            # get the file names
            for fname in files:
                if fname.startswith(self.atlasFileName):
                    if fname.endswith('raw'):
                        continue
                    pths['atlas'] = os.path.join(path, fname)
                    print("Adding atlas file {}".format(fname))
                    break 

            for fname in files:
                if fname.startswith(self.labelsFileName):
                    pths['labels'] = os.path.join(path, fname)
                    print("Adding labels file {}".format(fname))
                    break 

            pths['template'] = ''
            for fname in files:
                if fname.startswith(self.templateFileName):
                    if fname.endswith('raw'):
                        continue
                    pths['template'] = os.path.join(path, fname)
                    print("Adding template file {}".format(fname))
                    break

            if not pths['atlas'] or not pths['labels']:
                print('Skipping empty empty paths entry')
                continue

            # If we're here, this entry should at least have a valid atlas file and a valid labels file
            # We will index the self.paths dictionary by the name of the atlas file as this is also
            # what will be put into the combobox.
            atlas_dir_name = path.split(os.path.sep)[-1]  # FIXME: use os.path.dirname or basename

            # skip if a file with this name already exists
            if atlas_dir_name in self.paths:
                print("Skipping as a directory called {} is already in the list".format(atlas_dir_name))
                continue

            # Add this ARA to the paths dictionary and to the combobox
            self.paths[atlas_dir_name] = pths
            self.araName_comboBox.addItem(atlas_dir_name)

        # blank line
        print("")

        # If we have no paths to ARAs by the end of this, issue an error alertbox and quit
        if not self.paths:
            self.warnAndQuit('Found no valid paths in preferences file at<br>%s.<br>SEE <a href='
                             '"http://raacampbell.github.io/lasagna/ara_explorer_plugin.html"'
                             '>http://raacampbell.github.io/lasagna/ara_explorer_plugin.html</a>' % self.pref_file)
            return

        self.lasagna.removeIngredientByType('imagestack')  # remove all image stacks

        # If the user has asked for this, load the first ARA entry automatically
        self.data = dict(currentlyLoadedAtlasName='', currentlyLoadedOverlay='')

        currently_selected_ara = str(self.araName_comboBox.itemText(self.araName_comboBox.currentIndex()))
        if self.prefs['loadFirstAtlasOnStartup']:
            print("Auto-Loading " + currently_selected_ara)
            self.loadARA(currently_selected_ara)
            self.load_pushButton.setEnabled(False)  # disable because the current selection has now been loaded

        # Make a lines ingredient that will house the contours for the currently selected area.
        self.contourName = 'aracontour'
        self.lasagna.addIngredient(objectName=self.contourName,
                                   kind='lines',
                                   data=[])
        self.lasagna.returnIngredientByName(self.contourName).addToPlots()  # Add item to all three 2D plots
        # End of constructor

    # --------------------------------------
    # plugin hooks
    # all methods starting with hook_ are automatically registered as hooks with lasagna
    # when the plugin is started this happens in the LasagnaPlugin constructor
    def hook_updateStatusBar_End(self):
        """
        hooks into the status bar update function to show the brain area name in the status bar 
        as the user mouses over the images
        """

        # Get the atlas volume and find in which voxel the mouse cursor is located
        ara_name = str(self.araName_comboBox.itemText(self.araName_comboBox.currentIndex()))
        atlas_layer_name = self.paths[ara_name]['atlas'].split(os.path.sep)[-1]
        ingredient = self.lasagna.returnIngredientByName(atlas_layer_name)

        if not ingredient:
            print("ARA_explorer_plugin.hook_updateStatusBar_End Failed to find image_stack named {}"
                  .format(atlas_layer_name))
            return

        image_stack = self.lasagna.returnIngredientByName(atlas_layer_name).raw_data()

        value = self.writeAreaNameInStatusBar(image_stack, self.statusBarName_checkBox.isChecked())  # Inherited from ARA_plotter

        # Highlight the brain area we are mousing over by drawing a boundary around it
        if self.lastValue != value and self.highlightArea_checkBox.isChecked():
            self.drawAreaHighlight(image_stack, value)  # Inherited from ARA_plotter

    def hook_deleteLayerStack_Slot_End(self):
        """
        Runs when a stack is removed. Watches for the removal of the current atlas and 
        triggers closing of the plugin if it is removed.
        """
        # is the current loaded atlas present
        atlas_name = self.data['currentlyLoadedAtlasName']
        if not self.lasagna.returnIngredientByName(atlas_name):
            print("The current atlas has been removed by the user. Closing the ARA explorer plugin")
            self.closePlugin()

    # --------------------------------------
    # UI slots
    # all methods starting with hook_ are automatically registered as hooks with lasagna
    # when the plugin is started this happens in the LasagnaPlugin constructor
    def araName_comboBox_slot(self):
        """
        Enables the load button only if the currently selected item is not loaded
        """
        # If nothing has been loaded then for sure we need the load button enabled
        if not self.data['currentlyLoadedAtlasName']:
            self.load_pushButton.setEnabled(True) 
            return

        if self.data['currentlyLoadedAtlasName'] != str(self.araName_comboBox.itemText(self.araName_comboBox.currentIndex())):  # FIXME: else ?
            self.load_pushButton.setEnabled(True) 
        elif self.data['currentlyLoadedAtlasName'] == str(self.araName_comboBox.itemText(self.araName_comboBox.currentIndex())):
            self.load_pushButton.setEnabled(False)

    def load_pushButton_slot(self):
        """
        Load the currently selected ARA version
        """
        selected_name = str(self.araName_comboBox.itemText(self.araName_comboBox.currentIndex()))
        self.loadARA(selected_name)

    def overlayTemplate_checkBox_slot(self):
        """
        Load or unload the template overlay
        """
        fname = self.data['template']
        if not fname:
            return

        if self.overlayTemplate_checkBox.isChecked():
            if os.path.exists(fname):
                self.addOverlay(fname)
                return

        if not self.overlayTemplate_checkBox.isChecked():
            overlay_name = fname.split(os.path.sep)[-1]
            self.lasagna.removeIngredientByName(overlay_name)

        self.lasagna.returnIngredientByName(self.data['currentlyLoadedAtlasName']).lut = 'gray'
        self.lasagna.initialiseAxes()

    def statusBarName_checkBox_slot(self):
        """
        Remove the area name or add it as soon as the check box is unchecked
        """
        ara_name = str(self.araName_comboBox.itemText(self.araName_comboBox.currentIndex()))
        atlas_layer_name = self.paths[ara_name]['atlas'].split(os.path.sep)[-1]
        imageStack = self.lasagna.returnIngredientByName(atlas_layer_name).raw_data()
        
        if not self.statusBarName_checkBox.isChecked():
            self.writeAreaNameInStatusBar(imageStack, False)
        elif self.statusBarName_checkBox.isChecked():
            self.writeAreaNameInStatusBar(imageStack, True)
            
        self.lasagna.updateStatusBar()

    def highlightArea_checkBox_slot(self):
        """
        Remove the contour or add it as soon as the check box is unchecked
        """
        if not self.highlightArea_checkBox.isChecked():
            self.removeAreaContour()
        elif self.highlightArea_checkBox.isChecked():
            self.addAreaContour()
            
    # --------------------------------------
    # core methods: these do the meat of the work
    def loadARA(self, araName):
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

        # remove the currently loaded ARA (if present)
        if self.data['currentlyLoadedAtlasName']:
            self.lasagna.removeIngredientByName(self.data['currentlyLoadedAtlasName'])

        self.data['labels'] = self.loadLabels(paths['labels'])  # see ARA_plotter.py

        self.addAreaDataToTreeView(self.data['labels'], self.rootNode, self.brainArea_itemModel.invisibleRootItem())

        self.lasagna.loadImageStack(paths['atlas'])
        
        self.data['currentlyLoadedAtlasName'] = paths['atlas'].split(os.path.sep)[-1]

        self.data['template'] = paths['template']
        if os.path.exists(paths['template']):
            self.overlayTemplate_checkBox.setEnabled(True)
            if self.overlayTemplate_checkBox.isChecked():
                self.addOverlay(self.data['template'])
        else:
            self.overlayTemplate_checkBox.setEnabled(False)

        # self.setARAcolors()
        # self.lasagna.initialiseAxes(resetAxes=True)
        self.lasagna.returnIngredientByName(self.data['currentlyLoadedAtlasName']).minMax = [0, 1.2E3]
        self.lasagna.initialiseAxes(resetAxes=True)

    def addOverlay(self, fname):
        """
        Add an overlay
        """
        self.lasagna.loadImageStack(fname)
        self.data['currentlyLoadedOverlay'] = str(fname.split(os.path.sep)[-1])
        self.lasagna.returnIngredientByName(self.data['currentlyLoadedAtlasName']).lut = 'gray'
        self.lasagna.returnIngredientByName(self.data['currentlyLoadedOverlay']).lut = 'cyan'
        self.lasagna.returnIngredientByName(self.data['currentlyLoadedOverlay']).minMax = [0, 1.5E3]
        self.lasagna.initialiseAxes(resetAxes=True)

    # ---------------
    # Methods to handle the tree
    def addAreaDataToTreeView(self, thisTree, nodeID, parent):
        """
        Add a tree structure of area names to the QListView
        """
        children = thisTree[nodeID].children
        for child in sorted(children):
            child_item = QtGui.QStandardItem(thisTree[child].data['name'])
            child_item.setData(child)  # Store index. Can be retrieved by: child_item.data().toInt()[0] NOT USING THIS RIGHT NOW
            parent.appendRow(child_item)
            self.addAreaDataToTreeView(thisTree, child, child_item)

    def AreaName2NodeID(self, thisTree, name, nodeID=None):
        """
        Searches the tree for a brain area called name and returns the node ID (atlas index value)
        Breaks out of the search loop if the area is found and propagates the value back through
        the recursive function calls
        """
        if nodeID is None:
            nodeID = self.rootNode
        
        children = thisTree[nodeID].children
        for child in sorted(children):
            if thisTree[child].data['name'] == name:
                return child
            else:
                return_val = self.AreaName2NodeID(thisTree=thisTree, name=name, nodeID=child)
                if return_val:
                    return return_val
        return False

    def highlightSelectedAreaFromList(self):
        """
        This slot is run when the user clicks on a brain area in the list
        """
        get_from_model = False  # It would be great to get the area ID from the model, but I can't figure out how to get the sub-model that houses the data

        index = self.brainArea_treeView.selectedIndexes()[0]

        # Get the image stack, as we need to feed it to drawAreaHighlight
        ara_name = str(self.araName_comboBox.itemText(self.araName_comboBox.currentIndex()))
        atlas_layer_name = self.paths[ara_name]['atlas'].split(os.path.sep)[-1]
        image_stack = self.lasagna.returnIngredientByName(atlas_layer_name).raw_data()

        if get_from_model:
            # The following row and column indexes are also correct, but index.model() is the root model and this is wrong.
            tree_index = index.model().item(index.row(), index.column()).data().toInt()[0]
            print("tree_index (%d,%d): %d" % (index.row(), index.column(), tree_index))
        else:  # so we do it the stupid way from the reee
            area_name = index.data()
            tree_index = self.AreaName2NodeID(self.data['labels'], area_name)

        if tree_index is not None:
            # print("highlighting %d" % tree_index)
            self.drawAreaHighlight(image_stack, tree_index, highlightOnlyCurrentAxis=False)

    # ----------------------------
    # Methods to handle close events and errors
    def closePlugin(self):
        """
        Runs when the user unchecks the plugin in the menu box and also (in this case)
        when the user loads a new base stack
        """
        # remove the currently loaded ARA (if present)
        self.lasagna.removeIngredientByName('aracontour')

        if self.data['currentlyLoadedAtlasName']:
            self.lasagna.removeIngredientByName(self.data['currentlyLoadedAtlasName'])

        if self.data['currentlyLoadedOverlay']:
            self.lasagna.removeIngredientByName(self.data['currentlyLoadedOverlay'])

        # self.lasagna.intensityHistogram.clear()
        self.detachHooks()
        self.lasagna.statusBar.showMessage("ARA explorer closed")
        self.close()

    def closeEvent(self, event):
        """
        This event is execute when the user presses the close window (cross) button in the title bar
        """
        self.lasagna.stopPlugin(self.__module__)  # This will call self.closePlugin
        self.lasagna.pluginActions[self.__module__].setChecked(False)  # Uncheck the menu item associated with this plugin's name

        self.closePlugin()
        self.deleteLater()
        event.accept()

    def warnAndQuit(self, msg):
        """
        Display alert and (maybe) quit the plugin
        """
        self.lasagna.alert = alert(self.lasagna, alertText=msg)
        self.lasagna.stopPlugin(self.__module__)  # This will call self.closePlugin
        self.lasagna.pluginActions[self.__module__].setChecked(False)  # Uncheck the menu item associated with this plugin's name

        # TODO: If we close the plugin the warning vanishes right away
        # self.closePlugin()
