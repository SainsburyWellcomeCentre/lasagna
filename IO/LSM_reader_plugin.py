
"""
Load an LSM stack into Lasagna
"""
import os
from lasagna.plugins.lasagna_plugin import LasagnaPlugin
import tifffile
from PyQt5 import QtGui
import lasagna.utils.preferences as lasPref # Module the provides a variety of import functions (e.g. preference file handling)

class loaderClass(LasagnaPlugin):
    def __init__(self,lasagna):
        super(loaderClass,self).__init__(lasagna)

        self.lasagna = lasagna
        self.objectName = 'LSM_reader'
        self.kind = 'imagestack'
        #Construct the QActions and other stuff required to integrate the load dialog into the menu
        self.loadAction = QtGui.QAction(self.lasagna) #Instantiate the menu action

        #Add an icon to the action
        iconLoadOverlay = QtGui.QIcon()
        iconLoadOverlay.addPixmap(QtGui.QPixmap(":/actions/icons/overlay.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.loadAction.setIcon(iconLoadOverlay)

        #Insert the action into the menu
        self.loadAction.setObjectName("LSMread")
        self.lasagna.menuLoad_ingredient.addAction(self.loadAction)
        self.loadAction.setText("Load LSM stack")

        self.loadAction.triggered.connect(self.showLoadDialog) #Link the action to the slot



 #Slots follow
    def showLoadDialog(self):
        """
        This slot brings up the load dialog and retrieves the file name.
        If the file name is valid, it loads the image stack using the load method.
        """
        
        fname = self.lasagna.showFileLoadDialog(fileFilter="LSM (*.lsm)")
        if fname is None:
            return

        colorOrder = lasPref.readPreference('colorOrder')
        if os.path.isfile(fname): 
            im=tifffile.imread(str(fname)) 
            print("Found LSM stack with dimensions:")
            print(im.shape)
            for ii in range(im.shape[2]):
                stack=im[0,:,ii,:,:]

                objName="layer_%d" % (ii+1)
                self.lasagna.addIngredient(object_name=objName,
                                           kind='imagestack',
                                           data=stack,
                                           fname=fname
                                           )
                self.lasagna.returnIngredientByName(objName).addToPlots() #Add item to all three 2D plots                

                print("Adding '%s' layer" % colorOrder[ii])
                self.lasagna.returnIngredientByName(objName).lut=colorOrder[ii]


            self.lasagna.initialiseAxes()

        else:
            self.lasagna.statusBar.showMessage("Unable to find " + str(fname))
