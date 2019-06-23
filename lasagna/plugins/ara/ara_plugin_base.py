import os

from PyQt5 import QtGui

from lasagna.alert import alert
from lasagna.plugins.ara.ara_plotter import ARA_plotter
from lasagna.plugins.lasagna_plugin import LasagnaPlugin

from lasagna.utils.pref_utils import get_lasagna_pref_dir
from lasagna.utils import preferences


class AraPluginBase(ARA_plotter, LasagnaPlugin, QtGui.QWidget):
    def __init__(self, lasagna_serving):
        super(AraPluginBase, self).__init__(lasagna_serving)
        self.lasagna = lasagna_serving

        # Read file locations from preferences file (creating a default file if none exists)
        self.pref_file = get_lasagna_pref_dir() + 'ARA_plugin_prefs.yml'  # FIXME: should be in prefs module
        self.prefs = preferences.loadAllPreferences(prefFName=self.pref_file, defaultPref=self.defaultPrefs())  # FIXME: should be in prefs module

        # The last value the mouse hovered over. When this changes, we re-calculate the contour
        self.lastValue = -1

        # The root node index of the ARA
        self.rootNode = 8

        # Warn and quit if there are no paths
        if not self.prefs['ara_paths']:
            self.warnAndQuit(self.get_missing_ara_paths_in_prefs_warning())
            return

        # Set up the UI
        self.setupUi(self)
        self.show()
        self.statusBarName_checkBox.setChecked(self.prefs['enableNameInStatusBar'])
        self.highlightArea_checkBox.setChecked(self.prefs['enableOverlay'])

        self.link_slots()

        self.paths = self._get_ara_paths()
        if not self.paths:  # If we have no paths to ARAs by the end of this, issue an error alertbox and quit
            self.warnAndQuit(self.get_invalid_ara_paths_in_prefs_warning())
            return

        if self.clear_stacks:
            self.lasagna.removeIngredientByType('imagestack')  # remove all image stacks

        self.data = self._get_data_structure()

        self.autoload_first_ara_entry()

        # Make a lines ingredient that will house the contours for the currently selected area.
        self.addAreaContour()  # from ARA_plotter

    def statusBarName_checkBox_slot(self):
        """
        Remove the area name or add it as soon as the check box is unchecked
        """
        _, image_stack = self.get_atlas_image_stack()

        if not self.statusBarName_checkBox.isChecked():
            self.writeAreaNameInStatusBar(image_stack, False)
        elif self.statusBarName_checkBox.isChecked():
            self.writeAreaNameInStatusBar(image_stack, True)

        self.lasagna.updateStatusBar()

    def highlightArea_checkBox_slot(self):
        """
        Remove the contour or add it as soon as the check box is unchecked
        """
        if not self.highlightArea_checkBox.isChecked():
            self.removeAreaContour()
        elif self.highlightArea_checkBox.isChecked():
            self.addAreaContour()

    def link_slots(self):
        pass

    def _get_repo_url(self):
        return 'http://raacampbell.github.io/lasagna/ara_explorer_plugin.html'

    def get_missing_ara_paths_in_prefs_warning(self):
        return 'Please fill in preferences file at<br>{0}<br><a href="{1}">{1}</a>'\
            .format(self.pref_file, self._get_repo_url())

    def get_invalid_ara_paths_in_prefs_warning(self):
        return 'Found no valid paths in preferences file at<br>{}.<br>SEE <a href="{1}">{1}</a>'\
            .format(self.pref_file, self._get_repo_url())

    def _get_ara_files(self, candidate_files, file_type, prefix, suffix=''):
        for file_name in candidate_files:
            if file_name.startswith(prefix):
                if suffix and file_name.endswith(suffix):
                    continue
                print('Adding {} file {}'.format(file_type, file_name))
                return file_name
        return ''

    def _get_ara_paths(self):
        # Loop through all paths and add to combobox.
        ara_paths = {}
        n = 1
        for candidate_ara_folder in self.prefs['ara_paths']:
            if not os.path.exists(candidate_ara_folder):
                print("{} does not exist. skipping".format(candidate_ara_folder))
                continue

            if not os.listdir(candidate_ara_folder):
                print("No files in {}. skipping".format(candidate_ara_folder))
                continue

            pths = dict(atlas='', labels='')
            print("\n %d. Looking for files in directory %s" % (n, candidate_ara_folder))
            n += 1

            files = os.listdir(candidate_ara_folder)
            atlas_path = self._get_ara_files(files, 'atlas', self.atlasFileName, suffix='raw')
            if not atlas_path:
                print('Skipping empty paths entry')
                continue
            else:
                pths['atlas'] = os.path.join(candidate_ara_folder, atlas_path)

            labels_file = self._get_ara_files(files, 'labels', self.labelsFileName)
            if not labels_file:
                print('Skipping empty paths entry')
                continue
            else:
                pths['labels'] = os.path.join(candidate_ara_folder, labels_file)

            if hasattr(self, 'templateFileName'):
                template_file = self._get_ara_files(files, 'template', self.templateFileName, suffix='raw')
                pths['template'] = os.path.join(candidate_ara_folder, template_file)

            # If we're here, this entry should at least have a valid atlas file and a valid labels file
            # We will index the ara_paths dictionary by the name of the atlas file as this is also
            # what will be put into the combobox.
            atlas_dir_name = os.path.basename(os.path.dirname(candidate_ara_folder))

            # skip if a file with this name already exists
            if atlas_dir_name in ara_paths:
                print("Skipping as a directory called {} is already in the list".format(atlas_dir_name))
            else:
                # Add this ARA to the paths dictionary and to the combobox
                ara_paths[atlas_dir_name] = pths
                self.araName_comboBox.addItem(atlas_dir_name)
        print("")  # blank line
        return ara_paths

    # HOOKS
    # all methods starting with hook_ are automatically registered as hooks with lasagna
    # when the plugin is started this happens in the LasagnaPlugin constructor
    def hook_updateStatusBar_End(self):
        """
        hooks into the status bar update function to show the brain area name in the status bar
        as the user mouses over the images
        """
        # Get the atlas volume and find in which voxel the mouse cursor is located
        atlas_layer_name, image_stack = self.get_atlas_image_stack('hook_updateStatusBar_End')
        if image_stack is None:
            return

        # Inherited from ARA_plotter
        value = self.writeAreaNameInStatusBar(image_stack, self.statusBarName_checkBox.isChecked())

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

# ----------------------------
    # Methods to handle close events and errors
    def deregister_from_lasagna(self):
        self.lasagna.stopPlugin(self.__module__)  # This will call self.closePlugin
        # Uncheck the menu item associated with this plugin's name
        self.lasagna.pluginActions[self.__module__].setChecked(False)

    def closePlugin(self):
        """
        Runs when the user unchecks the plugin in the menu box and also (in this case)
        when the user loads a new image stack
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
        self.deregister_from_lasagna()

        # self.closePlugin()  # already called by lasagna
        self.deleteLater()
        event.accept()

    def warnAndQuit(self, msg):
        """
        Display alert and (maybe) quit the plugin
        """
        self.lasagna.alert = alert(self.lasagna, alertText=msg)
        self.deregister_from_lasagna()

        # TODO: If we close the plugin the warning vanishes right away
        # self.closePlugin()