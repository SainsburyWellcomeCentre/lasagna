
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

import numpy as np

from lasagna.io_libs.sparse_point_io import read_pts_file, read_masiv_roi, read_lasagna_pts
from lasagna.plugins.io.io_plugin_base import IoBasePlugin


class loaderClass(IoBasePlugin):
    def __init__(self, lasagna_serving):
        self.objectName = 'sparse_point_reader'
        self.kind = 'sparsepoints'
        self.icon_name = 'points'
        self.actionObjectName = 'sparsePointRead'
        super(loaderClass, self).__init__(lasagna_serving)

    # Slots follow
    def showLoadDialog(self, fname=None):
        """
        This slot brings up the load dialog and retrieves the file name.
        If a filename is provided then this is loaded and no dialog is brought up.
        If the file name is valid, it loads the base stack using the load method.

        """
        
        if not fname:
            fname = self.lasagna.showFileLoadDialog(fileFilter="Text Files (*.txt *.csv *.pts *.yml)")

        if not fname:
            return

        if os.path.isfile(fname):
            if fname.endswith('.pts'):
                data, roi_type = read_pts_file(fname)
                if roi_type == 'point':
                    print('!!! WARNING points are set in real world coordinates. I assume a pixel size of 1')
            elif fname.endswith('.yml'):
                data = read_masiv_roi(fname)
                # re-order in lasagna order Z X Y
                data = [[d[2], d[0], d[1], d[3]] for d in data]
            else:
                data = read_lasagna_pts(fname)
            # A point series should be a list of lists where each list has a length of 3,
            # corresponding to the position of each point in 3D space. However, point
            # series could also have a length of 4. If this is the case, the fourth 
            # value is the index of the series. This allows a single file to hold multiple
            # different point series. We handle these two cases differently. First we deal
            # with the the standard case:
            if len(data[0]) == 3:
                # Create an ingredient with the same name as the file name 

                objName = fname.split(os.path.sep)[-1]
                self.lasagna.addIngredient(object_name=objName,
                                           kind=self.kind,
                                           data=np.asarray(data),
                                           fname=fname
                                           )
                # Add this ingredient to all three plots
                self.lasagna.returnIngredientByName(obj_name).addToPlots()
                # Update the plots
                self.lasagna.initialiseAxes()

            elif len(data[0]) == 4:
                # What are the unique data series values?
                d_series = [x[3] for x in data]
                d_series = list(set(d_series))
                
                # Loop through these unique series and add as separate sparse point objects

                for idx in d_series:
                    tmp = []
                    for row in data:
                        if row[3] == idx:
                            tmp.append(row[:3])

                    print("Adding point series %d with %d points" % (idx, len(tmp)))

                    # Create an ingredient with the same name as the file name 
                    obj_name = "%s #%d" % (fname.split(os.path.sep)[-1], idx)

                    self.lasagna.addIngredient(object_name=objName,
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
            self.lasagna.statusBar.showMessage("Unable to find {}".format(fname))
