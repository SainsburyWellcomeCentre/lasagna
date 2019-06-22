"""
Read line data from a text file. This reader is very similar to sparse pointer reader. 
The data format is:

lineseries_id,z_position,x_position,y_position\n
lineseries_id,z_position,x_position,y_position\n
...

No header. 

The loader creates a list of lists, where all points within each list are linked. 
All points bearing the same lineseries_id are grouped into the same list and rendered
as a single line.

See also:
lines.py ingredient 
"""

import os
from lasagna.plugins.lasagna_plugin import LasagnaPlugin
import numpy as np
from PyQt5 import QtGui
from lasagna.plugins.io.sparse_point_reader_plugin import (
    read_pts_file,
    read_masiv_roi,
    read_lasagna_pts,
)


class loaderClass(LasagnaPlugin):
    def __init__(self, lasagna):
        super(loaderClass, self).__init__(lasagna)

        self.lasagna = lasagna
        self.objectName = "lines_reader"
        self.kind = "lines"

        # Construct the QActions and other stuff required to integrate the load dialog into the menu
        self.loadAction = QtGui.QAction(self.lasagna)  # Instantiate the menu action

        # Add an icon to the action
        iconLoadOverlay = QtGui.QIcon()
        iconLoadOverlay.addPixmap(
            QtGui.QPixmap(":/actions/icons/lines_64.png"),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off,
        )
        self.loadAction.setIcon(iconLoadOverlay)

        # Insert the action into the menu
        self.loadAction.setObjectName("linesRead")
        self.lasagna.menuLoad_ingredient.addAction(self.loadAction)
        self.loadAction.setText("Lines read")

        self.loadAction.triggered.connect(
            self.showLoadDialog
        )  # Link the action to the slot

    # Slots follow
    def showLoadDialog(self, fname=None):
        """
        This slot brings up the load dialog and retrieves the file name.
        If a filename is provided then this is loaded and no dialog is brought up.
        If the file name is valid, it loads the image stack using the load method.
        """
        if fname is None or not fname:
            fnames = self.lasagna.showFileLoadDialog(
                fileFilter="Text Files (*.txt *.csv *.pts *.yml)", multifile=True
            )
            if fnames is None or not fnames:
                return
            for fname in fnames:
                self.showLoadDialog(fname)

        if os.path.isfile(fname):
            if fname.endswith(".pts"):
                data, roi_type = read_pts_file(fname)
                if roi_type == "point":
                    print(
                        "!!! WARNING points are set in real world coordinates. I assume a pixel size of 1"
                    )
            elif fname.endswith(".yml"):
                data = read_masiv_roi(fname)
                # re-order in lasagna order Z X Y
                data = [[d[2], d[0], d[1], d[3]] for d in data]
            else:
                data = read_lasagna_pts(fname)

            if len(data[0]) == 3:
                obj_name = fname.split(os.path.sep)[-1]
                self.lasagna.addIngredient(
                    object_name=obj_name,
                    kind=self.kind,
                    data=np.asarray(data),
                    fname=fname,
                )

                self.lasagna.returnIngredientByName(
                    obj_name
                ).addToPlots()  # Add item to all three 2D plots
                self.lasagna.initialiseAxes()

            elif len(data[0]) == 4:
                # What are the unique data series values?
                d_series = [x[3] for x in data]
                d_series = list(set(d_series))

                # Loop through these unique series and add as separate sparse point objects

                for this_index in d_series:
                    tmp = []
                    for this_row in data:
                        if this_row[3] == this_index:
                            tmp.append(this_row[:3])

                    print(
                        "Adding point series %d with %d points" % (this_index, len(tmp))
                    )

                    # Create an ingredient with the same name as the file name
                    obj_name = "%s #%d" % (fname.split(os.path.sep)[-1], this_index)

                    self.lasagna.addIngredient(
                        object_name=obj_name,
                        kind=self.kind,
                        data=np.asarray(tmp),
                        fname=fname,
                    )

                    # Add this ingredient to all three plots
                    self.lasagna.returnIngredientByName(obj_name).addToPlots()

                    # Update the plots
                    self.lasagna.initialiseAxes()
            else:
                print(
                    (
                        "Line series has %d columns. Only 3 or 4 columns are supported"
                        % len(data)
                    )
                )

        else:
            self.lasagna.statusBar.showMessage("Unable to find " + str(fname))
