
"""
Overlays brain area onto a registered sample brain without overlaying the atlas.
"""

import os

import numpy as np
from PyQt5 import QtGui

from lasagna.io_libs import image_stack_loader
# For the UI
from lasagna.plugins.ara import area_namer_UI
# For contour drawing
from lasagna.plugins.ara.ara_plugin_base import AraPluginBase
from lasagna.utils import preferences


class plugin(AraPluginBase, area_namer_UI.Ui_area_namer):
    def __init__(self, lasagna_serving):
        self.pluginAuthor = "Rob Campbell"
        self.pluginShortName = "area namer"
        self.pluginLongName = "brain area namer"

        # Default names of the files that we need:
        self.atlasFileName = 'atlas'
        self.labelsFileName = 'labels'
        self.clear_stacks = False
        super(plugin, self).__init__(lasagna_serving)

    def autoload_first_ara_entry(self):  # For compatibility with sibling classes
        pass

    def _get_data_structure(self):
        return dict(currentlyLoadedAtlasName='', currentlyLoadedOverlay='', atlas=np.ndarray([]))

    def link_slots(self):
        """Link signals to slots"""
        self.araName_comboBox.activated.connect(self.araName_comboBox_slot)
        self.loadOrig_pushButton.released.connect(self.loadOrig_pushButton_slot)
        self.loadOther_pushButton.released.connect(self.loadOther_pushButton_slot)
        self.statusBarName_checkBox.stateChanged.connect(self.statusBarName_checkBox_slot)
        self.highlightArea_checkBox.stateChanged.connect(self.highlightArea_checkBox_slot)

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
        self.data['atlas'] = image_stack_loader.load_stack(paths['atlas'])

        self.data['currentlyLoadedAtlasName'] = paths['atlas'].split(os.path.sep)[-1]

    def loadOther_pushButton_slot(self, fnameToLoad=False):
        """
        Load a user-selected atlas file but use the labels from the ARA in the drop-down box.
        Can optionally load a specific file name (used for de-bugging)
        """
        if not fnameToLoad:
            file_filter = "Images (*.mhd *.mha *.tiff *.tif *.nrrd)"
            fnameToLoad = QtWidgets.QFileDialog.getOpenFileName(self,
                                                            'Open file',
                                                            preferences.readPreference('lastLoadDir'),
                                                            file_filter)
            fnameToLoad = str(fnameToLoad[0])  # tuple with filter as 2nd value

        # re-load labels
        selected_name = str(self.araName_comboBox.itemText(self.araName_comboBox.currentIndex()))
        paths = self.paths[selected_name]
        self.data['labels'] = self.loadLabels(paths['labels'])

        # load the selected atlas (without displaying it)
        self.data['atlas'] = image_stack_loader.load_stack(fnameToLoad)

        self.data['currentlyLoadedAtlasName'] = fnameToLoad.split(os.path.sep)[-1]

    def get_atlas_image_stack(self, plugin_name=None):
        return None, self.data['atlas']
