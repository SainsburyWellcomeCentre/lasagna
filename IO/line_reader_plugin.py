
"""
Read line data from a text file. This reader is very similar to sparse pointer reader. 
The data format is:

lineseries_id,z_position,x_position,y_position\n
lineseries_id,z_position,x_position,y_position\n
...

No header. 

The loader creates a list of lists, where all points within each list are linked. 
All points bearing the same lineseries_id are grouped into the same list. 
"""

import os
from lasagna_plugin import lasagna_plugin
import numpy as np
from PyQt5 import QtGui
import lasagna_helperFunctions as lasHelp # Module the provides a variety of import functions (e.g. preference file handling)


class loaderClass(lasagna_plugin):
    def __init__(self,lasagna):
        super(loaderClass,self).__init__(lasagna)

        self.lasagna = lasagna
        self.objectName = 'lines_reader'
        self.kind = 'lines'

        #Construct the QActions and other stuff required to integrate the load dialog into the menu
        self.loadAction = QtGui.QAction(self.lasagna) #Instantiate the menu action

        #Add an icon to the action
        iconLoadOverlay = QtGui.QIcon()
        iconLoadOverlay.addPixmap(QtGui.QPixmap(":/actions/icons/lines_64.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.loadAction.setIcon(iconLoadOverlay)


        #Insert the action into the menu
        self.loadAction.setObjectName("linesRead")
        self.lasagna.menuLoad_ingredient.addAction(self.loadAction)
        self.loadAction.setText("Lines read")

        self.loadAction.triggered.connect(self.showLoadDialog) #Link the action to the slot



 #Slots follow
    def showLoadDialog(self,fname=None):
        """
        This slot brings up the load dialog and retrieves the file name.
        If a filename is provided then this is loaded and no dialog is brought up.
        If the file name is valid, it loads the base stack using the load method.
        """
        if fname is None or fname == False:
            fname = self.lasagna.showFileLoadDialog(fileFilter="Text Files (*.txt *.csv)")
    
        if fname is None or fname == False:
            return

        if os.path.isfile(fname): 
            with open(str(fname),'r') as fid:
                contents = fid.read()
    

            # a list of strings with each string being one line from the file
            # add nans between lineseries
            asList = contents.split('\n')

            data=[]
            lastLineSeries=None
            n=0
            expectedCols = 4 
            for ii in range(len(asList)):
                if len(asList[ii])==0:
                    continue

                thisLineAsFloats = [float(x) for x in asList[ii].split(',')]
                if not len(thisLineAsFloats)==expectedCols:
                    #Check that all rows have a length of 4, since this is what a line series needs
                    print("Lines data file %s appears corrupt" % fname)
                    return                     

                if lastLineSeries is None:
                    lastLineSeries=thisLineAsFloats[0]

                if lastLineSeries != thisLineAsFloats[0]:
                    n+=1
                    data.append([np.nan, np.nan, np.nan])

                lastLineSeries=thisLineAsFloats[0]
                data.append(thisLineAsFloats[1:])


            objName=fname.split(os.path.sep)[-1]
            self.lasagna.addIngredient(objectName=objName, 
                        kind=self.kind,
                        data=np.asarray(data), 
                        fname=fname,
                        )

            self.lasagna.returnIngredientByName(objName).addToPlots() #Add item to all three 2D plots
            self.lasagna.initialiseAxes()


        else:
            self.lasagna.statusBar.showMessage("Unable to find " + str(fname))
