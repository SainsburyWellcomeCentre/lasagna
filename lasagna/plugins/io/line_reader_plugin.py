
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

import numpy as np
from PyQt5 import QtGui

from lasagna.plugins.lasagna_plugin import LasagnaPlugin


class loaderClass(LasagnaPlugin):
    def __init__(self, lasagna_serving):
        super(loaderClass, self).__init__(lasagna_serving)

        self.lasagna = lasagna_serving
        self.objectName = 'lines_reader'
        self.kind = 'lines'

        # Construct the QActions and other stuff required to integrate the load dialog into the menu
        self.loadAction = QtGui.QAction(self.lasagna)  # Instantiate the menu action

        # Add an icon to the action
        icon_load_overlay = QtGui.QIcon()
        icon_load_overlay.addPixmap(QtGui.QPixmap(":/actions/icons/lines_64.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.loadAction.setIcon(icon_load_overlay)

        # Insert the action into the menu
        self.loadAction.setObjectName("linesRead")
        self.lasagna.menuLoad_ingredient.addAction(self.loadAction)
        self.loadAction.setText("Lines read")

        self.loadAction.triggered.connect(self.showLoadDialog)  # Link the action to the slot

    # Slots follow
    def showLoadDialog(self, fname=None):
        """
        This slot brings up the load dialog and retrieves the file name.
        If a filename is provided then this is loaded and no dialog is brought up.
        If the file name is valid, it loads the base stack using the load method.
        """
        if not fname:
            fname = self.lasagna.showFileLoadDialog(fileFilter="Text Files (*.txt *.csv)")
    
        if not fname:
            return

        if os.path.isfile(fname): 
            with open(str(fname), 'r') as fid:
                contents = fid.read()

            # a list of strings with each string being one line from the file
            # add nans between lineseries
            as_list = contents.split('\n')

            data = []
            last_line_series = None
            n = 0
            expected_cols = 4
            for i in range(len(as_list)):
                if not as_list[i]:
                    continue

                this_line_as_floats = [float(x) for x in as_list[i].split(',')]
                if len(this_line_as_floats) != expected_cols:
                    # Check that all rows have a length of 4, since this is what a line series needs
                    print("Lines data file {} appears corrupt".format(fname))
                    return                     

                if last_line_series is None:
                    last_line_series = this_line_as_floats[0]

                if last_line_series != this_line_as_floats[0]:
                    n += 1
                    data.append([np.nan, np.nan, np.nan])

                last_line_series = this_line_as_floats[0]
                data.append(this_line_as_floats[1:])

            obj_name = fname.split(os.path.sep)[-1]
            self.lasagna.addIngredient(objectName=obj_name,
                                       kind=self.kind,
                                       data=np.asarray(data),
                                       fname=fname,
                                       )
            self.lasagna.returnIngredientByName(obj_name).addToPlots()  # Add item to all three 2D plots
            self.lasagna.initialiseAxes()
        else:
            self.lasagna.statusBar.showMessage("Unable to find {}".format(fname))
