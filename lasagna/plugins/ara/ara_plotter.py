
"""
This class handles the overlay of highlights and the brain area name in the status bar. 
This enables more than one plugin to use these features.
"""

import numpy as np
import pyqtgraph as pg
# For contour drawing
from skimage import measure

from lasagna import tree
# For handling the labels files
from lasagna.io_libs import ara_json


class ARA_plotter(object):  # must inherit lasagna_plugin first
    def __init__(self, lasagna):
        super(ARA_plotter, self).__init__(lasagna)
       
        self.lasagna = lasagna
        self.contourName = 'aracontour'  # The ingredient name for the ARA contour

    # --------------------------------------
    # File handling and housekeeping methods
    def loadLabels(self, fname):
        """
        Load the labels file, which may be in JSON or CSV format
        
        The csv file should have the following format
        index,parent_index,data1,data1,dataN\n
        The first line should be a header line. Suggested separators: | or ,

        Header must include at least the name of the area. So we can get, e.g. 
        'name': 'Entorhinal area, lateral part, layer 2'

        The JSON should be the raw JSON from the ARA website

        Returns the labels as a tree structure that can be indexed by ID
        """

        if fname.lower().endswith('.csv'):
            col_sep = self.guessFileSep(fname)
            return tree.importData(fname, colSep=col_sep)

        if fname.lower().endswith('.json'):
            flattened, col_names = ara_json.importData(fname)
            table = flattened.split('\n')
            return tree.importData(table, colSep='|', headerLine=col_names)

    def guessFileSep(self, fname):
        """
        Guess the file separator in file fname. [MAY BE ORPHANED]
        """
        with open(fname, 'r') as fid:
            contents = fid.read()
    
        n_lines = contents.count('\n')
        possible_separators = ('|', '\t', ',')  # don't include space because for these data that would be crazy
        for separator in possible_separators:
            if contents.count(separator) >= n_lines:
                return separator

        # Just return comma if nothing was found. At least we tried!
        return ','

    def defaultPrefs(self):
        """
        Return default preferences in the YAML file in this directory
        """
        return {
            'ara_paths': [],
            'loadFirstAtlasOnStartup': True,
            'enableNameInStatusBar': True,
            'enableOverlay': True,
            }

    # --------------------------------------
    # Drawing-related methods
    def addAreaContour(self):
        """
        Add the line ingredient for ARA contour 
        """
        self.lasagna.addIngredient(objectName=self.contourName,
                                   kind='lines',
                                   data=[])
        self.lasagna.returnIngredientByName(self.contourName).addToPlots()  # Add item to all three 2D plots

    def removeAreaContour(self):
        """
        Remove area contour from the plot
        """
        self.lasagna.removeIngredientByName(self.contourName)

    def writeAreaNameInStatusBar(self, imageStack, displayAreaName=True):
        """
        imageStack - the 3-D atlas stack
        displayAreaName - display area name in status bar if this True
        Write brain area name in the status bar (optional) return value of atlas pixel under mouse.
        Atlas need not be visible.
        """

        if not imageStack.shape:
            return -1

        im_shape = imageStack.shape
        pos = self.lasagna.mousePositionInStack
        
        verbose = False
        if verbose:
            print("Mouse is in %d,%d,%d and image size is %d,%d,%d" %
                  (pos[0], pos[1], pos[2], im_shape[0], im_shape[1], im_shape[2]))

        # Detect if the mouse is outside of the atlas
        value = 0
        for i in range(len(im_shape)):
            if pos[i] < 0 or pos[i] >= im_shape[i]:
                if verbose:
                    print("NOT IN RANGE: pos: %d shape %d" % (pos[i], im_shape[i]))
                area = 'outside image area'
                value = -1
                break

        # If value is still zero we're inside the atlas image area
        if value == 0:
            value = imageStack[pos[0], pos[1], pos[2]]
            if value == 0:
                area = 'outside brain'
            elif value in self.data['labels'].nodes:
                area = self.data['labels'][value].data['name']
            else:
                area = 'UNKNOWN'

        if displayAreaName:
            self.lasagna.statusBarText = self.lasagna.statusBarText + ", area: " + area

        return value

    def getContoursFromAxis(self, imageStack, axisNumber=-1, value=-1):
        """
        Return a contours array from the axis indexed by integer axisNumber
        i.e. one of the three axes
        """        
        if axisNumber == -1:
            return False

        imageStack = np.swapaxes(imageStack, 0, axisNumber)
        this_slice = self.lasagna.axes2D[axisNumber].currentSlice  # This is the current slice in this axis
        tmp_image = np.array(imageStack[this_slice])  # So this is the image associated with that slice

        # Make a copy of the image and set values lower than our value to a greater number
        # since the countour finder will draw around everything less than our value
        tmp_image[tmp_image < value] = value+10
        return measure.find_contours(tmp_image, value)

    def drawAreaHighlight(self, imageStack, value, highlightOnlyCurrentAxis=False):
        """
        if highlightOnlyCurrentAxis is True, we draw highlights only on the axis we are mousing over
        """
        if value <= 0:
            return

        nans = np.array([np.nan, np.nan, np.nan]).reshape(1, 3)
        all_contours = nans

        for ax_num in range(len(self.lasagna.axes2D)):
            contours = self.getContoursFromAxis(imageStack, axisNumber=ax_num, value=value)
            if (highlightOnlyCurrentAxis and ax_num != self.lasagna.inAxis) or not contours:
                tmp_nan = np.array([np.nan, np.nan, np.nan]).reshape(1, 3)
                tmp_nan[0][ax_num] = self.lasagna.axes2D[ax_num].currentSlice  # ensure nothing is plotted in this layer
                all_contours = np.append(all_contours, tmp_nan, axis=0)
                continue

            # print "Plotting area %d in plane %d" % (value,self.lasagna.axes2D[ax_num].currentSlice)
            for contour in contours:
                tmp = np.ones(contour.shape[0]*3).reshape(contour.shape[0], 3)*self.lasagna.axes2D[ax_num].currentSlice

                if ax_num == 0:
                    tmp[:, 1:] = contour
                elif ax_num == 1:
                    tmp[:, 0] = contour[:, 0]
                    tmp[:, 2] = contour[:, 1]
                elif ax_num == 2:
                    tmp[:, 1] = contour[:, 0]
                    tmp[:, 0] = contour[:, 1]

                tmp = np.append(tmp, nans, axis=0)  # Terminate each contour with nans so that they are not  linked
                all_contours = np.append(all_contours, tmp, axis=0)

            if highlightOnlyCurrentAxis:
                self.lastValue = value
            
        # Replace the data in the ingredient so they are plotted
        self.lasagna.returnIngredientByName(self.contourName)._data = all_contours
        self.lasagna.initialiseAxes()

    def setARAcolors(self):
        # Make up a disjointed colormap
        pos = np.array([0.0, 0.001, 0.25, 0.35, 0.45, 0.65, 0.9])
        color = np.array([[0, 0, 0, 255],
                          [255, 0, 0, 255],
                          [0, 2, 230, 255],
                          [7, 255, 112, 255],
                          [255, 240, 7, 255],
                          [7, 153, 255, 255],
                          [255, 7, 235, 255]
                          ], dtype=np.ubyte)
        color_map = pg.ColorMap(pos, color)
        lut = color_map.getLookupTable(0.0, 1.0, 256)

        # Assign the colormap to the imagestack object
        self.ARAlayerName = self.lasagna.imageStackLayers_Model.index(0, 0).data().toString()  # FIXME: a bit horrible
        first_layer = self.lasagna.returnIngredientByName(self.ARAlayerName)
        first_layer.lut = lut
        # Specify what colors the histogram should be so it doesn't end up megenta and
        # vomit-yellow, or who knows what, due to the weird color map we use here.
        first_layer.histPenCustomColor = [180, 180, 180, 255]
        first_layer.histBrushCustomColor = [150, 150, 150, 150]
