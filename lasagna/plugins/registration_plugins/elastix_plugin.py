

"""
Elastix registration plugin for Lasagna 
Rob Campbell
"""

import os
import shutil
import subprocess  # To run the elastix binary
import tempfile

from PyQt5 import QtGui, QtCore

from lasagna.plugins.lasagna_plugin import lasagna_plugin
from lasagna.plugins.registration_plugins import elastix_plugin_UI
from lasagna.plugins.registration_plugins import which  # To test if binaries exist in system path


class plugin(lasagna_plugin, QtGui.QWidget, elastix_plugin_UI.Ui_elastixMain):  # must inherit lasagna_plugin first

    def __init__(self, lasagna_serving, parent=None):

        super(plugin, self).__init__(lasagna_serving)  # This calls the lasagna_plugin constructor which in turn calls subsequent constructors

        # Is the Elastix binary in the system path?
        if which('elastix') is None:
            # TODO: does not stop properly. Have to uncheck and recheck the plugin menu item to get it to run a second time.
            from lasagna.alert import alert
            self.alert = alert(lasagna_serving,
                               'The elastix binary does not appear to be in your path.<br>Not starting plugin.')
            self.lasagna.pluginActions[self.__module__].setChecked(False)  # Uncheck the menu item associated with this plugin's name
            self.deleteLater()
            return
        else:
            print("Using elastix binary at " + which('elastix'))

        # re-define some default properties that were originally defined in lasagna_plugin
        self.pluginShortName = 'Elastix'  # Appears on the menu
        self.pluginLongName = 'registration of images'  # Can be used for other purposes (e.g. tool-tip)
        self.pluginAuthor = 'Rob Campbell'

        # This is the file name we monitor during running
        self.elastixLogName = 'elastix.log'

        # Create widgets defined in the designer file
        self.setupUi(self)
        self.show()

        # The dictionary which will store the command components
        # the param files and output are separate as they are stored in the list view and ouput path text edit box
        self.elastix_cmd = {
            'f': '',   # fixed image
            'm': ''    # moving image
        }

        # A dictionary for storing location of temporary parameter files
        # Temporary parameter files are created as the user edits them and are
        # removed when the registration starts
        self.tmpParamFiles = {}

        # Create some properties which we will need
        self.fixedStackPath = ''  # absolute path to reference image
        self.movingStackPath = ''  # absolute path to sample image

        # Set up the list view on Tab 2
        self.paramItemModel = QtGui.QStandardItemModel(self.paramListView)
        self.paramListView.setModel(self.paramItemModel)
  
        # Link signals to slots
        # Tab 1 - Loading data
        self.loadFixed.released.connect(self.loadFixed_slot)
        self.loadMoving.released.connect(self.loadMoving_slot)
        self.originalMovingImage = None  # The original moving image is stored here
        self.originalMovingFname = None 

        # Flip axis
        self.flipAxis1.released.connect(lambda: self.flipAxis_Slot(0))
        self.flipAxis2.released.connect(lambda: self.flipAxis_Slot(1))
        self.flipAxis3.released.connect(lambda: self.flipAxis_Slot(2))

        # Rotate axis
        self.rotAxis1.released.connect(lambda: self.rotAxis_Slot(0))
        self.rotAxis2.released.connect(lambda: self.rotAxis_Slot(1))
        self.rotAxis3.released.connect(lambda: self.rotAxis_Slot(2))

        # Swap axes
        self.swapAxis1_2.released.connect(lambda: self.swapAxis_Slot(0,1))
        self.swapAxis2_3.released.connect(lambda: self.swapAxis_Slot(1,2))
        self.swapAxis3_1.released.connect(lambda: self.swapAxis_Slot(2,0))

        self.saveModifiedMovingStack.released.connect(self.saveModifiedMovingStack_slot)

        # Tab 2 - Building the registration command
        self.outputDirSelect_button.released.connect(self.selectOutputDir_slot)
        self.removeParameter.released.connect(self.removeParameter_slot)
        self.loadParamFile.released.connect(self.loadParamFile_slot)
        self.moveParamUp_button.released.connect(self.moveParamUp_button_slot)
        self.moveParamDown_button.released.connect(self.moveParamDown_button_slot)

        # Tab 3 - parameter file
        self.plainTextEditParam.textChanged.connect(self.plainTextEditParam_slot)
        self.comboBoxParam.activated.connect(self.comboBoxParamLoadOnSelect_slot)

        # Tab 4: running
        self.runElastix_button.released.connect(self.runElastix_button_slot)
        self.runElastix_button.setEnabled(False)
        # Start a QTimer to poll for finished analyses
        self.finishedMonitorTimer = QtCore.QTimer()
        self.finishedMonitorTimer.timeout.connect(self.analysisFinished_slot)
        self.finishedMonitorTimer.start(2500)  # Number of milliseconds between poll events
        self.listofDirectoriesWithRunningAnalyses = [] 
        # Set up list view on the running tab
        self.runningAnalysesItemModel = QtGui.QStandardItemModel(self.runningRegistrations_ListView)
        self.runningRegistrations_ListView.setModel(self.runningAnalysesItemModel)

        # Tab 5: results
        self.resultsItemModel = QtGui.QStandardItemModel(self.registrationResults_ListView)
        self.registrationResults_ListView.setModel(self.resultsItemModel)
        self.registrationResults_ListView.clicked.connect(self.resultImageClicked_Slot)
        self.resultImages_Dict = {}  # the keys are result image file names and the values are the result images
        self.showHighlightedResult_radioButton.toggled.connect(self.overlayRadioButtons_Slot)
        self.showOriginalMovingImage_radioButton.toggled.connect(self.overlayRadioButtons_Slot)

        # Clear all image stacks
        self.lasagna.removeIngredientByType('imagestack')

        # -------------------------------------------------------------------------------------
        # The following will either be hugely changed or deleted when the plugin is no longer
        # under heavy development
        debug = False  # runs certain things quickly to help development
        if debug and os.path.expanduser("~") == '/home/rob': #Ensure only I can trigger this. Ensures that it doesn't activate if I accidently push with debug enabled
            self.fixedStackPath = '/mnt/data/TissueCyte/registrationTests/regPipelinePrototype/YH84_150507_target.mhd'
            self.movingStackPath = '/mnt/data/TissueCyte/registrationTests/regPipelinePrototype/YH84_150507_moving.mhd'
            do_real_load = True
            if do_real_load:
                self.loadFixed_slot(self.fixedStackPath)                
                self.loadMoving_slot(self.movingStackPath)
                self.lasagna.initialiseAxes()
            do_param_file = True
            if do_param_file:
                # load param file list
                param_files = ['/mnt/data/TissueCyte/registrationTests/regPipelinePrototype/Par0000affine.txt',
                               '/mnt/data/TissueCyte/registrationTests/regPipelinePrototype/Par0000bspline.txt']
                param_files = ['/mnt/data/TissueCyte/registrationTests/regPipelinePrototype/Par0000affine_quick.txt']
                self.loadParamFile_slot(param_files)

            self.outputDir_label.setText(self.absToRelPath('/mnt/data/TissueCyte/registrationTests/regPipelinePrototype/reg2'))
            self.updateWidgets_slot()
            self.tabWidget.setCurrentIndex(3)
        # -------------------------------------------------------------------------------------

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # Tab 1 - Loading -  slots
    def loadFixed_slot(self, fnameToLoad=False):
        """
        Clear all stacks and load a fixed image
        can optionally load a specific file name (used for de-bugging)
        """
        self.lasagna.removeIngredientByType('imagestack')
        if not fnameToLoad:
            self.lasagna.showStackLoadDialog(fileFilter="MHD Images (*.mhd *.mha)") 
        else:
            self.lasagna.loadImageStack(fnameToLoad)

        fixed_name = self.lasagna.stacksInTreeList()[0]
        self.referenceStackName.setText(fixed_name)
        self.fixedStackPath = self.lasagna.returnIngredientByName(fixed_name).fnameAbsPath

        # Enable UI buttons
        self.loadMoving.setEnabled(True)        
        
        self.updateWidgets_slot()
        self.movingStackName.setText('')
        self.elastix_cmd['f'] = self.absToRelPath(self.fixedStackPath)

    def loadMoving_slot(self, fnameToLoad=False):
        """
        Load the moving stack can optionally load a specific file name (used for de-bugging)
        """
        # If there is already a moving stack loaded we should wipe it
        current_moving_stack = str(self.movingStackName.text())
        if current_moving_stack:
            self.lasagna.removeIngredientByName(current_moving_stack)

        if not fnameToLoad:
            self.lasagna.showStackLoadDialog(fileFilter="MHD Images (*.mhd *mha )") 
        else:
            self.lasagna.loadImageStack(fnameToLoad)

        moving_name = self.lasagna.stacksInTreeList()[1]
        self.movingStackName.setText(moving_name)
        self.movingStackPath = self.lasagna.returnIngredientByName(moving_name).fnameAbsPath

        self.updateWidgets_slot()
        moving_name = self.lasagna.stacksInTreeList()[1]
        moving = self.lasagna.returnIngredientByName(moving_name)
        self.originalMovingImage = moving.raw_data()
        self.originalMovingFname = moving.fnameAbsPath
        self.elastix_cmd['m'] = self.absToRelPath(self.movingStackPath)

        # Enable UI elements for modifying moving stack orientation
        self.flipAxis1.setEnabled(True)
        self.flipAxis2.setEnabled(True)
        self.flipAxis3.setEnabled(True)     
        self.rotAxis1.setEnabled(True)
        self.rotAxis2.setEnabled(True)
        self.rotAxis3.setEnabled(True)
        self.swapAxis1_2.setEnabled(True)
        self.swapAxis2_3.setEnabled(True)
        self.swapAxis3_1.setEnabled(True)

    def flipAxis_Slot(self, axisToFlip):
        """
        Flips the moving stack along the defined axis
        """
        print("Flipping axis %d of moving stack" % (axisToFlip+1))
        moving_name = self.movingStackName.text()
        if not self.lasagna.returnIngredientByName(moving_name):
            print("Failed to flip moving image")
            return

        self.lasagna.returnIngredientByName(moving_name).flipAlongAxis(axisToFlip)
        self.lasagna.initialiseAxes()
        self.saveModifiedMovingStack.setEnabled(True)

    def rotAxis_Slot(self, axisToRotate):
        """
        Rotates the moving stack along the defined axis
        """
        print("Rotating axis %d of moving stack" % (axisToRotate+1))
        moving_name = self.movingStackName.text()
        if not self.lasagna.returnIngredientByName(moving_name):
            print("Failed to rotate moving image")
            return

        self.lasagna.returnIngredientByName(moving_name).rotateAlongDimension(axisToRotate)
        self.lasagna.initialiseAxes()
        self.saveModifiedMovingStack.setEnabled(True)

    def swapAxis_Slot(self, ax1, ax2):
        """
        Swaps the moving stack axes along the defined dimensions
        """
        print("Swapping moving stack axes %d and %d" % (ax1+1, ax2+1))
        moving_name = self.movingStackName.text()
        if not self.lasagna.returnIngredientByName(moving_name):
            print("Failed to swap moving image axes")
            return

        self.lasagna.returnIngredientByName(moving_name).swapAxes(ax1, ax2)
        self.lasagna.initialiseAxes()
        self.saveModifiedMovingStack.setEnabled(True)

    def saveModifiedMovingStack_slot(self):
        """
        Save modified stack.
        Following code only works if the image dimensions have not changed.
        So ok for flipping.
        """
        from lasagna.io_libs import image_stack_loader

        moving_name = self.movingStackName.text()
        im_stack = self.lasagna.returnIngredientByName(moving_name).raw_data()
        
        print("Saving...")

        orig_button_text = self.saveModifiedMovingStack.text()
        self.saveModifiedMovingStack.setText('SAVING') #TODO: bug - this text does not appear

        return_val = image_stack_loader.mhdWrite(im_stack, self.originalMovingFname)
        
        if return_val:
            self.saveModifiedMovingStack.setEnabled(False)
            print("Saved")
        else:
            print("Save failed")
        
        self.saveModifiedMovingStack.setText(orig_button_text)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # Tab 2 - Command build - slots
    def selectOutputDir_slot(self):
        """
        Select the Elastix output directory
        """
        selected_dir = str(QtGui.QFileDialog.getExistingDirectory(self, "Select Directory"))
        # TODO: check if directory is not empty. If it's not empty, prompt to delete contents
        self.outputDir_label.setText(selected_dir)
        self.updateWidgets_slot()

    def loadParamFile_slot(self, selectedParamFiles=False):
        """
        optionally (for debugging) selectedParamFiles should be a list
        1. Bring up a load dialog so the user can select a parameter file
        2. Add parameter file to the list
        3. Create an editable copy in a tempoary location
        """
        if not selectedParamFiles:
            selectedParamFiles = QtGui.QFileDialog.getOpenFileNames(self, "Select parameter file", "Text files (*.txt *.TXT *.ini *.INI)")

        # Add to list
        for path_to_param_file in selectedParamFiles:
            item = QtGui.QStandardItem()
            # Add to list on Tab 2
            param_file_name = str(path_to_param_file).split(os.path.sep)[-1]
            item.setText(param_file_name)
            item.setEditable(False)
            self.paramItemModel.appendRow(item)

            # Copy to temporary location
            self.tmpParamFiles[param_file_name] = tempfile.gettempdir()+os.path.sep+param_file_name
            shutil.copyfile(path_to_param_file, self.tmpParamFiles[param_file_name])

        self.updateWidgets_slot()

    def moveParamUp_button_slot(self):
        """
        Move currently selected parameter up by one row
        """
        current_row = self.paramListView.currentIndex().row()
        if current_row == 0:
            return
        current_item = self.paramItemModel.takeRow(current_row)  # Get the contents
        self.paramItemModel.removeRows(current_row, 1)  # Delete the cell
        self.paramItemModel.insertRow(current_row - 1, current_item)
        self.updateWidgets_slot()

    def moveParamDown_button_slot(self):
        """
        Move currently selected parameter down by one row
        """
        current_row = self.paramListView.currentIndex().row()
        if (current_row+1) == self.paramItemModel.rowCount():
            return            
        current_item = self.paramItemModel.takeRow(current_row)
        self.paramItemModel.insertRow(current_row + 1, current_item)
        self.updateWidgets_slot()

    def removeParameter_slot(self, currentRow=None):
        """
        Remove parameter from parameter list
        """
        if currentRow is None:
            currentRow = self.paramListView.currentIndex().row()

        if currentRow < 0:
            print("Can not remove row %d" % currentRow)

        param_file = str(self.paramItemModel.index(currentRow, 0).data())

        # Remove from list view
        self.paramItemModel.removeRows(currentRow, 1)

        # remove from dictionary
        print("removing {}".format(param_file))
        del self.tmpParamFiles[param_file]

        self.updateWidgets_slot()

    def updateWidgets_slot(self):
        """
        Build the elastix command and show on text boxes on screen.
        This slot is called by the radio buttons but also by other 
        slots, such moving parameters up and down.
        """

        self.elastix_cmd['f'] = self.absToRelPath(self.fixedStackPath)
        self.elastix_cmd['m'] = self.absToRelPath(self.movingStackPath)

        # Build the command
        cmd_str = 'elastix -m {} -f {} '.format(self.elastix_cmd['m'], self.elastix_cmd['f'])

        # If the output directory exists, add it to the command along with any parameter files
        # TODO: paths become absolute if we didn't call Lasagna from within the registration path.
        #      could cd somewhere then run in order to make paths suck less
        if os.path.exists(self.outputDir_label.text()): 
            output_dir = self.absToRelPath(self.outputDir_label.text())
            cmd_str = '%s -out %s ' % (cmd_str, output_dir)

            # Build the parameter string that will be added to the command
            for i in range(self.paramItemModel.rowCount()):
                param_file = self.paramItemModel.index(i, 0).data()
                cmd_str = "%s -p %s%s%s " % (cmd_str, output_dir, os.path.sep, param_file)

        # Write the command to the boxes in tabs 2 and 4
        self.labelCommandText.setText(cmd_str)  # On Tab 2
        self.labelCommandText_copy.setText(cmd_str)  # On Tab 4

        # Refresh the parameter file list combobox on Tab 3
        self.comboBoxParam.clear()
        for i in range(self.paramItemModel.rowCount()):
            param_file = self.paramItemModel.index(i, 0).data()
            param_file = param_file.split(os.path.sep)[-1]  # Only the file name since we'll be saving to a different location
            self.comboBoxParam.addItem(param_file)

        # Load the file from the first index into the text box
        # TODO: there is no check for whether the load operation will wipe modifications to the buffer!
        if self.comboBoxParam.count() > 0:
            self.comboBoxParamLoadOnSelect_slot(0)

        # Enable the run tab if all is ready
        if self.comboBoxParam.count() > 0 and os.path.exists(self.outputDir_label.text()) and os.path.exists(self.elastix_cmd['m']) and os.path.exists(self.elastix_cmd['f']):
            # Can all param files in the temporary directory be found?
            for i in range(self.paramItemModel.rowCount()):
                param_file = str(self.paramItemModel.index(i, 0).data())
                if not os.path.exists(self.tmpParamFiles[param_file]):
                    return  # Don't proceed if we can't find the parameter file

            self.runElastix_button.setEnabled(True)
        else:
            self.runElastix_button.setEnabled(False)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # Tab 3 - Param edit - slots
    def comboBoxParamLoadOnSelect_slot(self, indexToLoad):
        """
        slot that loads a parameter file from the combobox index indexToLoad
        into the text box on Tab 3
        """

        selected_fname = str(self.paramItemModel.index(indexToLoad, 0).data())
        fname = self.tmpParamFiles[selected_fname]

        if not os.path.exists(fname):
            print(fname + " does not exist")
            return

        with open(fname, 'r') as fid:
            contents = fid.read()
    
        self.plainTextEditParam.clear()
        self.plainTextEditParam.insertPlainText(contents)

    def plainTextEditParam_slot(self):
        """
        Temporary file is updated on every change 
        """ 
        current_fname = str(self.comboBoxParam.itemText(self.comboBoxParam.currentIndex()))
        if not current_fname:
            return

        if current_fname not in self.tmpParamFiles:
            print("plainTextEditParam_slot no key {}".format(current_fname))
            return

        fname = self.tmpParamFiles[current_fname]
        if not os.path.exists(fname):
            print("Failed to find temporary file at {}".format(fname))
            return

        with open(fname, 'w') as fid:
            fid.write(str(self.plainTextEditParam.toPlainText()))
    
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # Tab 4 - Run - slots    
    def runElastix_button_slot(self):  
        """
        Performs all of the steps needed to run Elastix:
        1. Moves (potentially modified) parameter files from the temporary dir to the output dir
        2. Runs the command. 
        3. Cleans up references to the parameter files that have now moved
        """
        # Move files
        output_dir = self.absToRelPath(self.outputDir_label.text())
        for i in range(self.paramItemModel.rowCount()):
            param_file = str(self.paramItemModel.index(i, 0).data())
            temp_location = self.tmpParamFiles[param_file]
            destination_location = output_dir + os.path.sep + param_file
            print("moving {} to {}".format(temp_location, destination_location))
            shutil.move(temp_location, destination_location)

        # Run command (non-blocking in the background)
        cmd = str(self.labelCommandText.text())
        print("Running:\n{}".format(cmd))

        # Pipe everything to /dev/null if that's an option
        if os.name == 'posix' or os.name == 'mac':
            cmd = cmd + "  > /dev/null 2>&1"
    
        subprocess.Popen(cmd, shell=True)  # The command is now run

        # Tidy up GUI references to the now-moved parameter files
        while self.paramItemModel.rowCount() > 0:
            self.removeParameter_slot(0)

        # Add directory (with absolute path) to the list of those with running analyses
        output_dir_full_path = str(self.outputDir_label.text())  # FIXME: unused
        output_dir_full_path = os.path.abspath(output_dir)
        self.listofDirectoriesWithRunningAnalyses.append(output_dir_full_path)

        # Add directory to list view of running analyses
        item = QtGui.QStandardItem()
        item.setText(output_dir_full_path)
        item.setEditable(False)
        self.runningAnalysesItemModel.appendRow(item)

        # Wipe the parameter text and the output directory
        self.plainTextEditParam.setPlainText("")
        # self.outputDir_label.setText("")
        self.updateWidgets_slot()

    def analysisFinished_slot(self):
        """
        This slot is called by the self.finishedMonitorTimer QTimer.
        It updates the list of directories that contain running analyses.
        """
        if not self.listofDirectoriesWithRunningAnalyses:
            return

        for analysis_folder in self.listofDirectoriesWithRunningAnalyses:
            log_name = analysis_folder + os.path.sep + self.elastixLogName

            if self.lookForStringInFile(log_name, 'Total time elapsed: '):
                print("%s is finished." % analysis_folder)
                self.listofDirectoriesWithRunningAnalyses.remove(analysis_folder)
                
                # remove from list view
                for row in range(self.runningAnalysesItemModel.rowCount()):
                    dir_name = str(self.runningAnalysesItemModel.index(row, 0).data())
                    if dir_name == analysis_folder:
                        self.runningAnalysesItemModel.removeRows(row, 1)
                        break

                # Look for result images
                for file in os.listdir(analysis_folder):
                    if file.startswith('result') and file.endswith('.mhd'):  # TODO: will fail if user asks for something that is not an MHD file
                        result_fname = str(analysis_folder + os.path.sep + file)

                        # Don't add if it already exists
                        if not self.resultsItemModel.findItems(result_fname):
                            item = QtGui.QStandardItem()    
                            item.setText(result_fname)
                            item.setEditable(False)
                            self.resultsItemModel.appendRow(item)
                        else:
                            print("Result item '%s' already exists. Over-writing." % result_fname)

                        print("Loading " + result_fname)
                        self.lasagna.loadImageStack(result_fname)
                        # Get the data from this ingredient. Store it. Then wipe the ingredient
                        ingredient = self.lasagna.ingredientList[-1]
                        self.resultImages_Dict[result_fname] = ingredient.raw_data()

                        self.lasagna.removeIngredientByName(ingredient.objectName)

                        print("Image loading complete")

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # Tab 5 - Results - slots
    def resultImageClicked_Slot(self, index):
        """
        Show the result image into the main view.
        """
        if not isinstance(index, QtCore.QModelIndex):  # Nothing is selected
                return
        else:
            self.overlayRadioButtons_Slot(index)

    def overlayRadioButtons_Slot(self, Index=False):
        """
        Overlay selected image or original image. Index is optionally
        supplied when this slot is called from resultImageClicked_Slot
        Index is a QModelIndex
        """
        verbose = False

        moving_name = self.movingStackName.text()
        moving = self.lasagna.returnIngredientByName(moving_name)

        selected_indexes = self.registrationResults_ListView.selectedIndexes()
        if not selected_indexes:
            return
        else:
            selected_index = selected_indexes[0]  # in case there are multiple selections, select the first one

        image_fname = str(selected_index.data())

        # Show the image if the highlighted overlay radio button is enabled
        if self.showHighlightedResult_radioButton.isChecked():
            if moving.fnameAbsPath == image_fname:
                if verbose:
                    print("Skipping. Unchanged.")
                return

            moving.changeData(imageData=self.resultImages_Dict[image_fname], imageAbsPath=image_fname)
            if verbose:
                print("switched to overlay " + image_fname)
        elif self.showOriginalMovingImage_radioButton.isChecked():
            if moving.fnameAbsPath == self.originalMovingFname:
                if verbose:
                    print("Skipping. Unchanged.")
                return

            moving.changeData(imageData=self.originalMovingImage, imageAbsPath=self.originalMovingFname)
            if verbose:
                print("switched to original overlay")

        self.lasagna.initialiseAxes()

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # Utilities
    def absToRelPath(self, path):
        """
        Returns a relative path if path is within the current directory
        Otherwise returns the absolute path
        """
        path = str(path)  # in case it's a QString
        rel_path = path.replace(os.getcwd(), '')  # FIXME: see if can use os.relpath

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

    # The following methods are involved in shutting down the plugin window
    """
    This method is called by lasagna when the user unchecks the plugin in the menu
    """
    def closePlugin(self):
        # self.detachHooks()
        self.finishedMonitorTimer.stop()
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
