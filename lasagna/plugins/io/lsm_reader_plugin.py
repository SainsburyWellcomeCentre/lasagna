
"""
Load an LSM stack into Lasagna
"""
import os

import tifffile

from lasagna.plugins.io.io_plugin_base import IoBasePlugin
from lasagna.utils import preferences


class loaderClass(IoBasePlugin):
    def __init__(self, lasagna_serving):
        self.objectName = 'LSM_reader'
        self.kind = 'imagestack'
        self.icon_name = 'overlay'
        self.actionObjectName = 'LSMread'
        super(loaderClass, self).__init__(lasagna_serving)

    # Slots follow
    def showLoadDialog(self):
        """
        This slot brings up the load dialog and retrieves the file name.
        If the file name is valid, it loads the base stack using the load method.
        """
        
        fname = self.lasagna.showFileLoadDialog(fileFilter="LSM (*.lsm)")
        if fname is None:
            return

        color_order = preferences.readPreference('colorOrder')
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
