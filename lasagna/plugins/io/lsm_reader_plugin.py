
"""
Load an LSM stack into Lasagna
"""
import os

import tifffile
from PyQt5 import QtGui

from lasagna import lasagna_helperFunctions as lasHelp
from lasagna.plugins.lasagna_plugin import lasagna_plugin


class loaderClass(lasagna_plugin):
    def __init__(self, lasagna):
        super(loaderClass, self).__init__(lasagna)

        self.lasagna = lasagna
        self.objectName = 'LSM_reader'
        self.kind = 'imagestack'
        # Construct the QActions and other stuff required to integrate the load dialog into the menu
        self.loadAction = QtGui.QAction(self.lasagna)  # Instantiate the menu action

        # Add an icon to the action
        icon_load_overlay = QtGui.QIcon()
        icon_load_overlay.addPixmap(QtGui.QPixmap(":/actions/icons/overlay.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.loadAction.setIcon(icon_load_overlay)

        # Insert the action into the menu
        self.loadAction.setObjectName("LSMread")
        self.lasagna.menuLoad_ingredient.addAction(self.loadAction)
        self.loadAction.setText("Load LSM stack")

        self.loadAction.triggered.connect(self.showLoadDialog)  # Link the action to the slot


    # Slots follow
    def showLoadDialog(self):
        """
        This slot brings up the load dialog and retrieves the file name.
        If the file name is valid, it loads the base stack using the load method.
        """
        
        fname = self.lasagna.showFileLoadDialog(fileFilter="LSM (*.lsm)")
        if fname is None:
            return

        color_order = lasHelp.readPreference('colorOrder')
        if os.path.isfile(fname): 
            im = tifffile.imread(str(fname))
            print("Found LSM stack with dimensions:")
            print(im.shape)
            for i in range(im.shape[2]):
                stack = im[0, :, i, :, :]

                obj_name = "layer_%d" % (i+1)
                self.lasagna.addIngredient(objectName=obj_name,
                                           kind='imagestack',
                                           data=stack,
                                           fname=fname
                                           )
                self.lasagna.returnIngredientByName(obj_name).addToPlots()  # Add item to all three 2D plots

                print("Adding '{}' layer".format(color_order[i]))
                self.lasagna.returnIngredientByName(obj_name).lut = color_order[i]
            self.lasagna.initialiseAxes()
        else:
            self.lasagna.statusBar.showMessage("Unable to find {}".format(fname))
