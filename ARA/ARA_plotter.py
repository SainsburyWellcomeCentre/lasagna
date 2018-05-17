
"""
This class handles the overlay of highlights and the brain area name in the status bar. 
This enables more than one plugin to use these features.
"""


import lasagna_helperFunctions as lasHelp 
import numpy as np
import pyqtgraph as pg
import os.path





#For handling the labels files
import ara_json, tree

#For contour drawing
from skimage import measure

class ARA_plotter(object): #must inherit lasagna_plugin first
    def __init__(self,lasagna):
        super(ARA_plotter,self).__init__(lasagna)
       
        self.lasagna = lasagna
        self.contourName = 'aracontour' #The ingredient name for the ARA contour



    #--------------------------------------
    #File handling and housekeeping methods
    def loadLabels(self,fname):
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
            colSep = self.guessFileSep(fname)
            return tree.importData(fname,colSep=colSep, headerLine=True)

        if fname.lower().endswith('.json'):
            (flattened,colNames) = ara_json.importData(fname)
            return tree.importData(flattened.split('\n'), colSep='|', headerLine=colNames)


    def guessFileSep(self,fname):
        """
        Guess the file separator in file fname. [MAY BE ORPHANED]
        """
        with open(fname,'r') as fid:
            contents=fid.read()
    
        nLines = contents.count('\n')
        possibleSeparators = ['|','\t',','] #don't include space because for these data that would be crazy
        for thisSep in possibleSeparators:
            if contents.count(thisSep)>=nLines:
                return thisSep

        #Just return comma if nothing was found. At least we tried!
        return ','


    def defaultPrefs(self):
        """
        Return default preferences in the YAML file in this directory
        """
        return {
            'ara_paths' : [] ,
            'loadFirstAtlasOnStartup' : True,
            'enableNameInStatusBar' : True ,
            'enableOverlay' : True ,
            }



    #--------------------------------------
    # Drawing-related methods
    def addAreaContour(self):
        """
        Add the line ingredient for ARA contour 
        """
        self.lasagna.addIngredient(object_name=self.contourName,
                                   kind='lines',
                                   data=[])
        self.lasagna.returnIngredientByName(self.contourName).addToPlots() #Add item to all three 2D plots


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

        if len(imageStack.shape)==0:
            return -1

        imShape = imageStack.shape
        pos = self.lasagna.mousePositionInStack
        
        verbose=False
        if verbose:
            print("Mouse is in %d,%d,%d and image size is %d,%d,%d" % (pos[0],pos[1],pos[2],imShape[0],imShape[1],imShape[2]))

        #Detect if the mouse is outside of the atlas
        value=0
        for ii in range(len(imShape)):
            if pos[ii]<0 or pos[ii]>=imShape[ii]:
                if verbose:
                    print("NOT IN RANGE: pos: %d shape %d" % (pos[ii], imShape[ii]))
                thisArea='outside image area'
                value=-1
                break

        #If value is still zero we're inside the atlas image area
        if value==0:
            value = imageStack[pos[0],pos[1],pos[2]]
            if value==0:
                thisArea='outside brain'
            elif value in self.data['labels'].nodes :
                thisArea=self.data['labels'][value].data['name']
            else:
                thisArea='UNKNOWN'

        if displayAreaName:
            self.lasagna.statusBarText = self.lasagna.statusBarText + ", area: " + thisArea

        return value


    def getContoursFromAxis(self,imageStack,axisNumber=-1,value=-1):
        """
        Return a contours array from the axis indexed by integer axisNumber
        i.e. one of the three axes
        """        
        if axisNumber == -1:
            return False

        imageStack = np.swapaxes(imageStack,0,axisNumber)
        thisSlice = self.lasagna.axes2D[axisNumber].currentSlice  #This is the current slice in this axis
        tmpImage = np.array(imageStack[thisSlice]) #So this is the image associated with that slice

        #Make a copy of the image and set values lower than our value to a greater number
        #since the countour finder will draw around everything less than our value
        tmpImage[tmpImage<value] = value+10
        return measure.find_contours(tmpImage, value)


    def drawAreaHighlight(self, imageStack, value, highlightOnlyCurrentAxis=False):
        """
        if highlightOnlyCurrentAxis is True, we draw highlights only on the axis we are mousing over
        """
        if value<=0:
            return

        nans = np.array([np.nan, np.nan, np.nan]).reshape(1,3)
        allContours = nans

        for axNum in range(len(self.lasagna.axes2D)):
            contours = self.getContoursFromAxis(imageStack,axisNumber=axNum,value=value)


            if (highlightOnlyCurrentAxis == True  and  axNum != self.lasagna.inAxis) or len(contours)==0:
                tmpNan =  np.array([np.nan, np.nan, np.nan]).reshape(1,3)
                tmpNan[0][axNum]=self.lasagna.axes2D[axNum].currentSlice #ensure nothing is plotted in this layer
                allContours = np.append(allContours,tmpNan,axis=0)
                continue

            #print "Plotting area %d in plane %d" % (value,self.lasagna.axes2D[axNum].currentSlice)
            for thisContour in contours:
                tmp = np.ones(thisContour.shape[0]*3).reshape(thisContour.shape[0],3)*self.lasagna.axes2D[axNum].currentSlice

                if axNum==0:
                    tmp[:,1:] = thisContour

                elif axNum==1:
                    tmp[:,0] = thisContour[:,0]
                    tmp[:,2] = thisContour[:,1]

                elif axNum==2:
                    tmp[:,1] = thisContour[:,0]
                    tmp[:,0] = thisContour[:,1]

                tmp = np.append(tmp,nans,axis=0) #Terminate each contour with nans so that they are not  linked
                allContours = np.append(allContours,tmp,axis=0)

            if highlightOnlyCurrentAxis:
                self.lastValue = value 
        
            
        #Replace the data in the ingredient so they are plotted
        self.lasagna.returnIngredientByName(self.contourName)._data = allContours
        self.lasagna.initialiseAxes()
            

    def setARAcolors(self):
        #Make up a disjointed colormap
        pos = np.array([0.0, 0.001, 0.25, 0.35, 0.45, 0.65, 0.9])
        color = np.array([[0,0,0,255],[255,0,0,255], [0,2,230,255], [7,255,112,255], [255,240,7,255], [7,153,255,255], [255,7,235,255]], dtype=np.ubyte)
        map = pg.ColorMap(pos, color)
        lut = map.getLookupTable(0.0, 1.0, 256)

        #Assign the colormap to the imagestack object
        self.ARAlayerName = self.lasagna.imageStackLayers_Model.index(0,0).data().toString() #TODO: a bit horrible
        firstLayer = self.lasagna.returnIngredientByName(self.ARAlayerName)
        firstLayer.lut=lut
        #Specify what colors the histogram should be so it doesn't end up megenta and 
        #vomit-yellow, or who knows what, due to the weird color map we use here.
        firstLayer.histPenCustomColor = [180,180,180,255]
        firstLayer.histBrushCustomColor = [150,150,150,150]
