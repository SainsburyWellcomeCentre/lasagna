
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
from lasagna.plugins.lasagna_plugin import LasagnaPlugin
import numpy as np
from PyQt5 import QtGui

from lasagna.tree import importData


class loaderClass(LasagnaPlugin):
    def __init__(self,lasagna):
        super(loaderClass,self).__init__(lasagna)

        self.lasagna = lasagna
        self.objectName = 'tree_reader'
        self.kind = 'lines'

        #Construct the QActions and other stuff required to integrate the load dialog into the menu
        self.loadAction = QtGui.QAction(self.lasagna) #Instantiate the menu action

        #Add an icon to the action
        iconLoadOverlay = QtGui.QIcon()
        iconLoadOverlay.addPixmap(QtGui.QPixmap(":/actions/icons/tree_64.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.loadAction.setIcon(iconLoadOverlay)


        #Insert the action into the menu
        self.loadAction.setObjectName("treeRead")
        self.lasagna.menuLoad_ingredient.addAction(self.loadAction)
        self.loadAction.setText("Tree read")

        self.loadAction.triggered.connect(self.showLoadDialog) #Link the action to the slot


    def dataFromPath(self,tree,path):
        """
        Get the data from the tree given a path.
        """

        z=[]
        x=[]
        y=[]

        for thisNode in path:
            if thisNode==0:
                continue
            z.append(tree.nodes[thisNode].data['z'])
            x.append(tree.nodes[thisNode].data['x'])
            y.append(tree.nodes[thisNode].data['y'])


        return (z,x,y)


    #Slots follow
    def showLoadDialog(self,fname=None):
        """
        This slot brings up the load dialog and retrieves the file name.
        NOTE:
        If a filename is provided then this is loaded and no dialog is brought up.
        If the file name is valid, it loads the base stack using the load method.
        """

        verbose = False 

        if fname is None or not fname:
            fname = self.lasagna.showFileLoadDialog(fileFilter="Text Files (*.txt *.csv)")
    
        if fname is None or not fname:
            return

        if os.path.isfile(fname): 
            with open(str(fname),'r') as fid:

                #import the tree 
                if verbose:
                    print("tree_reader_plugin.showLoadDialog - importing %s" % fname)

                dataTree = importData(fname,headerLine=['id','parent','z','x','y'],verbose=verbose)
                if not dataTree:
                    print("No data loaded from %s" % fname)
                    return

                #We now have an array of unique paths (segments)
                paths=[]
                for thisSegment in dataTree.findSegments():
                    paths.append(thisSegment)


                ii=0
                asList=[] #list of list data (one item per node)
                for thisPath in paths:
                    data = self.dataFromPath(dataTree,thisPath)
                    for jj in range(len(data[0])):
                        tmp = [ii,data[0][jj],data[1][jj],data[2][jj]]
                        tmp = [float(x) for x in tmp] #convert to floats
                        asList.append(tmp)
                    ii += 1



            # add nans between lineseries
            data=[]
            lastLineSeries=None
            n=0
            for ii in range(len(asList)):
                if len(asList[ii])==0:
                    continue

                thisLine = asList[ii]
                if lastLineSeries is None:
                    lastLineSeries=thisLine[0]

                if lastLineSeries != thisLine[0]:
                    n+=1
                    data.append([np.nan, np.nan, np.nan])

                lastLineSeries=thisLine[0]
                data.append(thisLine[1:])


            if verbose:
                print("Divided tree into %d segments" % n)

            #print data         
            objName=fname.split(os.path.sep)[-1]
            self.lasagna.addIngredient(object_name=objName,
                                       kind=self.kind,
                                       data=np.asarray(data),
                                       fname=fname,
                                       )

            self.lasagna.returnIngredientByName(objName).addToPlots() #Add item to all three 2D plots
            self.lasagna.initialiseAxes()


        else:
            self.lasagna.statusBar.showMessage("Unable to find " + str(fname))
