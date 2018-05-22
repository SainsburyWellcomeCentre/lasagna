
"""
Overlays brain area onto a registered sample brain without overlaying the atlas.
"""

import os.path

import numpy as np
from PyQt5 import QtGui

from lasagna import lasagna_helperFunctions as lasHelp
from lasagna.alert import alert
from lasagna.io_libs import image_stack_loader
# For the UI
from lasagna.plugins.ara import area_namer_UI
# For contour drawing
from lasagna.plugins.ara.ara_plotter import ARA_plotter
from lasagna.plugins.lasagna_plugin import lasagna_plugin


class plugin(ARA_plotter, lasagna_plugin, QtGui.QWidget, area_namer_UI.Ui_area_namer): 
    def __init__(self, lasagna):
        super(plugin, self).__init__(lasagna)
        self.lasagna = lasagna

        self.pluginShortName = "area namer"
        self.pluginLongName = "brain area namer"
        self.pluginAuthor = "Rob Campbell"

        # Read file locations from preferences file (creating a default file if none exists)
        self.pref_file = lasHelp.getLasagna_prefDir() + 'ARA_plugin_prefs.yml'
        self.prefs = lasHelp.loadAllPreferences(prefFName=self.pref_file, defaultPref=self.defaultPrefs())

        # The last value the mouse hovered over. When this changes, we re-calculate the contour
        self.lastValue = -1

        # Default names of the three files that we need:
        self.atlasFileName = 'atlas'
        self.labelsFileName = 'labels'

        # The root node index of the ARA
        self.rootNode = 8

        # Warn and quit if there are no paths
        if not self.prefs['ara_paths']:
            self.warnAndQuit('Please fill in preferences file at<br>%s<br><a href='
                             '"http://raacampbell13.github.io/lasagna/ara_explorer_plugin.html">'
                             'http://raacampbell13.github.io/lasagna/ara_explorer_plugin.html</a>' % self.pref_file)
            return

        # Set up the UI
        self.setupUi(self)
        self.show()
        self.statusBarName_checkBox.setChecked(self.prefs['enableNameInStatusBar'])
        self.highlightArea_checkBox.setChecked(self.prefs['enableOverlay'])

        # Link signals to slots
        self.araName_comboBox.activated.connect(self.araName_comboBox_slot)
        self.loadOrig_pushButton.released.connect(self.loadOrig_pushButton_slot)
        self.loadOther_pushButton.released.connect(self.loadOther_pushButton_slot)

        self.statusBarName_checkBox.stateChanged.connect(self.statusBarName_checkBox_slot)
        self.highlightArea_checkBox.stateChanged.connect(self.highlightArea_checkBox_slot)

        # Loop through all paths and add to combobox.
        self.paths = dict()
        n = 1
        for path in self.prefs['ara_paths']:
            if not os.path.exists(path):
                print("%s does not exist. skipping" % path) 
                continue

            if not os.listdir(path):
                print("No files in %s . skipping" % path)
                continue

            pths = dict(atlas='', labels='')
            print("\n %d. Looking for files in directory %s" % (n, path))
            n += 1

            files = os.listdir(path)

            # get the file names
            for thisFile in files:
                if thisFile.startswith(self.atlasFileName):
                    if thisFile.endswith('raw'):
                        continue
                    pths['atlas'] = os.path.join(path, thisFile)
                    print("Adding atlas file %s" % thisFile)
                    break 

            for thisFile in files:
                if thisFile.startswith(self.labelsFileName):
                    pths['labels'] = os.path.join(path, thisFile)
                    print("Adding labels file %s" % thisFile)
                    break 

            if not pths['atlas'] or not pths['labels']:
                print('Skipping empty empty paths entry')
                continue

            # If we're here, this entry should at least have a valid atlas file and a valid labels file
            # We will index the self.paths dictionary by the name of the atlas file as this is also
            # what will be put into the combobox.
            atlas_dir_name = path.split(os.path.sep)[-1]

            # skip if a file with this name already exists
            if atlas_dir_name in self.paths:
                print("Skipping as a directory called %s is already in the list" % atlas_dir_name)
                continue

            # Add this ARA to the paths dictionary and to the combobox
            self.paths[atlas_dir_name] = pths
            self.araName_comboBox.addItem(atlas_dir_name)

        # blank line
        print("")

        # If we have no paths to ARAs by the end of this, issue an error alertbox and quit
        if not self.paths:
            self.warnAndQuit('Found no valid paths in preferences file at<br>%s.<br>SEE <a href='
                             '"http://raacampbell13.github.io/lasagna/ara_explorer_plugin.html"'
                             '>http://raacampbell13.github.io/lasagna/ara_explorer_plugin.html</a>' % self.pref_file)
            return

        # If the user has asked for this, load the first ARA entry automatically
        self.data = dict(currentlyLoadedAtlasName='', currentlyLoadedOverlay='', atlas=np.ndarray([])) 

        # Make a lines ingredient that will house the contours for the currently selected area.
        self.addAreaContour()  # from ARA_plotter

    # --------------------------------------
    # plugin hooks
    # all methods starting with hook_ are automatically registered as hooks with lasagna
    # when the plugin is started this happens in the lasagna_plugin constructor
    def hook_updateStatusBar_End(self):
        """
        hooks into the status bar update function to show the brain area name in the status bar 
        as the user mouses over the images
        """
        image_stack = self.data['atlas']
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
    # when the plugin is started this happens in the lasagna_plugin constructor
    def araName_comboBox_slot(self):
        """
        Enables the load button only if the currently selected item is not loaded
        """
        # If nothing has been loaded then for sure we need the load button enabled
        if not self.data['currentlyLoadedAtlasName']:
            self.loadOrig_pushButton.setEnabled(True) 
            return

        if self.data['currentlyLoadedAtlasName'] != str(self.araName_comboBox.itemText(self.araName_comboBox.currentIndex())):  # FIXME: else ?
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
        selected_name = str(self.araName_comboBox.itemText(self.araName_comboBox.currentIndex()))

        paths = self.paths[selected_name]

        # Load the labels (this associates brain area index values with brain area names)
        self.data['labels'] = self.loadLabels(paths['labels'])

        # Load the raw image data but do not display it.
        self.data['atlas'] = image_stack_loader.loadStack(paths['atlas'])

        self.data['currentlyLoadedAtlasName'] = paths['atlas'].split(os.path.sep)[-1]

    def loadOther_pushButton_slot(self, fnameToLoad=False):
        """
        Load a user-selected atlas file but use the labels from the ARA in the drop-down box.
        Can optionally load a specific file name (used for de-bugging)
        """
        if not fnameToLoad:
            file_filter = "Images (*.mhd *.mha *.tiff *.tif *.nrrd)"
            fnameToLoad = QtGui.QFileDialog.getOpenFileName(self,
                                                            'Open file',
                                                            lasHelp.readPreference('lastLoadDir'),
                                                            file_filter)
            fnameToLoad = str(fnameToLoad[0])  # tuple with filter as 2nd value

        # re-load labels
        selected_name = str(self.araName_comboBox.itemText(self.araName_comboBox.currentIndex()))
        paths = self.paths[selected_name]
        self.data['labels'] = self.loadLabels(paths['labels'])

        # load the selected atlas (without displaying it)
        self.data['atlas'] = image_stack_loader.loadStack(fnameToLoad)

        self.data['currentlyLoadedAtlasName'] = fnameToLoad.split(os.path.sep)[-1]

    def statusBarName_checkBox_slot(self):
        """
        Remove the area name or add it as soon as the check box is unchecked
        """
        if not self.statusBarName_checkBox.isChecked():
            self.writeAreaNameInStatusBar(self.data['atlas'], False)
        elif self.statusBarName_checkBox.isChecked():
            self.writeAreaNameInStatusBar(self.data['atlas'], True)
            
        self.lasagna.updateStatusBar()

    def highlightArea_checkBox_slot(self):
        """
        Remove the contour or add it as soon as the check box is unchecked
        """
        if not self.highlightArea_checkBox.isChecked():
            self.removeAreaContour()
        elif self.highlightArea_checkBox.isChecked():
            self.addAreaContour()

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
