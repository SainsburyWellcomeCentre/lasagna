
"""
Read sparse points from a text file.

The sparse points file makes it possible to load individual point data into the 3D space defined 
the volume image. 

The sparse points file may have one of two formats.
In both cases it's one row per data point. 
There is no header that contains information on what the columns are.

ONE:
z_position,x_position,y_position\n
z_position,x_position,y_position\n
...


TWO
z_position,x_position,y_position,data_series_number\n
z_position,x_position,y_position,data_series_number\n
...


In the second format, each data point is associated with a scalar value.
All points with the same scalar value are grouped together as one ingredient. 
This allows points of different sorts to be overlaid easily on the same 
image and have their properties changed together. 


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
        
        if fname is None or fname == False:
            fname = self.lasagna.showFileLoadDialog(fileFilter="Text Files (*.txt *.csv)")

        if fname is None or fname == False:
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

            # A point series should be a list of lists where each list has a length of 3,
            # corresponding to the position of each point in 3D space. However, point
            # series could also have a length of 4. If this is the case, the fourth 
            # value is the index of the series. This allows a single file to hold multiple
            # different point series. We handle these two cases differently. First we deal
            # with the the standard case:
            if len(data[1]) == 3:
                # Create an ingredient with the same name as the file name 
                objName=fname.split(os.path.sep)[-1]
                self.lasagna.addIngredient(objectName=objName, 
                            kind=self.kind, 
                            data=np.asarray(data), 
                            fname=fname
                            )

                # Add this ingredient to all three plots
                self.lasagna.returnIngredientByName(objName).addToPlots() 

                # Update the plots
                self.lasagna.initialiseAxes()

            elif len(data[1]) == 4:
                # What are the unique data series values?
                dSeries = [x[3] for x in data]
                dSeries = list(set(dSeries))
                
                # Loop through these unique series and add as separate sparse point objects

                for thisIndex in dSeries:
                    tmp = []
                    for thisRow in data:
                        if thisRow[3]==thisIndex:
                            tmp.append(thisRow[:3])

                    print("Adding point series %d with %d points" % (thisIndex,len(tmp)))

                    # Create an ingredient with the same name as the file name 
                    objName = "%s #%d" % (fname.split(os.path.sep)[-1],thisIndex)

                    self.lasagna.addIngredient(objectName=objName, 
                                kind=self.kind, 
                                data=np.asarray(tmp), 
                                fname=fname
                                )

                    # Add this ingredient to all three plots
                    self.lasagna.returnIngredientByName(objName).addToPlots() 

                    # Update the plots
                    self.lasagna.initialiseAxes()


            else:
                print(("Point series has %d columns. Only 3 or 4 columns are supported" % len(data[1])))


        else:
            self.lasagna.statusBar.showMessage("Unable to find " + str(fname))
