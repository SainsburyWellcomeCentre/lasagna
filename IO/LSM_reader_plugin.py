
"""
Load an LSM stack into Lasagna
"""
import os
from lasagna_plugin import lasagna_plugin
import tifffile
from PyQt4 import QtGui
import lasagna_helperFunctions as lasHelp # Module the provides a variety of import functions (e.g. preference file handling)

class loaderClass(lasagna_plugin):
    def __init__(self,lasagna):
        super(loaderClass,self).__init__(lasagna)

        self.lasagna = lasagna
        self.objectName = 'LSM_reader'

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
        If the file name is valid, it loads the base stack using the load method.
        We split things up to make it easier to load the base stack pragmatically,
        such as from a plugin, without going via the load dialog. 
        """

        #TODO: get it to filter by LSM
        
        fname = self.lasagna.showFileLoadDialog()
        if fname == None:
            return

        colorOrder = lasHelp.readPreference('colorOrder')
        if os.path.isfile(fname): 
            im=tifffile.imread(str(fname)) 

            for ii in range(im.shape[2]):
                stack=im[0,:,ii,:,:]

                objName="layer_%d" % (ii+1)
                self.lasagna.addIngredient(objectName=objName, 
                           kind='imagestack', 
                           data=stack, 
                           fname=fname
                           )
                self.lasagna.returnIngredientByName(objName).lut=colorOrder[ii]
                self.lasagna.returnIngredientByName(objName).show() #Add item to all three 2D plots

            self.lasagna.initialiseAxes()

        else:
            self.lasagna.statusBar.showMessage("Unable to find " + str(fname))
