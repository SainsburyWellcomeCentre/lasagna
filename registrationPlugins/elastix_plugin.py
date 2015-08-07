

"""
Elastix registration plugin for Lasagna 
Rob Campbell
"""


from lasagna_plugin import lasagna_plugin
from IO import loadOverlayImageStack
import elastix_plugin_UI
from PyQt4 import QtGui, QtCore
import sys
import os
import tempfile
from which import which #To test if binaries exist in system path
import subprocess #To run the elastix binary
import shutil


class plugin(lasagna_plugin, QtGui.QWidget, elastix_plugin_UI.Ui_elastixMain): #must inherit lasagna_plugin first

    def __init__(self,lasagna,parent=None):

        super(plugin,self).__init__(lasagna) #This calls the lasagna_plugin constructor which in turn calls subsequent constructors        

        #Is the Elastix binary in the system path?
        if which('elastix') is None:
            #TODO: does not stop properly. Have to uncheck and recheck the plugin menu item to get it to run a second time.
            from alert import alert
            self.alert=alert(lasagna,'The elastix binary does not appear to be in your path.<br>Not starting plugin.')
            self.lasagna.pluginActions[self.__module__].setChecked(False) #Uncheck the menu item associated with this plugin's name
            self.deleteLater()
            return
        else:
            print "Using elastix binary at " + which('elastix')


        #re-define some default properties that were originally defined in lasagna_plugin
        self.pluginShortName='Elastix' #Appears on the menu
        self.pluginLongName='registration of images' #Can be used for other purposes (e.g. tool-tip)
        self.pluginAuthor='Rob Campbell'


        #Create widgets defined in the designer file
        self.setupUi(self)
        self.show()


        #The dictionary which will store the command components
        #the param files and output are separate as they are stored in the list view and ouput path text edit box
        self.elastix_cmd = {
                        'f': '',   #fixed image
                        'm' : ''   #moving image
                        }

        #A dictionary for storing location of temporary parameter files
        self.tmpParamFiles = {}

        #Create some properties which we will need
        self.refAbsPath = '' #absolute path to reference image
        self.samAbsPath = '' #absolute path to sample image

        #Set up the list view on Tab 2
        self.paramItemModel = QtGui.QStandardItemModel(self.paramListView)
        self.paramListView.setModel(self.paramItemModel)
  
        #Link signals to slots
        #Tab 1 - Loading data
        self.loadReference.released.connect(self.loadReference_slot)
        self.loadSample.released.connect(self.loadSample_slot)

        #Tab 2 - Building the registration command
        self.radioButtonReferenceFixed.toggled.connect(self.updateWidgets_slot)
        self.radioButtonSampleFixed.toggled.connect(self.updateWidgets_slot)
        self.outputDirSelect_button.released.connect(self.selectOutputDir_slot)
        self.removeParameter.released.connect(self.removeParameter_slot)
        self.loadParamFile.released.connect(self.loadParamFile_slot)
        self.moveParamUp_button.released.connect(self.moveParamUp_button_slot)
        self.moveParamDown_button.released.connect(self.moveParamDown_button_slot)

        #Tab 3 - parameter file
        self.plainTextEditParam.textChanged.connect(self.plainTextEditParam_slot)
        self.comboBoxParam.activated.connect(self.comboBoxParamLoadOnSelect_slot)

        #Tab 4: running
        self.runElastix_button.released.connect(self.runElastix_button_slot)
        self.tabRun.setEnabled(False)


        #-------------------------------------------------------------------------------------
        #The following will either be hugely changed or deleted when the plugin is no longer
        #under heavy development
        debug=True #runs certain things quickly to help development
        if debug:
         
            doRealLoad=False
            if doRealLoad:
                self.lasagna.loadBaseImageStack(self.refAbsPath)
                self.lasagna.initialiseAxes()
                self.loadSample.setEnabled(True)
                self.lasagna.loadActions[0].load(self.samAbsPath)
                self.lasagna.initialiseAxes()
            else:
                self.refAbsPath='/mnt/data/TissueCyte/registrationTests/regPipelinePrototype/YH84_150507_moving.mhd'
                self.samAbsPath='/mnt/data/TissueCyte/registrationTests/regPipelinePrototype/YH84_150507_target.mhd'


            doParamFile=True
            if doParamFile:
                #load param file list
                paramFiles = ['/mnt/data/TissueCyte/registrationTests/regPipelinePrototype/Par0000affine.txt',
                              '/mnt/data/TissueCyte/registrationTests/regPipelinePrototype/Par0000bspline.txt']
                #paramFiles = ['/mnt/data/TissueCyte/registrationTests/regPipelinePrototype/Par0000affine.txt']
                self.loadParamFile_slot(paramFiles)

            self.outputDir_label.setText(self.absToRelPath('/mnt/data/TissueCyte/registrationTests/regPipelinePrototype/reg1'))
            self.updateWidgets_slot()
            self.tabWidget.setCurrentIndex(1)

        #-------------------------------------------------------------------------------------

    #Tab 3 - Editing the parameter files
    #Parameter files are optionally edited and always saved to the registration directory.
    #The registration directory is created as needed.
    #Once all files are copied, the final tab is enabled.

    #Tab 4 - Running the registration 
    #At this point we just need to press Run! 

    #The following are slots
    def loadReference_slot(self):
        #TODO: allow only MHD files to be read
        self.lasagna.showBaseStackLoadDialog() 
        self.referenceStackName.setText(self.lasagna.returnIngredientByName('baseImage').fname())
        self.refAbsPath = self.lasagna.returnIngredientByName('baseImage').fnameAbsPath
        self.loadSample.setEnabled(True)
        self.updateWidgets_slot()
        self.sampleStackName_3.setText('')


    def loadSample_slot(self):
        #TODO: allow only MHD files to be read
        self.lasagna.loadActions[0].showLoadDialog()
        self.sampleStackName_3.setText(self.lasagna.returnIngredientByName('overlayImage').fname())
        self.samAbsPath = self.lasagna.returnIngredientByName('overlayImage').fnameAbsPath
        self.updateWidgets_slot()


    def selectOutputDir_slot(self):
        """
        Select the Elastix output directory
        """
        selectedDir = str(QtGui.QFileDialog.getExistingDirectory(self, "Select Directory"))
        #TODO: check if directory is not empty. If it's not empty, prompt to delete contents
        self.outputDir_label.setText(selectedDir)
        self.updateWidgets_slot()


    def loadParamFile_slot(self,selectedParamFiles=False):
        """
        optionally (for debugging) selectedParamFiles should be a list
        1. Bring up a load dialog so the user can select a parameter file
        2. Add parameter file to the list
        3. Create an editable copy in a tempoary location
        """
        if selectedParamFiles==False:
            selectedParamFiles = QtGui.QFileDialog.getOpenFileNames(self, "Select parameter file", "Text files (*.txt *.TXT *.ini *.INI)")

        #Add to list
        for pathToParamFile in selectedParamFiles:
            item = QtGui.QStandardItem()
            #Add to list on Tab 2
            thisParamFName = str(pathToParamFile).split(os.path.sep)[-1]
            item.setText(thisParamFName)
            self.paramItemModel.appendRow(item)

            #Copy to temporary location
            self.tmpParamFiles[thisParamFName] = tempfile.gettempdir()+os.path.sep+thisParamFName
            shutil.copyfile(pathToParamFile,self.tmpParamFiles[thisParamFName])

        self.updateWidgets_slot()


    def moveParamUp_button_slot(self):
        """
        Move currently selected parameter up by one row
        """
        currentRow = self.paramListView.currentIndex().row()
        if currentRow==0:
            return
        currentItem = self.paramItemModel.takeRow(currentRow) #Get the contents
        self.paramItemModel.removeRows(currentRow,1) #Delete the cell
        self.paramItemModel.insertRow(currentRow - 1, currentItem)
        self.updateWidgets_slot()


    def moveParamDown_button_slot(self):
        """
        Move currently selected parameter down by one row
        """
        currentRow = self.paramListView.currentIndex().row()
        if (currentRow+1) == self.paramItemModel.rowCount():
            return            
        currentItem = self.paramItemModel.takeRow(currentRow)
        self.paramItemModel.insertRow(currentRow + 1, currentItem)
        self.updateWidgets_slot()


    def removeParameter_slot(self):
        """
        Remove parameter from parameter list
        """
        currentRow = self.paramListView.currentIndex().row()
        paramFile = str(self.paramItemModel.index(currentRow,0).data().toString())

        #Remove from list view
        self.paramItemModel.removeRows(currentRow,1)
        self.updateWidgets_slot()

        #remove from dictionary
        del self.tmpParamFiles[paramFile]


    def updateWidgets_slot(self):
        """
        Build the elastix command and show on text boxes on screen.
        This slot is called by the radio buttons but also by other 
        slots, such moving parameters up and down.
        """

        if self.radioButtonReferenceFixed.isChecked():
            self.elastix_cmd['f'] = self.refAbsPath
            self.elastix_cmd['m'] = self.samAbsPath
        else:
            self.elastix_cmd['m'] = self.refAbsPath
            self.elastix_cmd['f'] = self.samAbsPath

        #Make paths relative if possible
        self.elastix_cmd['m'] = self.absToRelPath(self.elastix_cmd['m'])
        self.elastix_cmd['f'] = self.absToRelPath(self.elastix_cmd['f'])


        #Build the command
        cmd_str = 'elastix -m %s -f %s ' % (self.elastix_cmd['m'], 
                                        self.elastix_cmd['f'])

    
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
            self.tabRun.setEnabled(True)
        else:
            self.tabRun.setEnabled(False)


    def comboBoxParamLoadOnSelect_slot(self,indexToLoad):
        """
        slot that loads a parameter file from the combobox index indexToLoad
        into the text box on Tab 3
        """

        fname=self.paramItemModel.index(indexToLoad,0).data().toString()

        if os.path.exists(fname)==False:
            print fname + " does not exist"
            return

        fid = open(fname,'r')
        contents = fid.read()
        fid.close()
        self.plainTextEditParam.clear()
        self.plainTextEditParam.insertPlainText(contents)


    def plainTextEditParam_slot(self):
        """
        Temporary file is updated on every change 
        """ 
        currentFname = str(self.comboBoxParam.itemText(self.comboBoxParam.currentIndex()))
        tempFname = self.tmpParamFiles[currentFname]
        fid = open(tempFname,'w')
        fid.write(str(self.plainTextEditParam.toPlainText()))
        fid.close()

    
    def runElastix_button_slot(self):  
        cmd = str(self.labelCommandText.text())
        print "Running:\n" + cmd
        subprocess.Popen(cmd, shell=True)


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


    #The following methods are involved in shutting down the plugin window
    """
    This method is called by lasagna when the user unchecks the plugin in the menu
    """
    def closePlugin(self):
        #self.detachHooks()
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

