
"""
Read line data from a text file. This reader is versy similar to sparse pointer reader. 
The principle difference is that points are not linked the text files we read are 
simply a list of z,x, and y positions. On the other hand, we may want to numerous 
non-linked lines (e.g. as part of a tree structure) all under the same ingredient. 
This loader class handles this case. The data format is:

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
from PyQt4 import QtGui
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
        
        if fname==None:
            fname = self.lasagna.showFileLoadDialog(fileFilter="Text Files (*.txt *.csv)")
    
        if fname == None:
            return


        if os.path.isfile(fname): 
            fid = open(str(fname),'r')
            contents = fid.read()
            fid.close()


            # a list of strings with each string being one line from the file
            # add nans between lineseries
            asList = contents.split('\n')
            data=[]
            lastLineSeries=None
            n=0
            for ii in range(len(asList)):
                if len(asList[ii])==0:
                    continue

                thisLineAsFloats = [float(x) for x in asList[ii].split(',')]
                if lastLineSeries==None:
                    lastLineSeries=thisLineAsFloats[0]

                if lastLineSeries != thisLineAsFloats[0]:
                    n+=1
                    data.append([np.nan, np.nan, np.nan])

                lastLineSeries=thisLineAsFloats[0]
                data.append(thisLineAsFloats[1:])

            print "Added %d nan rows" % n
            #TEMPORARY HACK
            data = np.asarray(data)
            data[:,0] = data[:,0]/5
            data[:,1:] = data[:,1:]/20.8
            #TEMPORAY HACK




            objName=fname.split(os.path.sep)[-1]
            self.lasagna.addIngredient(objectName=objName, 
                        kind=self.kind,
                        data=data, 
                        fname=fname
                        )

            self.lasagna.returnIngredientByName(objName).addToPlots() #Add item to all three 2D plots
            self.lasagna.initialiseAxes()


        else:
            self.lasagna.statusBar.showMessage("Unable to find " + str(fname))
