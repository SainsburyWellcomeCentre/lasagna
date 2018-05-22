"""
Loads data from imagej/fiji ROIs or ROIs sets (zip files)

Requires ijroi from: https://github.com/tdsmith/ijroi/blob/master/ijroi/ijroi.py
`pip install ijroi` to get it.


"""
import os
try:
    import ijroi
except ImportError:
    print('fiji_roi_reader_plugin requires the ijroi module from:\n'
          '  https://github.com/tdsmith/ijroi/blob/master/ijroi/ijroi.py.'
          '  Use `pip install ijroi` to get it.')
    raise

import numpy as np
from PyQt5 import QtGui

from lasagna.plugins import lasagna_plugin


class loaderClass(lasagna_plugin):
    def __init__(self, lasagna):
        super(loaderClass, self).__init__(lasagna)

        self.lasagna = lasagna
        self.objectName = 'fiji_roi_reader'
        self.kind = 'sparsepoints'
        # Construct the QActions and other stuff required to integrate the load dialog into the menu
        self.loadAction = QtGui.QAction(self.lasagna)  # Instantiate the menu action

        # Add an icon to the action
        icon_load_overlay = QtGui.QIcon()
        icon_load_overlay.addPixmap(QtGui.QPixmap(":/actions/icons/points.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.loadAction.setIcon(icon_load_overlay)

        # Insert the action into the menu
        self.loadAction.setObjectName("fijiPointRead")
        self.lasagna.menuLoad_ingredient.addAction(self.loadAction)
        self.loadAction.setText("Fiji roi read")

        self.loadAction.triggered.connect(self.showLoadDialog)  # Link the action to the slot

    # Slots follow
    def showLoadDialog(self, fname=None):
        """
        This slot brings up the load dialog and retrieves the file name.
        If a filename is provided then this is loaded and no dialog is brought up.
        If the file name is valid, it loads the base stack using the load method.

        """

        if not fname:
            fname = self.lasagna.showFileLoadDialog(fileFilter="ImageJ ROIs (*.roi *.zip)")

        if not fname:
            return

        if os.path.isfile(fname):
            if fname.endswith('.zip'):
                rois = ijroi.read_roi_zip(fname)
            else:
                rois = []

            # a list of strings with each string being one line from the file
            as_list = contents.split('\n')
            data = []
            for i in range(len(as_list)):
                if len(as_list[i]) == 0:
                    continue
                data.append([float(x) for x in as_list[i].split(',')])

            # A point series should be a list of lists where each list has a length of 3,
            # corresponding to the position of each point in 3D space. However, point
            # series could also have a length of 4. If this is the case, the fourth
            # value is the index of the series. This allows a single file to hold multiple
            # different point series. We handle these two cases differently. First we deal
            # with the the standard case:
            if len(data[1]) == 3:
                # Create an ingredient with the same name as the file name
                obj_name = fname.split(os.path.sep)[-1]
                self.lasagna.addIngredient(objectName=obj_name,
                                           kind=self.kind,
                                           data=np.asarray(data),
                                           fname=fname
                                           )

                # Add this ingredient to all three plots
                self.lasagna.returnIngredientByName(obj_name).addToPlots()

                # Update the plots
                self.lasagna.initialiseAxes()
            elif len(data[1]) == 4:
                # What are the unique data series values?
                d_series = [x[3] for x in data]
                d_series = list(set(d_series))

                # Loop through these unique series and add as separate sparse point objects

                for idx in d_series:
                    tmp = []
                    for thisRow in data:
                        if thisRow[3] == idx:
                            tmp.append(thisRow[:3])

                    print("Adding point series %d with %d points" % (idx, len(tmp)))

                    # Create an ingredient with the same name as the file name
                    obj_name = "%s #%d" % (fname.split(os.path.sep)[-1], idx)

                    self.lasagna.addIngredient(objectName=obj_name,
                                               kind=self.kind,
                                               data=np.asarray(tmp),
                                               fname=fname
                                               )

                    # Add this ingredient to all three plots
                    self.lasagna.returnIngredientByName(obj_name).addToPlots()

                    # Update the plots
                    self.lasagna.initialiseAxes()
            else:
                print(("Point series has %d columns. Only 3 or 4 columns are supported" % len(data[1])))
        else:
            self.lasagna.statusBar.showMessage("Unable to find " + str(fname))
