
"""
Read sparse points from a text file.
The text file containing the sparse points should be in the form:
z_position,x_position,y_position\n
z_position,x_position,y_position\n
...

No header. 
"""

import os
from lasagna_plugin import lasagna_plugin
import numpy as np
from PyQt4 import QtGui
import lasagna_helperFunctions as lasHelp # Module the provides a variety of import functions (e.g. preference file handling)


class loaderClass(lasagna_plugin):
    def __init__(self,lasagna):
        super(loaderClass,self).__init__(lasagna)

        self.lasagna = lasagna
        self.objectName = 'sparse_point_reader'
        self.kind = 'sparsepoints'
        #Construct the QActions and other stuff required to integrate the load dialog into the menu
        self.loadAction = QtGui.QAction(self.lasagna) #Instantiate the menu action

        #Add an icon to the action
        iconLoadOverlay = QtGui.QIcon()
        iconLoadOverlay.addPixmap(QtGui.QPixmap(":/actions/icons/points.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.loadAction.setIcon(iconLoadOverlay)


        #Insert the action into the menu
        self.loadAction.setObjectName("sparsePointRead")
        self.lasagna.menuLoad_ingredient.addAction(self.loadAction)
        self.loadAction.setText("Sparse point read")

        self.loadAction.triggered.connect(self.showLoadDialog) #Link the action to the slot



 #Slots follow
    def showLoadDialog(self,fname=None):
        """
        This slot brings up the load dialog and retrieves the file name.
        If a filename is provided then this is loaded and no dialog is brought up.
        If the file name is valid, it loads the base stack using the load method.

        """
        
        if fname == None or fname == False:
            fname = self.lasagna.showFileLoadDialog(fileFilter="Text Files (*.txt *.csv)")

        if fname == None or fname == False:
            return


        if os.path.isfile(fname): 
            with open(str(fname),'r') as fid:
                contents = fid.read()
    

            # a list of strings with each string being one line from the file
            asList = contents.split('\n')
            data=[]
            for ii in range(len(asList)):
                if len(asList[ii])==0:
                    continue
                data.append([float(x) for x in asList[ii].split(',')])


            objName=fname.split(os.path.sep)[-1]
            self.lasagna.addIngredient(objectName=objName, 
                        kind=self.kind, 
                        data=np.asarray(data), 
                        fname=fname
                        )

            self.lasagna.returnIngredientByName(objName).addToPlots() #Add item to all three 2D plots
            self.lasagna.initialiseAxes()

        else:
            self.lasagna.statusBar.showMessage("Unable to find " + str(fname))
