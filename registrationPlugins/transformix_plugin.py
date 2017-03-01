

"""
Transformix plugin for Lasagna 
Rob Campbell
"""


from lasagna_plugin import lasagna_plugin
import transformix_plugin_UI
from PyQt5 import QtGui, QtCore
import sys
import os
import tempfile
from which import which #To test if binaries exist in system path
import subprocess #To run the transformix binary
import shutil 
import re
import lasagna_helperFunctions as lasHelp
import time

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
            print("Using transformix binary at " + which('transformix'))
            print("Using elastix binary at " + which('elastix'))


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
        self.transformixCommand = ''


        #Link signals to slots
        self.chooseStack_pushButton.released.connect(self.chooseStack_slot)
        self.chooseTransform_pushButton.released.connect(self.chooseTransform_slot)
        self.outputDirSelect_pushButton.released.connect(self.selectOutputDir_slot)

        self.run_pushButton.released.connect(self.run_slot)
        self.loadResult_pushButton.released.connect(self.loadResult_slot)
        

        #Disable UI elements that won't be available until the user has completed all actions
        self.run_pushButton.setEnabled(False)
        self.loadResult_pushButton.setEnabled(False)

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
            self.inputImagePath = ''
            #TODO: make an alert box for this case
            print("that file does not exits")
        
        self.checkIfReadyToRun()
        lasHelp.preferenceWriter('lastLoadDir', lasHelp.stripTrailingFileFromPath(fnameToChoose))
        self.stackName_label.setText(fnameToChoose.split(os.path.sep)[-1])

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
            self.transformPath = fnameToChoose
        else:
            self.transformPath = ''
            #TODO: make an alert box for this case
            print("that file does not exits")


        self.checkIfReadyToRun()
        lasHelp.preferenceWriter('lastLoadDir', lasHelp.stripTrailingFileFromPath(fnameToChoose))
        self.transformName_label.setText(fnameToChoose.split(os.path.sep)[-1])


    def selectOutputDir_slot(self):
        """
        Select the Transformix output directory via a QFileDialog
        """
        selectedDir = str(QtGui.QFileDialog.getExistingDirectory(self, "Select Directory"))
        #TODO: check if directory is not empty. If it's not empty, prompt to delete contents
        self.outputDir_label.setText(selectedDir)
        
        if os.path.exists(selectedDir):
            self.outputDirPath = selectedDir
        else:
            self.outputDirPath = ''

        self.checkIfReadyToRun()


    def run_slot(self):  
        """
        Run the transformix session
        """

        if len (self.transformixCommand)==0:
            print("transformix command is empty")
            return False

        #Run command (non-blocking in the background)
        cmd = self.transformixCommand
        print("Running:\n" + cmd)

        #Pipe everything to /dev/null if that's an option
        if os.name == 'posix' or os.name == 'mac':
            cmd = cmd + "  > /dev/null 2>&1"
    
        #If the log file exists already, delete it
        pathToLog = os.path.join(self.outputDirPath,self.transformixLogName)
        if os.path.exists(pathToLog):
            os.remove(pathToLog)




        #Deactivate the UI elements whilst we're running
        self.labelCommand.setText('RUNNING...')
        self.run_pushButton.setEnabled(False)
        self.loadResult_pushButton.setEnabled(False)
        self.chooseStack_pushButton.setEnabled(False)
        self.chooseTransform_pushButton.setEnabled(False)
        self.outputDirSelect_pushButton.setEnabled(False)
        QtCore.QCoreApplication.processEvents() #TODO: does not work

        #Watch for completion
        running = True
        time.sleep(0.1)
        subprocess.Popen(cmd, shell=True) #The command is now run
        success=False
        while running:

            if not os.path.exists(pathToLog): #wait for the file to appear
                time.sleep(0.15)
                continue

            if self.lookForStringInFile(pathToLog, 'Errors occurred'):
                print("FAILED")
                running = False

            if self.lookForStringInFile(pathToLog, 'Elapsed time'):
                print("FINISHED!")
                success=True
                running = False


        #Return to the original state so we can start another round
        self.labelCommand.setText('Command...')

        self.chooseStack_pushButton.setEnabled(True)
        self.chooseTransform_pushButton.setEnabled(True)
        self.outputDirSelect_pushButton.setEnabled(True)

        self.stackName_label.setText('')
        self.transformName_label.setText('') 
        self.outputDir_label.setText('')

        if success: #Display result if it is available
            self.loadResult_pushButton.setEnabled(True)
            self.commandText_label.setText('Transform sucessful ')
        else:
            self.commandText_label.setText('Transform FAILED! See %s for details ' % pathToLog)





    def loadResult_slot(self):
        """
        Show the result image in the main view.
        """
        #Find the result image format
        pathToLog = os.path.join(self.outputDirPath,self.transformixLogName)
        if not os.path.exists(pathToLog):
            print("Can not find " + pathToLog)
            return False

        fileExtension = ''
        with open(pathToLog, 'r') as fid:
            for line in fid:
                M = re.match('\(ResultImageFormat "(\w+)"',line)
                if M is not None:
                    g = M.groups()
                    if len(g)>0:
                        fileExtension = g[0]

        if len(fileExtension)==0:
            print("could not determine result file type from transformix log file")
            return False

        #build the image name
        fileName = os.path.join(self.outputDirPath,'result') + '.' + fileExtension

        if not os.path.exists(fileName):
            print("Can not find " + fileName)

        self.lasagna.loadImageStack(fileName)
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


    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # Housekeeping functions
    def checkIfReadyToRun(self):
        """
        Enables run button if we are ready to run. Also returns True or False
        """
        #Build the command
        cmd = ''
        if len(self.inputImagePath)>0 and os.path.exists(self.inputImagePath):
            cmd = '%s -in %s' % (cmd,self.inputImagePath)

        if len(self.transformPath)>0 and os.path.exists(self.transformPath):
            cmd = '%s -tp %s' % (cmd,self.transformPath)

        if len(self.outputDirPath)>0 and os.path.exists(self.outputDirPath):
            cmd = '%s -out %s' % (cmd,self.outputDirPath)
        
        if len(cmd)>0:
            self.transformixCommand = 'transformix ' + cmd
            self.commandText_label.setText(self.transformixCommand)
        else:
            self.transformixCommand = ''


        if os.path.exists(self.inputImagePath) and os.path.exists(self.transformPath) and os.path.exists(self.outputDirPath):
            self.run_pushButton.setEnabled(True)
            return True
        else:
            self.run_pushButton.setEnabled(False)
            return False


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

