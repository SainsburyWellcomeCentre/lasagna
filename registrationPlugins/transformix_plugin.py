

"""
Elastix registration plugin for Lasagna 
Rob Campbell
"""


from lasagna_plugin import lasagna_plugin
import transformix_plugin_UI
from PyQt4 import QtGui, QtCore
import sys
import os
import tempfile
from which import which #To test if binaries exist in system path
import subprocess #To run the transformix binary
import shutil 


class plugin(lasagna_plugin, QtGui.QWidget, transformix_plugin_UI.Ui_transformix_plugin): #must inherit lasagna_plugin first

    def __init__(self,lasagna,parent=None):

        super(plugin,self).__init__(lasagna) #This calls the lasagna_plugin constructor which in turn calls subsequent constructors        

        #Is the Transformix (or Elastix) binary in the system path?
        #We search for both in case we in the future add the ability to calculate inverse transforms and other good stuff
        if which('transformix') is None or which('elastix') is None:
            #TODO: does it stop properly? Will we have to uncheck and recheck the plugin menu item to get it to run a second time?
            from alert import alert
            self.alert=alert(lasagna,'The elastix or transformix binaries do not appear to be in your path.<br>Not starting plugin.')
            self.lasagna.pluginActions[self.__module__].setChecked(False) #Uncheck the menu item associated with this plugin's name
            self.deleteLater()
            return
        else:
            print "Using transformix binary at " + which('transformix')
            print "Using elastix binary at " + which('elastix')


        #re-define some default properties that were originally defined in lasagna_plugin
        self.pluginShortName='Transformix' #Appears on the menu
        self.pluginLongName='registration of images' #Can be used for other purposes (e.g. tool-tip)
        self.pluginAuthor='Rob Campbell'

        #This is the file name we monitor during running
        self.elastixLogName='elastix.log'
        self.transformixLogName='transformix.log'
        self.transformixCommand = '' #the command we will run

        #Create widgets defined in the designer file
        self.setupUi(self)
        self.show()

        #A dictionary for storing location of temporary parameter files
        #Temporary parameter files are created as the user edits them and are 
        #removed when the registration starts
        self.tmpParamFiles = {}


 

        #Create some properties which we will need
        self.inputImagePath = '' #absolute path to the image we will transform
        self.transformPath = '' #absolute path to the tranform file we will use
        self.outputDirPath = ''
  
        #Link signals to slots
        self.chooseStack_pushButton.released.connect(self.chooseStack_slot)
        self.chooseTransform_pushButton.released.connect(self.chooseTransform_slot)
        self.outputDirSelect_pushButton.released.connect(self.selectOutputDir_slot)

        self.run_pushButton.released.connect(self.run_slot)
        self.loadResult_pushButton.released.connect(self.loadResult_slot)
        
        #Disable UI elements that won't be available until the user has completed all actions
        self.run_pushButton.setEnabled(False)
        self.loadResult_pushButton.setEnabled(False)


        #Start a QTimer to poll for finished analyses
        self.finishedMonitorTimer = QtCore.QTimer()
        self.finishedMonitorTimer.timeout.connect(self.analysisFinished_slot)
        self.finishedMonitorTimer.start(2500) #Number of milliseconds between poll events



        #-------------------------------------------------------------------------------------
        #The following will either be hugely changed or deleted when the plugin is no longer
        #under heavy development
        debug=False #runs certain things quickly to help development
        if debug and os.path.expanduser("~")=='/home/rob' : #Ensure only I can trigger this. Ensures that it doesn't activate if I accidently push with debug enabled
  
            self.inputImagePath = '' #absolute path to the image we will transform
            self.transformPath = '' #absolute path to the tranform file we will use

        #-------------------------------------------------------------------------------------



    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # Slots
    def chooseStack_slot(self, fnameToChoose=False):
        """
        Choose the stack to transform
        can optionally load a specific file name (used for de-bugging)
        """

        if fnameToChoose==False:         
            fileFilter="Images (*.mhd *.mha)"
            fnameToChoose = QtGui.QFileDialog.getOpenFileName(self, 'Choose stack', lasHelp.readPreference('lastLoadDir'), fileFilter)
            fnameToChoose = str(fnameToChoose)


        if os.path.exists(fnameToChoose):
            self.inputImagePath = fnameToChoose
        else:
            #TODO: make an alert box for this case
            print "that file does not exits"
        
        #TODO: update stackName_label
        self.checkIfReadyToRun()

    def chooseTransform_slot(self, fnameToChoose=False):
        """
        Choose the transform file to use
        can optionally load a specific file name (used for de-bugging)
        """

        if fnameToChoose==False:         
            fileFilter="Images (*.txt)"
            fnameToChoose = QtGui.QFileDialog.getOpenFileName(self, 'Choose transform', lasHelp.readPreference('lastLoadDir'), fileFilter)
            fnameToChoose = str(fnameToChoose)


        if os.path.exists(fnameToChoose):
            self.inputImagePath = fnameToChoose
        else:
            #TODO: make an alert box for this case
            print "that file does not exits"

        #TODO: update transformName_label
        self.checkIfReadyToRun()




    def selectOutputDir_slot(self):
        """
        Select the Elastix output directory
        """
        selectedDir = str(QtGui.QFileDialog.getExistingDirectory(self, "Select Directory"))
        #TODO: check if directory is not empty. If it's not empty, prompt to delete contents
        self.outputDir_label.setText(selectedDir)
        self.updateWidgets_slot()

        self.checkIfReadyToRun()


    def checkIfReadyToRun(self):
        """
        Enables run button if we are ready to run. Also returns True or False
        """
        #Build the command
        self.transformixCommand =''

        if os.path.exists(self.inputImagePath) and os.path.exists(self.transformPath) and os.path.exists(self.outputDirPath):
            self.run_pushButton.setEnabled(True)
            return True
        else:
            self.run_pushButton.setEnabled(False)
            return False




   

    def updateWidgets_slot(self):
        """
        Build the elastix command and show on text boxes on screen.
        This slot is called by the radio buttons but also by other 
        slots, such moving parameters up and down.
        """

        self.elastix_cmd['f'] = self.absToRelPath(self.fixedStackPath)
        self.elastix_cmd['m'] = self.absToRelPath(self.movingStackPath)




        #Build the command
        sl
    
        #If the output directory exists, add it to the command along with any parameter files 
        #TODO: paths become absolute if we didn't call Lasagna from within the registration path. 
        #      could cd somewhere then run in order to make paths suck less
        if os.path.exists(self.outputDir_label.text()): 
            outputDir = self.absToRelPath(self.outputDir_label.text())
            cmd_str = '%s -out %s ' % (cmd_str, outputDir)

            #Build the parameter string that will be added to the command
            for ii in range(self.paramItemModel.rowCount()):
                paramFile = self.paramItemModel.index(ii,0).data().toString()
                cmd_str = "%s -p %s%s%s " % (cmd_str,outputDir,os.path.sep,paramFile)


        #Write the command to the boxes in tabs 2 and 4
        self.labelCommandText.setText(cmd_str) #On Tab 2
        self.labelCommandText_copy.setText(cmd_str) #On Tab 4

        #Refresh the parameter file list combobox on Tab 3
        self.comboBoxParam.clear()
        for ii in range(self.paramItemModel.rowCount()):
            paramFile = self.paramItemModel.index(ii,0).data().toString()
            paramFile = paramFile.split(os.path.sep)[-1] #Only the file name since we'll be saving to a different location
            self.comboBoxParam.addItem(paramFile)

        #Load the file from the first index into the text box 
        #TODO: there is no check for whether the load operation will wipe modifications to the buffer!
        if self.comboBoxParam.count()>0:
            self.comboBoxParamLoadOnSelect_slot(0)

        #Enable the run tab if all is ready
        if self.comboBoxParam.count()>0 and os.path.exists(self.outputDir_label.text()) and os.path.exists(self.elastix_cmd['m']) and os.path.exists(self.elastix_cmd['f']):
            #Can all param files in the temporary directory be found?
            for ii in range(self.paramItemModel.rowCount()):
                paramFile = str(self.paramItemModel.index(ii,0).data().toString())
                if os.path.exists(self.tmpParamFiles[paramFile])==False:
                    return #Don't proceed if we can't find the parameter file

            self.runElastix_button.setEnabled(True)
        else:
            self.runElastix_button.setEnabled(False)


  


    
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # Tab 4 - Run - slots    
    def runElastix_button_slot(self):  
        """
        Performs all of the steps needed to run Elastix:
        1. Moves (potentially modified) parameter files from the temporary dir to the output dir
        2. Runs the command. 
        3. Cleans up references to the parameter files that have now moved
        """

        #Move files
        outputDir = self.absToRelPath(self.outputDir_label.text())
        for ii in range(self.paramItemModel.rowCount()):
            paramFile = str(self.paramItemModel.index(ii,0).data().toString())
            tempLocation = self.tmpParamFiles[paramFile]
            destinationLocation = outputDir + os.path.sep + paramFile
            print "moving %s to %s" % (tempLocation,destinationLocation)
            shutil.move(tempLocation,destinationLocation)


        #Run command (non-blocking in the background)
        cmd = str(self.labelCommandText.text())
        print "Running:\n" + cmd

        #Pipe everything to /dev/null if that's an option
        if os.name == 'posix' or os.name == 'mac':
            cmd = cmd + "  > /dev/null 2>&1"
    
        subprocess.Popen(cmd, shell=True) #The command is now run
       

        #Tidy up GUI references to the now-moved parameter files
        while self.paramItemModel.rowCount()>0:
            self.removeParameter_slot(0)

        #Add directory (with absolute path) to the list of those with running analyses
        outputDirFullPath = str(self.outputDir_label.text())
        outputDirFullPath = os.path.abspath(outputDir)
        self.listofDirectoriesWithRunningAnalyses.append(outputDirFullPath)

        #Add directory to list view of running analyses
        item = QtGui.QStandardItem()
        item.setText(outputDirFullPath)
        item.setEditable(False)
        self.runningAnalysesItemModel.appendRow(item)


        #Wipe the parameter text and the output directory
        self.plainTextEditParam.setPlainText("")
        #self.outputDir_label.setText("")
        self.updateWidgets_slot()



    def analysisFinished_slot(self):
        """
        This slot is called by the self.finishedMonitorTimer QTimer.
        It updates the list of directories that contain running analyses.
        """
        if len(self.listofDirectoriesWithRunningAnalyses) ==0:
            return

        for thisDir in self.listofDirectoriesWithRunningAnalyses:
            logName = thisDir + os.path.sep + self.elastixLogName

            if self.lookForStringInFile(logName,'Total time elapsed: '):                
                print "%s is finished." % thisDir
                self.listofDirectoriesWithRunningAnalyses.remove(thisDir)
                
                #remove from list view
                for thisRow in range(self.runningAnalysesItemModel.rowCount()):
                    dirName = str(self.runningAnalysesItemModel.index(thisRow,0).data().toString())
                    if dirName == thisDir:
                        self.runningAnalysesItemModel.removeRows(thisRow,1)            
                        break

                #Look for result images
                for file in os.listdir(thisDir):
                    if file.startswith('result') and file.endswith('.mhd'):
                        resultFname = str(thisDir + os.path.sep + file)

                        #Don't add if it already exists
                        if len(self.resultsItemModel.findItems(resultFname))==0:
                            item = QtGui.QStandardItem()    
                            item.setText(resultFname)
                            item.setEditable(False)
                            self.resultsItemModel.appendRow(item)
                        else:
                            print "Result item '%s' already exists. Over-writing." % resultFname
        
                        print "Loading " + resultFname
                        self.lasagna.loadImageStack(resultFname)
                        #Get the data from this ingredient. Store it. Then wipe the ingredient
                        thisIngredient = self.lasagna.ingredientList[-1]
                        self.resultImages_Dict[resultFname] = thisIngredient.raw_data()

                        self.lasagna.removeIngredientByName(thisIngredient.objectName)


                        print "Image loading complete"

            


    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # Tab 5 - Results - slots
    def resultImageClicked_Slot(self,index):
        """
        Show the result image into the main view.
        """
        if isinstance(index,QtCore.QModelIndex)==False: #Nothing is selected
                return
        else:
            self.overlayRadioButtons_Slot(index)


    def overlayRadioButtons_Slot(self,Index=False):
        """
        Overlay selected image or original image. Index is optionally
        supplied when this slot is called from resultImageClicked_Slot
        Index is a QModelIndex
        """
        verbose=False

        movingName = self.movingStackName.text()
        moving=self.lasagna.returnIngredientByName(movingName)

        selectedIndex = self.registrationResults_ListView.selectedIndexes()
        if len(selectedIndex)==0:
            return
        else:
            selectedIndex = selectedIndex[0] #in case there are multiple selections, select the first one

        imageFname = str(selectedIndex.data().toString())


        #Show the image if the highlighted overlay radio button is enabled
        if self.showHighlightedResult_radioButton.isChecked()==True:
            if moving.fnameAbsPath == imageFname:
                if verbose:
                    print "Skipping. Unchanged."
                return

            moving.changeData(imageData=self.resultImages_Dict[imageFname], imageAbsPath=imageFname)
            if verbose:
                print "switched to overlay " + imageFname

        elif self.showOriginalMovingImage_radioButton.isChecked()==True:
            if moving.fnameAbsPath ==  self.originalMovingFname:
                if verbose:
                    print "Skipping. Unchanged."
                return

            moving.changeData(imageData=self.originalMovingImage, imageAbsPath=self.originalMovingFname)
            if verbose:
                print "switched to original overlay"

        self.lasagna.initialiseAxes()



    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    #Utilities
    def absToRelPath(self,path):
        """
        Returns a relative path if path is within the current directory
        Otherwise returns the absolute path
        """
        path = str(path) #in case it's a QString
        relPath = path.replace(os.getcwd(),'')

        if relPath == path: #Can not make a relative
            return path

        if relPath=='.':
            relPath = './'
        else:
            relPath = '.' + relPath

        return  relPath




    def lookForStringInFile(self,fname,searchString):
        """
        Search file "fname" for any line containing the string "searchString"
        return True if such a line exists and False otherwise
        """
        with open(fname, 'r') as handle:
            for line in handle:
                if line.find(searchString)>-1:
                    return True

        return False

    #The following methods are involved in shutting down the plugin window
    """
    This method is called by lasagna when the user unchecks the plugin in the menu
    """
    def closePlugin(self):
        #self.detachHooks()
        self.finishedMonitorTimer.stop()
        self.close()


    #We define this here because we can't assume all plugins will have QWidget::closeEvent
    def closeEvent(self, event):
        """
        This event is execute when the user presses the close window (cross) button in the title bar
        """
        self.lasagna.stopPlugin(self.__module__) #This will call self.closePlugin as well as making it possible to restart the plugin
        self.lasagna.pluginActions[self.__module__].setChecked(False) #Uncheck the menu item associated with this plugin's name
        self.deleteLater()
        event.accept()

