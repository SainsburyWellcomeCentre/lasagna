
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

from lasagna.plugins.io.io_plugin_base import IoBasePlugin
from lasagna.tree import tree_parser


class loaderClass(IoBasePlugin):
    def __init__(self, lasagna_serving):
        self.objectName = 'tree_reader'
        self.kind = 'lines'
        self.icon_name = 'tree_64'
        self.actionObjectName = 'treeRead'
        super(loaderClass, self).__init__(lasagna_serving)

    def dataFromPath(self, tree, path):
        """
        Get the data from the tree given a path.
        """

        z = []
        x = []
        y = []

        for node in path:
            if node == 0:
                continue
            z.append(tree.nodes[node].data['z'])
            x.append(tree.nodes[node].data['x'])
            y.append(tree.nodes[node].data['y'])
        return z, x, y

    # Slots follow
    def showLoadDialog(self, fname=None):
        """
        This slot brings up the load dialog and retrieves the file name.
        NOTE:
        If a filename is provided then this is loaded and no dialog is brought up.
        If the file name is valid, it loads the image stack using the load method.
        """

        verbose = False 

        if not fname:
            fname = self.lasagna.showFileLoadDialog(fileFilter="Text Files (*.txt *.csv)")
    
        if not fname:
            return

        if os.path.isfile(fname):
            with open(str(fname), 'r') as fid:
                # import the tree
                if verbose:
                    print("tree_reader_plugin.showLoadDialog - importing %s" % fname)

                data_tree = tree_parser.parse_file(fname, header_line=['id', 'parent', 'z', 'x', 'y'], verbose=verbose)
                if not data_tree:
                    print("No data loaded from %s" % fname)
                    return

                # We now have an array of unique paths (segments)
                paths = []
                for thisSegment in data_tree.find_segments():
                    paths.append(thisSegment)

                as_list = []  # list of list data (one item per node)
                for i, thisPath in enumerate(paths):
                    data = self.dataFromPath(data_tree, thisPath)
                    for j in range(len(data[0])):
                        tmp = [i, data[0][j], data[1][j], data[2][j]]
                        tmp = [float(x) for x in tmp]
                        as_list.append(tmp)

            # add nans between lineseries
            data = []
            last_line_series = None
            n = 0
            for i in range(len(as_list)):
                if len(as_list[i]) == 0:
                    continue

                line = as_list[i]
                if last_line_series is None:
                    last_line_series = line[0]

                if last_line_series != line[0]:
                    n += 1
                    data.append([np.nan, np.nan, np.nan])

                last_line_series = line[0]
                data.append(line[1:])

            if verbose:
                print("Divided tree into %d segments" % n)

            # print data
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
