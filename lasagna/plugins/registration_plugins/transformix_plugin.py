

"""
Transformix plugin for Lasagna 
Rob Campbell
"""

import os
import re
import subprocess  # To run the transformix binary
import time

from PyQt5 import QtGui, QtCore

import lasagna.utils.path_utils
import lasagna.utils.preferences
from lasagna.plugins.lasagna_plugin import lasagna_plugin
from lasagna.plugins.registration_plugins import transformix_plugin_UI
from lasagna.plugins.registration_plugins import which  # To test if binaries exist in system path
from lasagna.utils import lasagna_qt_helper_functions as las_help


class plugin(lasagna_plugin, QtGui.QWidget, transformix_plugin_UI.Ui_transformix_plugin):  # must inherit lasagna_plugin first

    def __init__(self, lasagna_serving, parent=None):

        super(plugin, self).__init__(lasagna_serving)  # This calls the lasagna_plugin constructor which in turn calls subsequent constructors

        # Is the Transformix (or Elastix) binary in the system path?
        # We search for both in case we in the future add the ability to calculate inverse transforms and other good stuff
        if which('transformix') is None or which('elastix') is None:
            #TODO: does it stop properly? Will we have to uncheck and recheck the plugin menu item to get it to run a second time?
            from lasagna.alert import alert
            self.alert = alert(lasagna_serving,
                               'The elastix or transformix binaries do not appear'
                               ' to be in your path.<br>Not starting plugin.')
            self.lasagna.pluginActions[self.__module__].setChecked(False)  # Uncheck the menu item associated with this plugin's name
            self.deleteLater()
            return
        else:
            print("Using transformix binary at " + which('transformix'))
            print("Using elastix binary at " + which('elastix'))


        # re-define some default properties that were originally defined in lasagna_plugin
        self.pluginShortName = 'Transformix'  # Appears on the menu
        self.pluginLongName = 'registration of images'  # Can be used for other purposes (e.g. tool-tip)
        self.pluginAuthor = 'Rob Campbell'

        # This is the file name we monitor during running
        self.elastixLogName = 'elastix.log'
        self.transformixLogName = 'transformix.log'
        self.transformixCommand = ''  # the command we will run

        # Create widgets defined in the designer file
        self.setupUi(self)
        self.show()

        # A dictionary for storing location of temporary parameter files
        # Temporary parameter files are created as the user edits them and are
        # removed when the registration starts
        self.tmpParamFiles = {}

        # Create some properties which we will need
        self.inputImagePath = ''  # absolute path to the image we will transform
        self.transformPath = ''  # absolute path to the tranform file we will use
        self.outputDirPath = ''
        self.transformixCommand = ''

        # Link signals to slots
        self.chooseStack_pushButton.released.connect(self.chooseStack_slot)
        self.chooseTransform_pushButton.released.connect(self.chooseTransform_slot)
        self.outputDirSelect_pushButton.released.connect(self.selectOutputDir_slot)

        self.run_pushButton.released.connect(self.run_slot)
        self.loadResult_pushButton.released.connect(self.loadResult_slot)

        # Disable UI elements that won't be available until the user has completed all actions
        self.run_pushButton.setEnabled(False)
        self.loadResult_pushButton.setEnabled(False)

        # -------------------------------------------------------------------------------------
        # The following will either be hugely changed or deleted when the plugin is no longer
        # under heavy development
        debug = False  # runs certain things quickly to help development
        if debug and os.path.expanduser("~") == '/home/rob':  # Ensure only I can trigger this. Ensures that it doesn't activate if I accidently push with debug enabled
            self.inputImagePath = '' # absolute path to the image we will transform
            self.transformPath = ''  # absolute path to the tranform file we will use
        # -------------------------------------------------------------------------------------

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # Slots
    def chooseStack_slot(self, fname_to_choose=False):
        """
        Choose the stack to transform
        can optionally load a specific file name (used for de-bugging)
        """
        if not fname_to_choose:
            file_filter = "Images (*.mhd *.mha)"
            fname_to_choose = QtGui.QFileDialog.getOpenFileName(self,
                                                                'Choose stack',
                                                                lasagna.utils.preferences.readPreference('lastLoadDir'),
                                                                file_filter)
            fname_to_choose = str(fname_to_choose)
        if os.path.exists(fname_to_choose):
            self.inputImagePath = fname_to_choose
        else:
            self.inputImagePath = ''
            # TODO: make an alert box for this case
            print("that file does not exits")
        
        self.checkIfReadyToRun()
        lasagna.utils.preferences.preferenceWriter('lastLoadDir', lasagna.utils.path_utils.stripTrailingFileFromPath(fname_to_choose))
        self.stackName_label.setText(fname_to_choose.split(os.path.sep)[-1])

    def chooseTransform_slot(self, fname_to_choose=False):
        """
        Choose the transform file to use
        can optionally load a specific file name (used for de-bugging)
        """
        if not fname_to_choose:
            file_filter = "Images (*.txt)"
            fname_to_choose = QtGui.QFileDialog.getOpenFileName(self,
                                                                'Choose transform',
                                                                lasagna.utils.preferences.readPreference('lastLoadDir'),
                                                                file_filter)
            fname_to_choose = str(fname_to_choose)

        if os.path.exists(fname_to_choose):
            self.transformPath = fname_to_choose
        else:
            self.transformPath = ''
            # TODO: make an alert box for this case
            print("that file does not exits")

        self.checkIfReadyToRun()
        lasagna.utils.preferences.preferenceWriter('lastLoadDir', lasagna.utils.path_utils.stripTrailingFileFromPath(fname_to_choose))
        self.transformName_label.setText(fname_to_choose.split(os.path.sep)[-1])

    def selectOutputDir_slot(self):
        """
        Select the Transformix output directory via a QFileDialog
        """
        selected_dir = str(QtGui.QFileDialog.getExistingDirectory(self, "Select Directory"))
        # TODO: check if directory is not empty. If it's not empty, prompt to delete contents
        self.outputDir_label.setText(selected_dir)
        
        if os.path.exists(selected_dir):
            self.outputDirPath = selected_dir
        else:
            self.outputDirPath = ''

        self.checkIfReadyToRun()

    def run_slot(self):
        """
        Run the transformix session
        """

        if not self.transformixCommand:
            print("transformix command is empty")
            return False

        # Run command (non-blocking in the background)
        cmd = self.transformixCommand
        print("Running:\n" + cmd)

        # Pipe everything to /dev/null if that's an option
        if os.name in ('posix', 'mac'):
            cmd += "  > /dev/null 2>&1"
    
        # If the log file exists already, delete it
        path_to_log = os.path.join(self.outputDirPath, self.transformixLogName)
        if os.path.exists(path_to_log):
            os.remove(path_to_log)

        # Deactivate the UI elements whilst we're running
        self.labelCommand.setText('RUNNING...')
        self.run_pushButton.setEnabled(False)
        self.loadResult_pushButton.setEnabled(False)
        self.chooseStack_pushButton.setEnabled(False)
        self.chooseTransform_pushButton.setEnabled(False)
        self.outputDirSelect_pushButton.setEnabled(False)
        QtCore.QCoreApplication.processEvents()  # TODO: does not work

        # Watch for completion
        running = True
        time.sleep(0.1)
        subprocess.Popen(cmd, shell=True)  # The command is now run
        success = False
        while running:
            if not os.path.exists(path_to_log):  # wait for the file to appear
                time.sleep(0.15)
                continue

            if self.lookForStringInFile(path_to_log, 'Errors occurred'):
                print("FAILED")
                running = False

            if self.lookForStringInFile(path_to_log, 'Elapsed time'):
                print("FINISHED!")
                success = True
                running = False

        # Return to the original state so we can start another round
        self.labelCommand.setText('Command...')

        self.chooseStack_pushButton.setEnabled(True)
        self.chooseTransform_pushButton.setEnabled(True)
        self.outputDirSelect_pushButton.setEnabled(True)

        self.stackName_label.setText('')
        self.transformName_label.setText('') 
        self.outputDir_label.setText('')

        if success:  # Display result if it is available
            self.loadResult_pushButton.setEnabled(True)
            self.commandText_label.setText('Transform sucessful ')
        else:
            self.commandText_label.setText('Transform FAILED! See %s for details ' % path_to_log)

    def loadResult_slot(self):
        """
        Show the result image in the main view.
        """
        # Find the result image format
        path_to_log = os.path.join(self.outputDirPath, self.transformixLogName)
        if not os.path.exists(path_to_log):
            print("Can not find " + path_to_log)
            return False

        file_extension = ''
        with open(path_to_log, 'r') as fid:
            for line in fid:
                match = re.match('\(ResultImageFormat "(\w+)"', line)
                if match is not None:
                    g = match.groups()
                    if g:
                        file_extension = g[0]

        if not file_extension:
            print("could not determine result file type from transformix log file")
            return False

        # build the image name
        file_name = os.path.join(self.outputDirPath, 'result') + '.' + file_extension

        if not os.path.exists(file_name):
            print("Can not find " + file_name)

        self.lasagna.loadImageStack(file_name)
        self.lasagna.initialiseAxes()

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # Utilities
    def absToRelPath(self, path):  # FIXME: full duplicate
        """
        Returns a relative path if path is within the current directory
        Otherwise returns the absolute path
        """
        path = str(path)  # in case it's a QString
        rel_path = path.replace(os.getcwd(), '')

        if rel_path == path:  # Can not make a relative
            return path

        if rel_path == '.':
            rel_path = './'
        else:
            rel_path = '.' + rel_path

        return rel_path
   
    def lookForStringInFile(self, fname, searchString):
        """
        Search file "fname" for any line containing the string "searchString"
        return True if such a line exists and False otherwise
        """
        with open(fname, 'r') as handle:
            for line in handle:
                if line.find(searchString) > -1:
                    return True
        return False

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # Housekeeping functions
    def checkIfReadyToRun(self):
        """
        Enables run button if we are ready to run. Also returns True or False
        """
        # Build the command
        cmd = ''
        if self.inputImagePath and os.path.exists(self.inputImagePath):
            cmd = '{} -in {}'.format(cmd, self.inputImagePath)

        if self.transformPath and os.path.exists(self.transformPath):
            cmd = '{} -tp {}'.format(cmd, self.transformPath)

        if self.outputDirPath and os.path.exists(self.outputDirPath):
            cmd = '{} -out {}'.format(cmd, self.outputDirPath)
        
        if cmd:
            self.transformixCommand = 'transformix {}'.format(cmd)
            self.commandText_label.setText(self.transformixCommand)
        else:
            self.transformixCommand = ''

        if os.path.exists(self.inputImagePath) and os.path.exists(self.transformPath) and os.path.exists(self.outputDirPath):
            self.run_pushButton.setEnabled(True)
            return True
        else:
            self.run_pushButton.setEnabled(False)
            return False

    # The following methods are involved in shutting down the plugin window
    """
    This method is called by lasagna when the user unchecks the plugin in the menu
    """
    def closePlugin(self):
        # self.detachHooks()
        self.close()

    # We define this here because we can't assume all plugins will have QWidget::closeEvent
    def closeEvent(self, event):
        """
        This event is execute when the user presses the close window (cross) button in the title bar
        """
        self.lasagna.stopPlugin(self.__module__)  # This will call self.closePlugin as well as making it possible to restart the plugin
        self.lasagna.pluginActions[self.__module__].setChecked(False)  # Uncheck the menu item associated with this plugin's name
        self.deleteLater()
        event.accept()

